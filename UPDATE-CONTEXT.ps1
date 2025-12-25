# Quick Context Update
# Double-click this file to update the context immediately (no prompts)

Set-Location "x:\Projects\Twitter News Curator"
.\scripts\update-context.ps1 -VerboseOutput

Write-Host "`n`nPress any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
