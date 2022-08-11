# Importing zotero API and internal data methods:
from pyzotero import zotero
from .zotero_data_methods import get_zotero_collection, zotero_collection_to_dataframe, extract_zotero_items_for_date

# Importing plotly methods:
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Importing data manipulation packages:
import pandas as pd
import numpy as np
import datetime

# Function for generating calendar heatmaps (modified from https://gist.github.com/bendichter/d7dccacf55c7d95aec05c6e7bcf4e66e):
def display_year(
    z,
    year: int = None,
    month_lines: bool = True, 
    fig=None, 
    row: int = None,
    color: str = "#76cf63",
    collection_name: str = None
    ):
    """The method that renders a calendar heatmap showing the number of sources per day given 
    an array of Source counts.
    
    This method can either be called on its own to generate a calendar heatmap for a single year
    or it can be 'recursively' called by the display_years function to generate a heatmap across
    multiple years. 
    
    Args:
        z (np.array): A dataset containing the daily counts of all Sources read per day stored in a 
                1-D numpy array.
                
        year (int): The year that the calendar heatmap will be rendered for. It creates a subplot of
                the calendar heatmap with this specific year as a label.
                
        month_lines (Bool): A boolean which determines if lines will be used to seperate each month
                on the heatmap.
                
        fig (go.Figure): The figure object that the subplot the method generates will be appended too.
                This is necessary as this method is recursively called via the display_years() method.
        
        row (int): The row of the sublot that is used for labeling and the transforming the dataset.
        
        color (str): The color that the individaul plots would be. This sets the base color used in the
            colorscale.
            
    """
    if year is None:
        year = datetime.datetime.now().year
        
        data = np.ones(365) * 0
        data[:len(z)] = z
        
        d1 = datetime.date(year, 1, 1)
        d2 = datetime.date(year, 12, 31)

        delta = d2 - d1
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_days =   [31,    28,    31,     30,    31,     30,    31,    31,    30,    31,    30,    31]
        month_positions = (np.cumsum(month_days) - 15)/7

        dates_in_year = [d1 + datetime.timedelta(i) for i in range(delta.days+1)] #gives me a list with datetimes for each day a year
        weekdays_in_year = [i.weekday() for i in dates_in_year] #gives [0,1,2,3,4,5,6,0,1,2,3,4,5,6,…] (ticktext in xaxis dict translates this to weekdays
        
        weeknumber_of_dates = [int(i.strftime("%V")) if not (int(i.strftime("%V")) == 1 and i.month == 12) else 53
                            for i in dates_in_year] #gives [1,1,1,1,1,1,1,2,2,2,2,2,2,2,…] name is self-explanatory
    
        text = [str(date.strftime("%d %b, %Y")) for date in dates_in_year]
    
        #4cc417 green #347c17 dark green
        colorscale=[[False, '#eeeeee'], [True, color]]
        
        # handle end of year
        data = [
            go.Heatmap(
                x=weeknumber_of_dates,
                y=weekdays_in_year,
                z=data,
                text=text,
                hovertemplate = "<b style='font-family: Helvetica Neue;'>%{z} sources read on %{text}</b>",
                xgap=3, # this
                ygap=3, # and this is used to make the grid-like apperance
                showscale=False,
                colorscale=colorscale,
                hoverlabel=dict(align="left")
            )
        ]
        
        # TODO: Add onclick events in plotly to imbed links to each day's Sources page. 
        # https://plotly.com/python/click-events/

        if month_lines:
            kwargs = dict(
                mode='lines',
                line=dict(
                    color='#9e9e9e',
                    width=1
                ),
                hoverinfo='skip'        
            )
            for date, dow, wkn in zip(dates_in_year,
                                    weekdays_in_year,
                                    weeknumber_of_dates):
                if date.day == 1:
                    data += [
                        go.Scatter(
                            x=[wkn-.5, wkn-.5],
                            y=[dow-.5, 6.5],
                            **kwargs
                        )
                    ]
                    if dow:
                        data += [
                        go.Scatter(
                            x=[wkn-.5, wkn+.5],
                            y=[dow-.5, dow - .5],
                            **kwargs
                        ),
                        go.Scatter(
                            x=[wkn+.5, wkn+.5],
                            y=[dow-.5, -.5],
                            **kwargs
                        )
                    ]
                        
        layout = go.Layout(
            height=260,
            yaxis=dict(
                showline=False, showgrid=False, zeroline=False,
                tickmode='array',
                ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                tickvals=[0, 1, 2, 3, 4, 5, 6],
                autorange="reversed"
            ),
            xaxis=dict(
                showline=False, showgrid=False, zeroline=False,
                tickmode='array',
                ticktext=month_names,
                tickvals=month_positions
            ),
            font={'size':10, 'color':'#000000'},
            plot_bgcolor=('#fff'),
            margin = dict(t=40),
            showlegend=False
        )

        if fig is None:
            fig = go.Figure(data=data, layout=layout)
        else:
            fig.add_traces(data, rows=[(row+1)]*len(data), cols=[1]*len(data))
            fig.update_layout(layout)
            fig.update_xaxes(layout['xaxis'])
            fig.update_yaxes(layout['yaxis'])

    return fig


