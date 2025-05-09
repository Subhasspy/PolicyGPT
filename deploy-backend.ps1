# Deploy backend to Azure App Service
# Make sure you're logged in to Azure CLI before running this script

# Variables
$resourceGroup = "ODL-OpenAI-1689746-02"
$webAppName = "aipolicyback13"

# Navigate to backend directory
Set-Location -Path ".\backend"

# Create a deployment package
Compress-Archive -Path * -DestinationPath deploy.zip -Force

# Deploy to Azure App Service
az webapp deployment source config-zip --resource-group $resourceGroup --name $webAppName --src deploy.zip

# Clean up
Remove-Item deploy.zip

# Return to original directory
Set-Location -Path ".."

Write-Host "Backend deployment completed!"
