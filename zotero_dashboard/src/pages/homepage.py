# Importing dash methods:
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.graph_objs as go
import plotly.express as px

# Data management packages:
import datetime

# Importing display methods:
from utils import (
    build_heatmap_from_collection, extract_zotero_items_for_date, create_collection_counts, plot_collections_count_radar_figure, 
    create_collection_timeseries_df, plot_collection_timeseries, plot_total_item_timeseries
)

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
            
            # Top Heatmap Components:
            html.H3(style={"padding-top":"2rem"}, id="heatmap_title"),
            dcc.Graph("main_heatmap"),
            html.H4(id="heatmap_accordion_title"),
            dbc.Accordion(id="main_heatmap_accordion", flush=True, always_open=True, start_collapsed=True),
            html.Hr(),
            
            # Sources Count Components:
            dbc.Row([


                dbc.Row([
                    dbc.Col([
                        html.H4("Breakdown of sources read by category", style={"padding-bottom":"0.25rem"})
                    ])]),

                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="source_radar")], width=6),

                    dbc.Col([dcc.Graph(id="source_timeseries")], width=6)
                    ])
                ], style={"padding-top":"0.5rem"}),
                html.Hr(),

                dbc.Row([
                    dbc.Col([
                        html.H4("Total sources read overtime", style={"padding-bottom":"0.25rem"}),    
                        dcc.Graph(id="total_items_timeseries")
                    ])
            ])

        ])
    ])

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

    else:
        return go.Figure(), "No Data Selected"

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

        abc.AccordionItem: A list of dbc.AccordionItems generated from zotero sources from the date
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

        accordion_content = accordion_items

        return accordion_content, accordion_title

# Callback that creates and populates the Collection breakdown plots based on zotero sources and collections:
@callback(
    Output("collection_breakdown_date_picker", "min_date_allowed"),
    Input("main_zotero_collection", "data")
)
def format_datepicker_based_on_dataset(data):
    """The method that formats the collection breakdown datepicker based on the date ranges avalible
    provided by the the main collections dataset from the browser session.

    Args:
        data (list): The JSON list of the zotero collection data

    Returns:

        str: The minium date allowed by the datepicker
    """
    #TODO: Write this method lol:
    if data != None:
        pass
        

@callback(
    Output("source_radar", "figure"),
    Input("main_zotero_collection", "data"),
    Input("all_zotero_collections", "data")
) 
def build_radial_graph_breakdown(data, collections):
    """The callback that builds the radial graphs.

    The method relies on the two browser session data stores containing all zotero items and collections.
        
    Args:
        data (lst): The list of zotero item data.

        collections (lst): The list of collection data.

    Returns:
        go.Figure: The Radial Graph.

    """
    if data != None and collections != None:
        # Transforming collection data into radial format:
        collection_count_df = create_collection_counts(data, collections, cutoff=20)    
        
        # Generating the Radar plot:
        r = collection_count_df["count"].tolist()
        theta = collection_count_df["name"].tolist()    
        radar_graph = plot_collections_count_radar_figure(r, theta)

        return radar_graph
    
    else:
        return go.Figure()

@callback(
    Output("source_timeseries", "figure"),
    Input("source_radar", "clickData"),
    Input("main_zotero_collection", "data"),
    Input("all_zotero_collections", "data")
)
def build_single_collection_timeseries(clickData=None, items=None, collections=None):
    """The method that takes in a collection name as click data from the radial graph and
    creates a timeseries displaying the number of sources read for that particular collection
    per day

    Args:
        clickData (dict): The JSON of click data returned from the radial plot.

        items (lst): The list of zotero item data.

        collections (lst): The list of collection data.

    Returns:
        go.Figure: The timeseries displaying the number of sources read for that particular collection

    """
    # Extracting the collection data from the radial clickData:
    if clickData != None:
        collection_name = clickData["points"][0]["theta"]
        
        collection = [collection for collection in collections if collection["data"]["name"] == collection_name]
        
        # Creating a timeseries dataset from the collection:
        # TODO: Add date functionality:
        timeseries_df = create_collection_timeseries_df(items, collection).cumsum()

        # Create a timeseries from the dataframe:
        timeseries_fig = px.area(timeseries_df, x=timeseries_df.index, y=timeseries_df.columns)
        #timeseries_fig = plot_collection_timeseries(timeseries_df)

        # Custom figure formatting:
        timeseries_fig.update_layout(
            title=f"Total Sources Read for {collection_name}",
            yaxis_title="Source Read",
            xaxis_title="",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False

        )
        timeseries_fig.update_layout(
            xaxis=dict(showgrid=False, showline=True, linecolor="black"),
            yaxis=dict(showgrid=False, showline=True, linecolor="black")
        )

        return timeseries_fig

    else:
        # Displaying an empty timeseries figure:
        fig = go.Figure()

        return fig
        
@callback(
    Output("total_items_timeseries", "figure"),
    Input("main_zotero_collection", "data"),
    Input("all_zotero_collections", "data")
)        
def build_total_collection_timeseries(items, collections):
    """The method plots the total number of sources read as a timeseries.

    Args:
        items (lst): The list of zotero item data.

        collections (lst): The list of collection data.

    Returns:
        go.Figure: The timeseries displaying the number of sources read.

    """
    if items != None and collections != None:
        # Creating a dataframe from items:
        total_items_df = create_collection_timeseries_df(items, collections).cumsum()
            
        # Plotting the timeseries based on dataframe:
        total_item_fig = px.area(total_items_df, x=total_items_df.index, y=total_items_df.columns)

        # Customizing the figure:
        total_item_fig.update_layout(
            yaxis_title="Source Read",
            xaxis_title="",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            
            xaxis=dict(showgrid=False, showline=True, linecolor="black"),
            yaxis=dict(showgrid=False, showline=True, linecolor="black"),

            legend=dict(title="Categories")
        )

        return total_item_fig
    
    else:
        return go.Figure()
    
    