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
