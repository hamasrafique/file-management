$path = ".\my-first-ec2-key.pem"
# Reset to remove inherited permissions
icacls $path /reset
# Grant Read-Only access to the current user
icacls $path /grant:r "$($env:USERNAME):(R)"
# Remove inheritance and wipe all other permissions
icacls $path /inheritance:r
Write-Host "Permissions fixed for $path"
