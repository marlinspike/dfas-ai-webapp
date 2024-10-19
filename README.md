# Running the app

# Building the container image
```
# Create the container image
docker build --platform linux/amd64 -t shuffereu/dfas-ai-webapp:v2 .

# Run the container locally
docker run -it --platform linux/amd64 -p 8000:8000 shuffereu/dfas-ai-webapp:v2

# Push the container image to docker hub
docker push shuffereu/dfas-ai-webapp:v2

# Create the webapp in azure 
 az webapp create --resource-group dfas2 --plan dfas2asp --name dfas2-webapp --deployment-container-image-name shuffereu/dfas-ai-webapp:v2

```

# Using ACR

```
# Create the ACR
az acr create --resource-group <your-resource-group> --name <your-acr-name> --sku Basic

# Push the container image to ACR
# Log in to ACR
az acr login --name <your-acr-name>

# Tag the image for the ACR repository
docker tag <your-image-name>:v1 <your-acr-name>.azurecr.io/<your-image-name>:v1

# Push the image to ACR
docker push <your-acr-name>.azurecr.io/<your-image-name>:v1

## Grant Azure Container APp Access to ACR
```
az acr update --name <your-acr-name> --resource-group <rg>  --admin-enabled true

```

## Create a Managed Idneitty for ACA and assign the AcrPull role to the ideneity so it can pull from ACR

```
az role assignment create --assignee dfas-acr-pull-role --role AcrPull --scope $(az acr show --name reubenc --query id --output tsv)

```

## Create an ACR using UID/PWD
```
az container create \
  --resource-group dfas2 \
  --name dfas-ai-webapp \
  --image reubenc.azurecr.io/dfas-ai-webapp:v2 \
  --registry-login-server reubenc.azurecr.io \
  --registry-username reubenc \
  --ports 8000 \
  --registry-password xxx+xxx \
  --cpu 1 --memory 1 \
  --dns-name-label dfasaiwebapp -o table
```

```


## Steps to deploy the FastAPI WebApp to Azure App Service

### Step 1: Resource Group Creation
Create a resource group named `dfas2` in your desired location (e.g., `eastus`):

```bash
az group create --name dfas2 --location eastus --output tsv
```

### Step 2: Create an App Service Plan
Create an App Service plan named `dfas-asp`:

```bash
az appservice plan create \
  --name dfas-asp \
  --resource-group dfas2 \
  --is-linux \
  --sku B1 \
  --output tsv
```
> **Note**: B1 is the Basic pricing tier. Modify the SKU to suit your needs if needed.

### Step 3: Create the WebApp with a Container Deployment and Assign Managed Identity
Create the WebApp that will use the container from ACR and assign a system-managed identity:

```bash
# **Important Note**: At this point, the WebApp may not be able to pull the container image from the Azure Container Registry (ACR) because the managed identity does not yet have the required `AcrPull` permission. The container deployment might fail initially, but this is resolved after assigning the `AcrPull` role in the next step.

# Create the WebApp
az webapp create \
  --resource-group dfas2 \
  --plan dfas-asp \
  --name dfas2-webapp \
  --deployment-container-image-name reubenc.azurecr.io/dfas-ai-webapp:v3 \
  --output tsv

# Assign a system-managed identity to the WebApp
az webapp identity assign --resource-group dfas2 --name dfas2-webapp --output tsv
```

### Step 4: Assign AcrPull Role for App Service to ACR
The system-assigned managed identity of the WebApp will need permission to pull the Docker container image from Azure Container Registry (ACR). To do this, assign the AcrPull role after creating the WebApp:

```bash
# Retrieve ACR resource ID
acr_id=$(az acr show --resource-group aoai --name reubenc --query "id" --output tsv)

# Retrieve the principal ID of the managed identity of the WebApp
identity_principal_id=$(az webapp identity show --resource-group dfas2 --name dfas2-webapp --query "principalId" --output tsv)

# Grant AcrPull permission for the managed identity
az role assignment create --assignee $identity_principal_id --scope $acr_id --role AcrPull --output tsv
```

### Step 5: Configure the WebApp to Run on Port 8000
Set the necessary app settings so that the WebApp runs on port 8000:

```bash
az webapp config appsettings set \
  --resource-group dfas2 \
  --name dfas2-webapp \
  --settings WEBSITES_PORT=8000 \
  --output tsv
```

### Step 6: Create Azure Function App (Optional)
If you want to create an Azure Function App, you can do so with the following commands:

```bash
# Create a storage account for the Function App
az storage account create \
  --name dfas2funcstorage \
  --resource-group dfas2 \
  --location eastus \
  --sku Standard_LRS \
  --output tsv

# Create the Function App
az functionapp create \
  --resource-group dfas2 \
  --consumption-plan-location eastus \
  --name dfas2-functionapp \
  --storage-account dfas2funcstorage \
  --runtime python \
  --functions-version 4 \
  --output tsv
```

### Step 7: Validate the Deployment
To ensure everything is working correctly, use the following validation steps:

1. **Verify WebApp Status**:
   ```bash
   az webapp show --resource-group dfas2 --name dfas2-webapp --query "state" --output tsv
   ```
   Ensure that the state is `Running`.

