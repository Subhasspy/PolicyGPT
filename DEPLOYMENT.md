# Deploying PolicyGPT to Azure Web App

This document provides instructions for deploying the PolicyGPT application to Azure Web App.

## Prerequisites

1. Azure CLI installed
2. Azure account with active subscription
3. Node.js and npm installed
4. Python 3.x installed

## Deployment Options

### Option 1: Using VS Code Azure Extension (Recommended)

#### Backend Deployment

1. Open VS Code
2. Click on the Azure icon in the Activity Bar (left side)
3. Expand the App Service section
4. You should see your subscription and the "aipolicyback13" web app
5. Right-click on "aipolicyback13" and select "Deploy to Web App..."
6. Select the "backend" folder as the deployment source
7. Wait for the deployment to complete

#### Configure Backend Environment Variables

1. In the Azure extension, right-click on "aipolicyback13" and select "Open in Portal"
2. In the Azure Portal, navigate to "Settings" > "Configuration"
3. Add the following Application settings:
   - OPENAI_API_KEY
   - OPENAI_API_BASE
   - OPENAI_MODEL_NAME
   - AZURE_TRANSLATOR_KEY
   - AZURE_TRANSLATOR_ENDPOINT
   - AZURE_TRANSLATOR_REGION
   - WEBSITES_PORT = 8000
4. Click "Save" to apply the settings

#### Create and Deploy the Frontend

1. In VS Code's Azure extension, right-click on "App Service" and select "Create New Web App..."
2. Enter a unique name for your frontend app (e.g., "aipolicyfrontend13")
3. Select the same resource group as your backend (ODL-OpenAI-1689746-02)
4. Choose a runtime stack (Node.js LTS)
5. Choose a pricing tier (Free or Basic)
6. Wait for the web app to be created
7. Right-click on the newly created web app and select "Deploy to Web App..."
8. Select the "frontend/dist/frontend" folder as the deployment source
9. Wait for the deployment to complete

#### Update CORS Settings

1. In the Azure Portal, navigate to your backend app (aipolicyback13)
2. Go to "API" > "CORS"
3. Add your frontend URL (e.g., https://aipolicyfrontend13.azurewebsites.net) to the allowed origins
4. Click "Save"

### Option 2: Using PowerShell Scripts

1. Make sure you're logged in to Azure CLI:
   ```powershell
   az login
   ```

2. Run the deployment script:
   ```powershell
   .\deploy-all.ps1
   ```

   This script will:
   - Deploy the backend to Azure App Service
   - Build and deploy the frontend to Azure App Service
   - Update CORS settings to allow communication between the two apps

## Verifying the Deployment

1. Open your frontend URL (e.g., https://aipolicyfrontend13.azurewebsites.net) in a browser
2. Test the application by uploading a PDF file and checking if the summary is generated
3. If there are any issues, check the logs in the Azure Portal for both the backend and frontend apps

## Troubleshooting

1. If the backend API calls fail, check:
   - CORS settings in the backend app
   - Environment variables in the backend app
   - Network security settings

2. If the frontend doesn't load properly, check:
   - Deployment logs in the Azure Portal
   - Web server logs
   - Browser console for any JavaScript errors

3. If you need to redeploy:
   - Make your changes locally
   - Run the appropriate deployment script again
   - Check the logs for any deployment errors