def display_years(z, years):
    """The method that makes use of the display_year() method to create and
    modify the calendar heatmap of Sources read. 
    
    Args:
        z (np.array): The dataset of Sources read per year stored as a 1-D array of integers.
        
        years (tuple): The relevant years of the dataset stored as a tuple which determines
            which subplots are generated eg: (2019, 2020).
    
    Returns:
        go.Figure: The fully rendered calendar heatmap ready to be passed onto the template.
    
    """
    fig = make_subplots(rows=len(years), cols=1, subplot_titles=years)
    for i, year in enumerate(years):
        data = z[i*365 : (i+1)*365]
        display_year(data, year=year, fig=fig, row=i)
        fig.update_layout(height=250*len(years))
    
    return fig

def build_source_array(dataframe, year):
    """This is a method that inqests a dataframe of zotro items and refactors it into 
    a 1-D array (list) of the number of sources read per day in a year.
    
    This array is used by the 'display_year' function to create the calendar heatmap
    of sources read per year.
    
    Args: 
        dataframe (pd.DataFrame): A dataframe built from zotero items (most likely using
        the zotero_collection_to_dataframe() method.
        
        year (datetime.datetime.date): The current year of the queryset and
            the calendar heatmap. It is used to build the datetime index.
    
    Returns: 
        lst: The 1-D array of source counts for the day. Should always be 365
            elements.
            
    """
    # Refactoring the zotero dataframe into number of items per day:
    df = dataframe.resample("D").apply({"Title":"count"})
    df.index = df.index.tz_localize(None)


    # Creating a pandas datetime index of each day in the current year: 
    heatmap_datetime_index = pd.date_range(
        start=datetime.date(year, 1, 1), 
        end=(datetime.date(year, 12, 31)),
        
    )
    
    # Full series of only 0 for the year:
    heatmap_series = pd.Series(data=0, index=heatmap_datetime_index.tz_localize(None))
    

    # Replacing the 0 values based on the index values present in the
    # annotated queryset:
    # WARNING: This may need to be refactored to be more efficent if speed becomes a problem:
    for day in df.index:
        heatmap_series.loc[day] = df.loc[day]["Title"]
        
    # Converting single_col df to 1-D array:
    #z = df["Title"].to_list()
    
    return heatmap_series.to_list()

# Function that produces a heatmap for a specific zotero collection based on name:
def build_collection_heatmap_pipeline(
    api_key: str,
    library_id: int,
    collection_name: str,
    year: str,
    library_type: str = "user"):
    """The method aggregates all the other logic to construct a source
    heatmap from the name of a zotero collection.
    
    It also returns the JSON response from the zotero API for use in other methods.
    
    Args:
        library_id (int): The zotero API user ID.
        
        api_key (str): The zotero API user key.
    
        library_type (str): The library type of the zotero object. Can be group or 
            user.
    
        collection_name (str): The verbose name for the zotero collection.
        
        year (str): The year that all the data will be extracted for.

    Returns:
        dict: A dictionary containing the generated heatmap as a plotly.graph_objs.heatmap and
            the JSON zotero collection data used to generate the heatmap.
    
    """
    # Extracting zotero items from a specific collection:
    items = get_zotero_collection(api_key=api_key, library_id=library_id, collection_name=collection_name)
    


    # Converting the list of zotero items to a structured dataframe:
    items_df = zotero_collection_to_dataframe(items)
    
    # Converting dataframe to a 1-D array of annual count values:
    current_year = datetime.datetime.now().year
    item_array = build_source_array(items_df, current_year)
    
    # Using the 1-D array to plot the heatmap:
    heatmap = display_year(item_array, collection_name=collection_name)
    
    # Building the dict of heatmap and collection data:
    payload = {"heatmap":heatmap, "collection":items}
    
    return payload

def build_heatmap_from_collection(
    collection: list, 
    #collection_name: str,
    year: int = datetime.datetime.now().year):
    """The method ingests a zotero JSON collection and generates a heatmap for that specific
    year using all of the other zotero dispaly methods above.

    Args:
        collection (list): This is the JSON collections data extracted using the Zotero API.

        year (int): This is the year that is used to filter the data. Filtering by year is done
            both at the dataframe array level and at the collection JSON level
    
        collection_name (str): The verbose name for the zotero collection.

    Returns:

        figure: A plotly.graph_obj heatmap.

    """
    # Filtering the collection based on the year provided:
    start_year = datetime.date(year, 1, 1).strftime("%Y-%m-%d") # Performance / readability issue need to make all dates date objs or strings, mixing is confusing
    
    # Extracting all items after this date
    items = extract_zotero_items_for_date(collection, start_date=start_year)
    
    # Converting the items to a dataframe and then into the 1-D array:
    item_df = zotero_collection_to_dataframe(items)
    item_array = build_source_array(item_df, year)

    # Using the 1-D array to plot the heatmap:
    heatmap = display_year(item_array)

    return heatmap