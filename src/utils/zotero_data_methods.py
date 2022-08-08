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
    zotero_con.add_parameters(sort="dateAdded", direction="asc")

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
    
    #print("\n\n", items[0]["data"]["dateAdded"], items[-1]["data"]["dateAdded"])

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

def create_collection_counts(items, collections, cutoff=None):
    """The method ingests a list of zotero items and collections and generates
    a dataframe containing the amount of sources read per collection.

    Args:
        
        items (lst): The list of zotero item data.

        collections (lst): The list of collection data.

        cutoff (None|int): A number that determines the minimum number of sources read required for 
            a collection to be included in the dataframe. If a collection has a number of sources read
            lower than the cutoff it is not included in the final df.
    
    Retuns:
        pd.Dataframe: The dataframe containing the number of sources from each 
            collection read. 

    """
    # TODO: Determine if I should only extract data from Parent Collections.
    # Parsing the collections for a list of individual collection names: 
    collections = [collection["data"] for collection in collections]
    items = [item["data"] for item in items if item["data"]["itemType"] != "attachment" and len(item["data"]["collections"]) > 0] # <-- Removing attachments from zotero item
    
    # Counting the number of items in each collection (O(n^2) cringe): 
    for collection in collections:

        num_items = 0 
        for item in items:
            if len(item["collections"]) > 0:
                if item["collections"][0] == collection["key"]:
                    num_items = num_items + 1 
        
        collection["count"] = num_items
        
    # Converting collections dataframe to dict:
    if cutoff != None:
        collections_cutoff = [collection for collection in collections if collection["count"] > cutoff]
    else:
        collections_cutoff = collections 

    collection_df = pd.DataFrame(collections_cutoff)
    
    return collection_df

def create_collection_timeseries_df(items, collections, start_date=None, end_date=None):
    """The method that converts the item dictionary to a pandas dataframe containing the counts
    of collections read for each day in the date range.
    """    
    # Depnding on the combination of start and end date values provided the index range will be built:
    if start_date == None and end_date == None:

        # Assuming the main collection items are sorted by dateAdded in ascending order - creating date range:
        start_date = items[0]["data"]["dateAdded"]
        end_date = items[-1]["data"]["dateAdded"]
        datetime_index = pd.date_range(start=start_date, end=end_date)
    
    elif end_date == None:
        year = datetime.datetime.now().year
        end_date = datetime.date(year, 12, 31)
    else:
        pass

    datetime_index = pd.date_range(start=start_date, end=end_date, freq='D')

    # Building a dictionary with the datetime index values as the main key to be populated:
    collection_count_dict = {}

    for date in datetime_index:
        # All collections queried for that date (that have collection values):
        collections_date = [
            item for item in extract_zotero_items_for_date(items, date=date.strftime("%Y-%m-%d")) 
            if len(item["data"]["collections"]) > 0]
        
        single_day_count = {}

        for collection in collections:
            collection_count_lst = [item for item in collections_date if item["data"]["collections"][0] == collection["data"]["key"]]
            
            # Adding the count of collection items to the counter dict:
            single_day_count[collection["data"]["name"]] = len(collection_count_lst)
            

        # Adding the counter dict to the main dict:
        collection_count_dict[date.strftime("%Y-%m-%d")] = single_day_count

    # Building the dataframe based on the dictionary:
    daily_collection_count_df = pd.DataFrame.from_dict(collection_count_dict, orient="index")
    
    return daily_collection_count_df