2. **Verify that the WebApp is accessible**:
   Open the WebApp URL in a browser or use `curl` to make sure it is responding:
   ```bash
   curl http://dfas2-webapp.azurewebsites.net
   ```

3. **Verify that the Managed Identity has AcrPull Role**:
   ```bash
   az role assignment list --assignee $identity_principal_id --scope $acr_id --query "[?roleDefinitionName=='AcrPull']" --output tsv
   ```
   Ensure that the output is not empty, confirming the role assignment.

### Step 8: Troubleshooting Tips
If the container still fails to start, try the following:
- **Check App Logs**:
  ```bash
  az webapp log tail --name dfas2-webapp --resource-group dfas2 --output tsv
  ```
  This can help identify missing dependencies or configuration issues.

- **Restart the WebApp**:
  ```bash
  az webapp restart --name dfas2-webapp --resource-group dfas2 --output tsv
  ```

### Step 9: Update the WebApp to Use a Different Container Version
If you need to update the container image used by the WebApp (for example, to deploy a new version of your application), you can use the following command to change the container image:

```bash
# Update the WebApp to use a different version of the container image
az webapp config container set \
  --resource-group dfas2 \
  --name dfas2-webapp \
  --docker-custom-image-name reubenc.azurecr.io/dfas-ai-webapp:v4 \
  --output tsv
```
> **Note**: Replace `v4` with the appropriate tag for the new version of your container image.

### Conclusion
Following these steps will create, deploy, and configure all necessary resources in Azure, ensuring that your FastAPI WebApp is up and running.




## Part 2: Deploy an Azure Function App as a Container

Below, I'll provide step-by-step Azure CLI commands to set up an Azure Function App as a container. The container image will be pulled from Azure Container Registry (ACR). We will assume the container image is named `dfas-ai-funcs`.

**NOTE:**

Function App can be co-hosted on the same App Service Plan as the WebApp, but only if both meet specific compatibility requirements:

- Linux Requirement: Both the WebApp and Function App need to be hosted in a Linux-based App Service Plan. In your case, the App Service Plan (dfas-asp) was created as a Linux plan (--is-linux), which makes it compatible for co-hosting both a WebApp and Function App container.

- Elastic Premium Plan: Azure Function Apps require an Elastic Premium (EP) or App Service Plan when using custom Docker containers. You would need at least a Premium v2 plan (such as P1v2) to support Function Apps as containers. 

**Commands to Co-host the Function App:** If you decide to use the same App Service Plan, the Function App can be created using the existing plan (dfas-asp) with a modified command:

```
# Create the Function App using the existing App Service Plan
az functionapp create \
  --resource-group dfas2 \
  --plan dfas-asp \  # Use the existing plan
  --name dfas2-functionapp \
  --storage-account dfasfuncstorage \
  --deployment-container-image-name reubenc.azurecr.io/dfas-ai-funcs:v1 \
  --functions-version 4 \
  --os-type Linux \
  --output tsv
```


### Step 1: Create the Azure Function App Plan
Create a dedicated Function App Plan to host the Azure Function App. This will allow the Function App to use Linux containers:

```bash
az functionapp plan create \
  --resource-group dfas2 \
  --name dfas-func-plan \
  --location eastus \
  --number-of-workers 1 \
  --sku EP1 \
  --is-linux \
  --output tsv
```
> **Note**: The SKU `EP1` refers to the Elastic Premium tier, which allows the use of custom containers.


### Step 2: Create a Storage Account for the Function App
Azure Function Apps require a storage account to store triggers and other state information:

```bash
az storage account create \
  --name dfasfuncstorage \
  --resource-group dfas2 \
  --location eastus \
  --sku Standard_LRS \
  --output tsv
```


### Step 3: Create the Function App with a Container Deployment
Create the Function App and configure it to use the container image from ACR:

```bash
# Create the Function App with a container image
az functionapp create \
  --resource-group dfas2 \
  --plan dfas-func-plan \
  --name dfas2-functionapp \
  --storage-account dfasfuncstorage \
  --deployment-container-image-name reubenc.azurecr.io/dfas-ai-funcs:v1 \
  --functions-version 4 \
  --os-type Linux \
  --output tsv
```
> **Note**: Replace `v1` with the appropriate tag for the container image you want to use.


### Step 4: Assign AcrPull Role for Function App to ACR
The Function App's managed identity will need permission to pull the Docker container image from ACR. Assign the `AcrPull` role to the Function App's identity:

```bash
# Assign AcrPull role for Function App to access ACR
identity_principal_id=$(az functionapp identity assign --resource-group dfas2 --name dfas2-functionapp --output tsv --query principalId)

# Grant AcrPull permission for the managed identity
az role assignment create --assignee $identity_principal_id --scope $acr_id --role AcrPull --output tsv
```

### Step 5: Validate the Deployment
To ensure everything is working correctly, use the following validation steps:

1. **Verify Function App Status**:
   ```bash
   az functionapp show --resource-group dfas2 --name dfas2-functionapp --query "state" --output tsv
   ```
   Ensure that the state is `Running`.

2. **Verify Logs**:
   Use the following command to view live logs and ensure the function is running properly:
   ```bash
   az functionapp log tail --name dfas2-functionapp --resource-group dfas2 --output tsv
   ```