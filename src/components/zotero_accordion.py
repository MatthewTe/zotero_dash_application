# Importing the dash methods:
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc 

# Function that builds a dash bootstrap component based on zotero source components:
# TODO: Look into making this an All-in-One component along with the heatmap: https://dash.plotly.com/all-in-one-components
# TODO: Change things like the Author and Collection Name and other sections like the Source as a bootstrap Button  
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/button/
def build_source_accordion(item, zotero_collections):
    """A method that builds a dash bootstrap "accordion" component that displays a single 
    zotero source item.

    Args:
        item (dict): The single zotero item used to build the boostrap component.

        zotero_collections (list): The list of zotero collections. 

    Returns:
        dbc.AccordionItem: The item that displays all of the Zotero source item fields. 

    """
    # Attempting to unpack the zotero fields:
    title = item["data"].get("title", None)
    url = item["data"].get("url", None)    
    website = item["data"].get("websiteTitle", None)
    abstract = item["data"].get("abstractNote", None)

    # Processing creators/author components - Author's return a dict of author content {}:
    authors = item["data"].get("creators", None)
    accordion_authors = []
    if authors != None: # <-- Returns an empty list when there is no author so need to check for this too:
        if len(authors) > 0:
            for author in authors:
                creator_type = author.get("creatorType", None)             
                name = author.get("name", None)

                # If there are no first and last name then there could be a single value as 'name':
                if name == None:
                    first_name = author.get("firstName", None)
                    last_name = author.get("lastName", None)

                    author_row = dbc.Row(dbc.Col([html.B(f"{creator_type}"),f": {first_name}, {last_name}"]))                    
                else:
                    author_row = dbc.Row(dbc.Col([html.B(f"{creator_type}"),f": {name}"]))
                
                accordion_authors.append(author_row)
    
    def get_collection_name(collection_id, collections):
        for collection in collections:
            if collection["key"] == collection_id:
                return html.H4(collection['data']['name'])

    # Processing the component id and name properties:
    collection_id = item["data"]["collections"][0] # <-- At most it has to be a len 1 list

    collection_value = get_collection_name(collection_id, zotero_collections)

    # Creating row stylings for inside the accordion:
    title_row = dbc.Row([
        dbc.Col(html.A(html.H3(title), href=url), width=10),
        dbc.Col([html.H4(website)], width=2)
    ])
    collection_row = dbc.Row(dbc.Col(collection_value))
    author_row = dbc.Row(accordion_authors)
    abstract_row = dbc.Row(dbc.Col(abstract, style={"padding-top":"1rem"}))

    # Building the accordion Items:
    accordion_title_str = f"{website}: {title}"
    accordion_body = html.Div([title_row, collection_row, author_row, abstract_row])

    return dbc.AccordionItem(accordion_body, title=accordion_title_str)
