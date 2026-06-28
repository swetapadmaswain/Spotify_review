# PowerShell script to move backend files to a separate folder

$source = "c:\Graduation Project - Spotify\backend"
$destination = "c:\Graduation Project - Spotify\backend_separate"

# Create destination folder if it doesn't exist
if (-not (Test-Path $destination)) {
    New-Item -ItemType Directory -Path $destination | Out-Null
}

# Copy backend files to new folder
Copy-Item -Path "$source\*" -Destination $destination -Recurse -Force

Write-Host "Backend files moved to: $destination"
Write-Host "Contents:"
Get-ChildItem -Path $destination
