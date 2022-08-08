# Importing plotly method: 
import plotly.express as px
import plotly.graph_objects as go

def plot_collection_timeseries(df):
    """A method that uses plotly express to generate a multi-column timeseries from
    a formatted dataframe.

    Args:
        df (pd.DataFrame): The dataframe that express will use to create the figure
            traces
        
    Returns:
        px.Figure: The timeseries graph

    """
    # Creating a figure from the dataframe:
    fig = px.line(df, x=df.index, y=df.columns)

    # Formatting and styling the figure:
    fig.update_layout(showlegend=False)

    return fig

def plot_total_item_timeseries(df):
    pass