#Requires -Version 5.1 -RunAsAdministrator
<#
.SYNOPSIS
    Sets up Windows Task Scheduler to run context updates automatically.

.DESCRIPTION
    Creates a scheduled task that runs the update-context.ps1 script daily
    to keep project documentation up-to-date automatically.

.PARAMETER TaskName
    Name for the scheduled task (default: "TwitterCurator-ContextUpdate")

.PARAMETER Schedule
    When to run: Daily, OnStartup, or OnChange (default: Daily)

.PARAMETER Time
    Time of day to run if Daily (default: "09:00")

.EXAMPLE
    .\setup-scheduler.ps1
    .\setup-scheduler.ps1 -Schedule Daily -Time "14:30"
#>

param(
    [string]$TaskName = "TwitterCurator-ContextUpdate",
    [ValidateSet("Daily", "OnStartup", "OnChange")]
    [string]$Schedule = "Daily",
    [string]$Time = "09:00"
)

# Verify running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator. Right-click and select 'Run as Administrator'."
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$UpdateScriptPath = Join-Path $ScriptDir "update-context.ps1"

if (-not (Test-Path $UpdateScriptPath)) {
    Write-Error "Update script not found: $UpdateScriptPath"
    exit 1
}

Write-Host "Setting up scheduled task: $TaskName" -ForegroundColor Cyan

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create action
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$UpdateScriptPath`"" `
    -WorkingDirectory $ScriptDir

# Create trigger based on schedule
switch ($Schedule) {
    "Daily" {
        $trigger = New-ScheduledTaskTrigger -Daily -At $Time
        Write-Host "Schedule: Daily at $Time" -ForegroundColor Green
    }
    "OnStartup" {
        $trigger = New-ScheduledTaskTrigger -AtStartup
        Write-Host "Schedule: On system startup" -ForegroundColor Green
    }
    "OnChange" {
        # For OnChange, we'll use a file system watcher trigger (advanced)
        Write-Host "OnChange schedule requires manual setup. Creating daily task instead." -ForegroundColor Yellow
        $trigger = New-ScheduledTaskTrigger -Daily -At $Time
    }
}

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -MultipleInstances IgnoreNew

# Create principal (run with current user privileges)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Limited

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Automatically updates the Twitter News Curator context file with current project state" | Out-Null
    
    Write-Host "`n✅ Scheduled task created successfully!" -ForegroundColor Green
    Write-Host "`nTask Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName"
    Write-Host "  Script: $UpdateScriptPath"
    Write-Host "  Schedule: $Schedule $(if ($Schedule -eq 'Daily') { "at $Time" })"
    
    Write-Host "`nTo manage this task:" -ForegroundColor Yellow
    Write-Host "  - Open Task Scheduler (taskschd.msc)"
    Write-Host "  - Navigate to: Task Scheduler Library"
    Write-Host "  - Find: $TaskName"
    
    Write-Host "`nTo run manually:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
    
    Write-Host "`nTo disable:" -ForegroundColor Yellow
    Write-Host "  Disable-ScheduledTask -TaskName '$TaskName'"
    
    Write-Host "`nTo remove:" -ForegroundColor Yellow
    Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false`n"
    
    # Offer to run now
    $runNow = Read-Host "Run the context update now? (Y/N)"
    if ($runNow -eq 'Y' -or $runNow -eq 'y') {
        Write-Host "`nRunning update..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $TaskName
        Start-Sleep -Seconds 2
        & $UpdateScriptPath -VerboseOutput
    }
    
} catch {
    Write-Error "Failed to create scheduled task: $_"
    exit 1
}
