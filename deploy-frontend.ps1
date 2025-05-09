# Deploy frontend to Azure App Service
# Make sure you're logged in to Azure CLI before running this script

# Variables
$resourceGroup = "ODL-OpenAI-1689746-02"
$webAppName = "aipolicyfrontend13"  # Replace with your frontend web app name

# Navigate to frontend directory
Set-Location -Path ".\frontend"

# Build the Angular app for production
npm run build

# Navigate to the build output directory
Set-Location -Path ".\dist\frontend"

# Create a deployment package
Compress-Archive -Path * -DestinationPath deploy.zip -Force

# Deploy to Azure App Service
az webapp deployment source config-zip --resource-group $resourceGroup --name $webAppName --src deploy.zip

# Clean up
Remove-Item deploy.zip

# Return to original directory
Set-Location -Path "..\..\.."

Write-Host "Frontend deployment completed!"
