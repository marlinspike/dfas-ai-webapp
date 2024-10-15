from azure.cosmos import CosmosClient
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from models import *
import os
from dotenv import load_dotenv
import math
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
async def read_items(request: Request, page: int = 1, size: int = 10):
    query = "SELECT * FROM c"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    
    # Pagination logic
    total_items = len(items)
    total_pages = math.ceil(total_items / size)  # Calculate the total number of pages
    start = (page - 1) * size
    end = start + size
    paged_items = items[start:end]
    
    return templates.TemplateResponse(
        "items.html", 
        {
            "request": request,
            "items": paged_items,
            "total_items": total_items,
            "page": page,
            "size": size,
            "total_pages": total_pages  # Pass total_pages to the template
        }
    )