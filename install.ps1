$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SQL Notepad Automated Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "Select installation mode:"
Write-Host "1) Global Install (Installs to ~\.ipython\sql_notepad, adds 'mysql' command globally)"
Write-Host "2) Local Testing (Installs to .\sql_notepad in current directory, no global commands)"

$mode = ""
while ($mode -ne "1" -and $mode -ne "2") {
    $mode = Read-Host "Choice [1/2]"
}

$repoUrl = "https://github.com/USANJAY05/sql_notepad.git"

if ($mode -eq "1") {
    $installDir = Join-Path $env:USERPROFILE ".ipython\sql_notepad"
    $binDir = Join-Path $env:USERPROFILE ".local\bin"
    Write-Host "Mode: Global Install" -ForegroundColor Green
} else {
    $installDir = Join-Path $PWD "sql_notepad"
    Write-Host "Mode: Local Testing" -ForegroundColor Green
}

# Check for git
if (-not (Get-Command "git" -ErrorAction SilentlyContinue)) {
    Write-Error "git is required but not installed."
    exit 1
}

if (Test-Path $installDir) {
    Write-Host "Directory $installDir already exists."
    Write-Host "Updating repository..."
    Set-Location $installDir
    git pull origin main
} else {
    Write-Host "Cloning repository to $installDir..."
    git clone $repoUrl $installDir
    Set-Location $installDir
}

if ($mode -eq "1") {
    Write-Host "Setting up global 'mysql' command..."
    if (-not (Test-Path $binDir)) {
        New-Item -ItemType Directory -Force -Path $binDir | Out-Null
    }
    
    $wrapperScript = Join-Path $binDir "mysql.bat"
    $wrapperContent = @"
@echo off
set "APP_DIR=$installDir"
call "%APP_DIR%\mysql.bat" %*
"@
    Set-Content -Path $wrapperScript -Value $wrapperContent
    
    # Add to PATH if necessary
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if (-not ($userPath -split ';' -contains $binDir)) {
        Write-Host "Adding $binDir to PATH in shell configuration..."
        $newPath = "$binDir;$userPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        $env:Path = "$binDir;$env:Path"
    }
}

Write-Host "Starting setup..."
.\mysql.bat install

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation complete!" -ForegroundColor Green
if ($mode -eq "1") {
    Write-Host "You can now run 'mysql start' from ANY directory."
    Write-Host "Note: You may need to restart your terminal for the 'mysql' command to be available."
} else {
    Write-Host "You can now run '.\mysql start' from inside the '$installDir' directory."
}
Write-Host "========================================" -ForegroundColor Cyan
