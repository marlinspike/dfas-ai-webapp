from azure.cosmos import CosmosClient
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from models import *
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Set up FastAPI and Jinja2
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# CosmosDB settings
# Load CosmosDB connection string from .env
COSMOS_CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING")
DATABASE_NAME = "dfas"
CONTAINER_NAME = "items"

# Connect to CosmosDB using the connection string
client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
database = client.get_database_client("dfas")
container = database.get_container_client("items")

@app.get("/")
async def read_items(request: Request):
    # Query to get all items from the container
    query = "SELECT * FROM c"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))

    # Pass the data to the Jinja2 template
    return templates.TemplateResponse("items.html", {"request": request, "items": items})
