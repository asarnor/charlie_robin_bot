# PowerShell setup script for environment configuration files

Write-Host "Charlie Robin Trading Bot - Environment Setup" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Function to copy example file if it doesn't exist
function Setup-EnvFile {
    param(
        [string]$EnvName
    )
    
    $exampleFile = "env.$EnvName.example"
    $envFile = ".env.$EnvName"
    
    if (Test-Path $envFile) {
        Write-Host "⚠️  $envFile already exists. Skipping..." -ForegroundColor Yellow
    } else {
        if (Test-Path $exampleFile) {
            Copy-Item $exampleFile $envFile
            Write-Host "✅ Created $envFile from $exampleFile" -ForegroundColor Green
            Write-Host "   Please edit $envFile and add your credentials" -ForegroundColor Gray
        } else {
            Write-Host "❌ Example file $exampleFile not found" -ForegroundColor Red
        }
    }
}

# Setup all environment files
Write-Host "Setting up environment files..." -ForegroundColor Cyan
Write-Host ""

Setup-EnvFile "local"
Setup-EnvFile "sandbox"
Setup-EnvFile "production"

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env.local, .env.sandbox, or .env.production with your credentials"
Write-Host "2. Set ENVIRONMENT variable when running:"
Write-Host "   `$env:ENVIRONMENT='local'; python trading_bot.py"
Write-Host "   `$env:ENVIRONMENT='sandbox'; python trading_bot.py"
Write-Host "   `$env:ENVIRONMENT='production'; python trading_bot.py"
Write-Host ""
Write-Host "⚠️  Remember: Never commit .env.* files to version control!" -ForegroundColor Yellow

