# Run this once (double-click, or right-click > Run with PowerShell) to make
# Today's To-Do launch automatically, hidden, whenever you log in to Windows.
#
# It creates a shortcut in your Startup folder pointing pythonw.exe at
# run_hidden.pyw. To undo this later, just delete the shortcut from:
#   shell:startup

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyw = Join-Path $scriptDir "run_hidden.pyw"

if (-not (Test-Path $pyw)) {
    Write-Host "Could not find run_hidden.pyw next to this script. Aborting." -ForegroundColor Red
    exit 1
}

$pythonwCmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
if (-not $pythonwCmd) {
    Write-Host "pythonw.exe was not found on your PATH." -ForegroundColor Yellow
    Write-Host "It normally lives next to python.exe (e.g. C:\Python312\pythonw.exe)." -ForegroundColor Yellow
    $manualPath = Read-Host "Paste the full path to pythonw.exe (or press Enter to cancel)"
    if ([string]::IsNullOrWhiteSpace($manualPath)) {
        exit 1
    }
    $pythonwPath = $manualPath
} else {
    $pythonwPath = $pythonwCmd.Source
}

$startupDir = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startupDir "Today's To-Do.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $pythonwPath
$Shortcut.Arguments = '"' + $pyw + '"'
$Shortcut.WorkingDirectory = $scriptDir
$Shortcut.WindowStyle = 7   # minimized/hidden style
$Shortcut.Description = "Today's To-Do habit tracker"
$Shortcut.Save()

Write-Host "Done! Shortcut created at:" -ForegroundColor Green
Write-Host "  $shortcutPath"
Write-Host "Today's To-Do will now start automatically (hidden, in the tray) at login."
