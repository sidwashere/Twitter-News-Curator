#Requires -Version 5.1
<#
.SYNOPSIS
    Automatically updates the project context file with current project structure and metadata.

.DESCRIPTION
    Scans the Twitter News Curator project directory, analyzes files, dependencies, and structure,
    then generates/updates comprehensive context documentation for AI assistants and developers.

.PARAMETER Force
    Force update even if no changes detected

.PARAMETER Verbose
    Show detailed progress information

.EXAMPLE
    .\update-context.ps1
    .\update-context.ps1 -Force -Verbose
#>

param(
    [switch]$Force,
    [switch]$VerboseOutput
)

# Set up paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ConfigPath = Join-Path $ProjectRoot ".context-config.json"
$LogPath = Join-Path $ScriptDir "update-context.log"

# Load configuration
if (Test-Path $ConfigPath) {
    $Config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
} else {
    Write-Error "Configuration file not found: $ConfigPath"
    exit 1
}

$ContextFilePath = Join-Path $ProjectRoot $Config.contextFile

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Add-Content -Path $LogPath -Value $LogMessage
    if ($VerboseOutput) {
        Write-Host $LogMessage
    }
}

Write-Log "Starting context update process"

# Function to check if path should be excluded
function Test-ShouldExclude {
    param([string]$Path)
    
    foreach ($pattern in $Config.excludePatterns) {
        if ($Path -like "*$pattern*") {
            return $true
        }
    }
    return $false
}

# Function to get file extension
function Test-ShouldInclude {
    param([string]$FilePath)
    
    $extension = [System.IO.Path]::GetExtension($FilePath)
    return $Config.includeFileTypes -contains $extension
}

# Scan project structure
Write-Log "Scanning project structure..."
$AllFiles = Get-ChildItem -Path $ProjectRoot -Recurse -File -ErrorAction SilentlyContinue | 
    Where-Object { -not (Test-ShouldExclude $_.FullName) }

$IncludedFiles = $AllFiles | Where-Object { Test-ShouldInclude $_.FullName }

# Calculate statistics
$TotalFiles = $AllFiles.Count
$TotalSize = ($AllFiles | Measure-Object -Property Length -Sum).Sum
$CodeFiles = $IncludedFiles.Count

# Count lines of code
$TotalLines = 0
foreach ($file in $IncludedFiles) {
    try {
        $lines = (Get-Content $file.FullName -ErrorAction SilentlyContinue).Count
        $TotalLines += $lines
    } catch {
        # Skip files that can't be read
    }
}

Write-Log "Found $TotalFiles files, $CodeFiles code files, $TotalLines lines of code"

# Build file structure tree
function Get-DirectoryTree {
    param([string]$Path, [int]$Depth = 0, [int]$MaxDepth = 3)
    
    if ($Depth -gt $MaxDepth) { return @() }
    
    $items = Get-ChildItem -Path $Path -ErrorAction SilentlyContinue | 
        Where-Object { -not (Test-ShouldExclude $_.FullName) }
    
    $tree = @()
    $indent = "  " * $Depth
    
    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            $tree += "$indent├── 📁 $($item.Name)/"
            $tree += Get-DirectoryTree -Path $item.FullName -Depth ($Depth + 1) -MaxDepth $MaxDepth
        } else {
            $size = if ($item.Length -lt 1KB) { "$($item.Length)B" } 
                    elseif ($item.Length -lt 1MB) { "{0:N1}KB" -f ($item.Length / 1KB) }
                    else { "{0:N1}MB" -f ($item.Length / 1MB) }
            $tree += "$indent├── 📄 $($item.Name) ($size)"
        }
    }
    
    return $tree
}

$FileTree = Get-DirectoryTree -Path $ProjectRoot

# Detect dependencies
$Dependencies = @{
    Python = @()
    Node = @()
    Other = @()
}

# Check for requirements.txt
$RequirementsPath = Join-Path $ProjectRoot "requirements.txt"
if (Test-Path $RequirementsPath) {
    $Dependencies.Python = Get-Content $RequirementsPath | Where-Object { $_ -match '\S' -and $_ -notmatch '^#' }
    Write-Log "Found Python dependencies: $($Dependencies.Python.Count)"
}

# Check for package.json
$PackageJsonPath = Join-Path $ProjectRoot "package.json"
if (Test-Path $PackageJsonPath) {
    $PackageJson = Get-Content $PackageJsonPath -Raw | ConvertFrom-Json
    if ($PackageJson.dependencies) {
        $Dependencies.Node = $PackageJson.dependencies.PSObject.Properties | ForEach-Object { "$($_.Name)@$($_.Value)" }
        Write-Log "Found Node dependencies: $($Dependencies.Node.Count)"
    }
}

