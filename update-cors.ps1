# Update CORS settings for the backend Azure App Service
# Make sure you're logged in to Azure CLI before running this script

# Variables
$resourceGroup = "ODL-OpenAI-1689746-02"
$backendAppName = "aipolicyback13"
$frontendAppUrl = "https://aipolicyfrontend13.azurewebsites.net"  # Replace with your frontend web app URL

# Update CORS settings
az webapp cors add --resource-group $resourceGroup --name $backendAppName --allowed-origins $frontendAppUrl

Write-Host "CORS settings updated!"
