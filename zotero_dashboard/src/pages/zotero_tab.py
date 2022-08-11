# Importing dash methods:
import dash
from dash import dcc
from dash import html

dash.register_page(
    __name__, 
    path_template='/collection/<collection_id>',
    name='My Collections'
)

def layout(collection_id=None):
    return html.Div([
        html.H1(f"PAGE {collection_id}")
    ])