# Read existing context to preserve manual sections
$ExistingContext = if (Test-Path $ContextFilePath) {
    Get-Content $ContextFilePath -Raw
} else {
    ""
}

# Extract manual sections (everything before AUTO-GENERATED marker or all content if no marker)
$ManualSections = ""
if ($ExistingContext -match '(?s)(.*?)(?=---\s*AUTO-GENERATED|\Z)') {
    $ManualSections = $Matches[1].Trim()
}

# Build new context
$NewContext = @"
$ManualSections

---

## AUTO-GENERATED CONTENT
> **Last Updated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
> 
> This section is automatically generated by the context updater.
> Do not manually edit below this line - your changes will be overwritten.

## 📊 Project Statistics

- **Total Files:** $TotalFiles
- **Code Files:** $CodeFiles
- **Total Lines of Code:** $TotalLines
- **Total Size:** $([Math]::Round($TotalSize / 1MB, 2)) MB
- **Last Updated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## 📁 Project Structure

``````
$($FileTree -join "`n")
``````

## 📦 Dependencies

"@

if ($Dependencies.Python.Count -gt 0) {
    $NewContext += "`n### Python Dependencies`n`n"
    foreach ($dep in $Dependencies.Python) {
        $NewContext += "- ``$dep```n"
    }
}

if ($Dependencies.Node.Count -gt 0) {
    $NewContext += "`n### Node.js Dependencies`n`n"
    foreach ($dep in $Dependencies.Node) {
        $NewContext += "- ``$dep```n"
    }
}

# Detect project type and frameworks
$NewContext += "`n## 🔧 Detected Technologies`n`n"

$Technologies = @()

if (Test-Path (Join-Path $ProjectRoot "requirements.txt")) {
    $Technologies += "Python"
}
if (Test-Path (Join-Path $ProjectRoot "package.json")) {
    $Technologies += "Node.js/JavaScript"
}
if (Get-ChildItem -Path $ProjectRoot -Filter "*.py" -Recurse -ErrorAction SilentlyContinue) {
    $pyFiles = Get-ChildItem -Path $ProjectRoot -Filter "*.py" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 5
    $content = $pyFiles | ForEach-Object { Get-Content $_.FullName -ErrorAction SilentlyContinue } | Out-String
    
    if ($content -match 'import tweepy|from tweepy') { $Technologies += "Tweepy (Twitter API)" }
    if ($content -match 'import feedparser|from feedparser') { $Technologies += "Feedparser (RSS)" }
    if ($content -match 'import google\.generativeai|from google\.generativeai') { $Technologies += "Google Gemini AI" }
    if ($content -match 'import openai|from openai') { $Technologies += "OpenAI API" }
    if ($content -match 'import fastapi|from fastapi') { $Technologies += "FastAPI" }
    if ($content -match 'import flask|from flask') { $Technologies += "Flask" }
}

foreach ($tech in $Technologies) {
    $NewContext += "- $tech`n"
}

# Recent changes (if tracking is enabled)
if ($Config.trackChanges) {
    $RecentFiles = Get-ChildItem -Path $ProjectRoot -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { -not (Test-ShouldExclude $_.FullName) } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 10
    
    $NewContext += "`n## 📝 Recent Changes`n`n"
    foreach ($file in $RecentFiles) {
        $relativePath = $file.FullName.Replace($ProjectRoot, "").TrimStart('\')
        $timeAgo = (New-TimeSpan -Start $file.LastWriteTime -End (Get-Date)).TotalHours
        
        if ($timeAgo -lt 1) {
            $timeStr = "< 1 hour ago"
        } elseif ($timeAgo -lt 24) {
            $timeStr = "$([Math]::Floor($timeAgo)) hours ago"
        } else {
            $timeStr = "$([Math]::Floor($timeAgo / 24)) days ago"
        }
        
        $NewContext += "- ``$relativePath`` - *$timeStr*`n"
    }
}

# Write updated context
Set-Content -Path $ContextFilePath -Value $NewContext -Encoding UTF8
Write-Log "Context file updated successfully"

Write-Host "`n✅ Context update complete!" -ForegroundColor Green
Write-Host "📄 Updated: $ContextFilePath" -ForegroundColor Cyan
Write-Host "📊 Stats: $TotalFiles files, $CodeFiles code files, $TotalLines lines" -ForegroundColor Cyan
Write-Host "📋 Log: $LogPath`n" -ForegroundColor Cyan
