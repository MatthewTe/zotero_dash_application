# Importing dash methods:
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Data management packages:
import datetime

# Importing display methods:
from utils import build_heatmap_from_collection, extract_zotero_items_for_date

# Importing the component methods:
from components import build_source_accordion

dash.register_page(
    __name__,
    path='/',
    name='Homepage'
    )

def layout():
    return html.Div(
        children=[

            html.Div([
            html.H3(style={"padding-top":"2rem"}, id="heatmap_title"),
            dcc.Graph("main_heatmap"),
            html.H4(id="heatmap_accordion_title"),
            dbc.Accordion(id="main_heatmap_accordion", flush=True)
            ])
        ]
    )

# Callback that generates the graph from the collection data stored in the browser session:
@callback(
    Output("main_heatmap", "figure"),
    Output("heatmap_title", "children"),
    Input("main_zotero_collection", "data")
)
def generate_heatmap(data):
    """The method that takes the zotero collection data and builds the plotly heatmap via 
    existing zotero data methods.

    Args:
        data (list): The JSON list of the zotero collection data

    Return:
        figure: A plotly.graph_obj heatmap

        str: The string used to format the heatmap title

    """
    if data != None:
        
        # Setting the year used to build all the datasets:
        year = datetime.datetime.now().year

        # Generating heatmap from browser session zotero collection:
        heatmap = build_heatmap_from_collection(data, year=year)

        title_string = f"Sources Read in {year}"

        return heatmap, title_string

# Callback that generates a collapsable list of data on a single day from a specific click event:
@callback(
    Output("main_heatmap_accordion", "children"),
    Output("heatmap_accordion_title", "children"),
    Input("main_heatmap", "clickData"),
    Input("main_zotero_collection", "data"),
    Input("all_zotero_collections", "data")
)
def build_accordion_from_heatmap_daily_point(clickData, data, collections):
    """The callback that builds and returns the children for the accordion component
    that displays information about the sources returned  for a single day given an 
    on click event from the heatmap. 
    
    It also returns frontend styling infomration for other assocaited components. 

    Args:
        clickData (dict): The dict of a single zotero item that contains a date.

        data (lst): The list of zotero item data.

        collections (lst): The list of collection data.

    Return:

        lst: A list of dbc.AccordionItems generated from zotero sources from the date
            value provided.

        str: A string for the title of the heatmap accordion.

    """
    # Extracting the point data from the heatmap:
    if clickData == None:
        return dbc.AccordionItem("Click on a data point on the heatmap to see sources read for that day.", title="No Date Selected"), "Select a Date on the Heatmap"
    
    else:
        
        # Extracting the date value from the heatmap click:
        date_value = datetime.datetime.strptime(clickData["points"][0]["text"], '%d %b, %Y').strftime("%Y-%m-%d")
        #print(date_value)

        # Extracting the main zotero collection from browser session and filtering it based on the provided date vale:
        day_sources = extract_zotero_items_for_date(collection=data, date=date_value)
        #print(day_sources)

        # Iterating over all the sources for the day and building dbc.AccordionItems:
        accordion_items = [build_source_accordion(source, collections) for source in day_sources]
        
        # Building the accordion item title:
        accordion_title = f"Sources read on {date_value}"

        return accordion_items, accordion_title