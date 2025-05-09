# Deploy both backend and frontend to Azure App Service
# Make sure you're logged in to Azure CLI before running this script

# Variables
$resourceGroup = "ODL-OpenAI-1689746-02"
$backendAppName = "aipolicyback13"
$frontendAppName = "aipolicyfrontend13"  # Replace with your frontend web app name if different

# Check if Azure CLI is installed
try {
    $azVersion = az --version
    Write-Host "Azure CLI is installed."
} catch {
    Write-Host "Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit
}

# Check if logged in to Azure
try {
    $account = az account show
    Write-Host "Already logged in to Azure."
} catch {
    Write-Host "Not logged in to Azure. Please run 'az login' first."
    exit
}

# Deploy backend
Write-Host "Deploying backend..."
.\deploy-backend.ps1

# Deploy frontend
Write-Host "Deploying frontend..."
.\deploy-frontend.ps1

# Update CORS settings
Write-Host "Updating CORS settings..."
.\update-cors.ps1

Write-Host "Deployment completed!"
Write-Host "Backend URL: https://$backendAppName.azurewebsites.net"
Write-Host "Frontend URL: https://$frontendAppName.azurewebsites.net"
