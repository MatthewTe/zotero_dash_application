# Importing zotero API:
from pyzotero import zotero

# Importing plotly methods:
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Importing data manipulation packages:
import pandas as pd
import numpy as np
import datetime

# Method that returns a collection of zotero items given a collection name:
def get_zotero_collection(
    api_key: str,
    library_id: int,
    collection_name: str = None,
    library_type: str = "user"):
    """Method that returns a collection of zotero items given a collection 
    name
    
    Args:
        library_id (int): The zotero API user ID.
        
        api_key (str): The zotero API user key.
    
        library_type (str): The library type of the zotero object. Can be group or 
            user.
    
        collection_name (str): The verbose name for the zotero collection.

    Returns:
        lst: The JSON object of zotero items from a specific collection.
        
    """
    # Creating a zotero API object:
    zotero_con = zotero.Zotero(library_id, library_type, api_key)
    
    # Querying the list of zotero collections to extract the ID for collection name:
    # If no collections provided:
    if collection_name == None:
        items = zotero_con.everything(zotero_con.items())
        
    # If a colleciton is provided:
    else:
        collection_id = None
        for collection in zotero_con.collections():
            if collection["data"]["name"] == collection_name:
                collection_id = collection["data"]["key"]

        # Using the collection id to query all items from the specific collection:
        if collection_id == None:
            return None

        items = zotero_con.everything(zotero_con.collection_items(collection_id))
        
    return items

# Converting a zotero collection to the dataframe:
def zotero_collection_to_dataframe(collection: list):
    """The function takes in a list of zotero objects (from a collection or a library)
    and converts them into a timeseries dataframe of sources. 
    
    The function is collection/library agnostic as it uses the timestamp inside of a
    zotero item dict to build a full dataframe.
    
    Args:
        collection (lst): The list of zotero item dicts - commonly extracted from the 
        Zotero API.
        
    Returns:
        pd.Dataframe: The timeseries dataframe of all zotero sources/items
        
    """    
    # Filtering out attachements and other attribute items (extracting data only):
    collection = [item["data"] for item in collection if item["data"]["itemType"] != "attachment"]
    
    # Slicing each item (dict) to contain only the keys that will be present in the dataframe:
    # Dict comprehension inside of list comprehension [{key logic} for item in items]:
    core_keys = {"itemType", "title", "creators", "dateAdded"}
    collection_filtered = [{key: item[key] for key in item.keys() & core_keys} for item in collection]
    
    # Converting list of item dicts to dataframe:
    df = pd.DataFrame.from_dict(collection_filtered, orient="columns")
    df.rename(columns={"title":"Title", "dateAdded":"Date"}, inplace=True)
    df.set_index("Date", inplace=True)
    df = df[["Title", "creators", "itemType"]]
    df.index = pd.to_datetime(df.index)
    
    return df

# Creating a full method that extracts zotero items for a specific date:
def extract_zotero_items_for_date(
    collection: list,
    date: str = None,
    start_date: str = None
):
    """The method ingests a JSON zotero collection and filters the response
    according to the date provided.
    
    Args:
    
        date (str): The date used to filter the zotero items in the format
            YYYY-MM-DD.
    
        start_date (str): If a date value is not provided then start and end dates are used
            to filter collections. In the form of YYYY-MM-DD

        collection (list): The JSON response containing Zotero collection API response that is
            used by the method as the full dataset.
        
    Returns:
        lst: The JSON object of zotero items that were added on the specified date. 
    
    """    
    # Filtering the data based on the provided date: 
    if date != None:

        # Converting date to datetime object:
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        collection = [
            item for item in collection 
            if item["data"]["itemType"] != "attachment" and
            datetime.datetime.strptime(item["data"]["dateAdded"], "%Y-%m-%dT%H:%M:%S%z").date() == date
        ]
    
    else:
        # Filtering collections based on start date:
        if start_date != None:
    
            # Converting start date to date object:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            
            # Only selecting items in the collections that are 'greater' than the start date:
            collection = [
                item for item in collection 
                if item["data"]["itemType"] != "attachment" and
                datetime.datetime.strptime(item["data"]["dateAdded"], "%Y-%m-%dT%H:%M:%S%z").date() >= start_date
            ]
        
        # TODO: Add end date functionality:

    return collection

def get_all_collections(
    api_key: str,
    library_id: int,
    library_type: str = "user"):
    """A function that creates a zotero API and queries a list of zotero 
    collections.

    Args:
        library_id (int): The zotero API user ID.
        
        api_key (str): The zotero API user key.
    
        library_type (str): The library type of the zotero object. Can be group or 
            user.
    
    Returns:
        lst: The JSON object of zotero collections data. 

    """
    # Creating the zotero API object:
    zotero_con = zotero.Zotero(library_id, library_type, api_key)

    collections = zotero_con.collections()

    return collections

def get_collection_name():
    """
    """
    pass