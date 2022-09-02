# Importing dash methods:
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

import dash_bootstrap_components as dbc

# Importing zotero data management APIs:
from utils import get_zotero_collection, get_all_collections

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions = True,
    url_base_pathname="/zotero_dashboard/"
)
server = app.server


# Main layout for the Dash Application:
app.layout = dbc.Container([

    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Welcome to the Zotero API Dashboard - A Plotly Dashboard that shows your research/reading trends")),
        dbc.ModalBody([
            html.H3("Tutorial:", style={"padding-bottom":"1rem"}),
            html.H4("Get your Library ID and API Key from your Zotero Account"),
                html.P([
                    "The dashboard queries data using the Python Zotero API, which requires your zotero main Library ID and your API key. You can find your Library ID (user ID) and API Key can be found or created in the Feeds/API section of your Zotero accout ", 
                    html.A("here.", href="https://www.zotero.org/settings/keys"),
                    dbc.CardImg(src=app.get_asset_url("images/Zotero_userID_screenshot.png"), style={"padding-top":"1rem"})
                    ]),

                html.H4("Entering your userID and your Zoter API", style={"padding-top":"1rem"}),
                html.P("Enter your userID and Zotero API in their respective input fields and wait for the dashboard to fully load all zotero source items (this may take awhile)"),
                dbc.CardImg(src=app.get_asset_url("images/Zotero_Dash_Inputs.png"), style={"padding-bottom":"1rem"}),
                html.P("When your data has been fully loaded the Status indicator will turn from red to green and the full dashboard should load soon after and look like this:"),
                dbc.Row([
                    dbc.Col(dbc.CardImg(src=app.get_asset_url("images/Navbar_no_data_button.png"))),
                    dbc.Col(dbc.CardImg(src=app.get_asset_url("images/Navbar_data_found_button.png")))
                ]),    
                html.H4("External Links:"),
                dbc.Row(html.A("Project Github", href="https://github.com/MatthewTe/zotero_dash_application")),
                dbc.Row(html.A("Zotero", href="https://www.zotero.org/"))        
            ]
        )
    ], 
    id="inital-tutorial-popup",
    size="xl",
    is_open=True,
    style={
        }
    ),    

    dbc.Navbar([

        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=app.get_asset_url("images/zotero_48x48x32.png"))),
                            dbc.Col(dbc.NavbarBrand("Zotero Dashboard", className="ms-2"))
                        ],
                        align="center",
                        className="g-0"
                    ),
                    href="https://www.zotero.org/",
                    style={"textDecoration":"none"}
                ),
                dbc.Row([
                    # Main Zotero Account Inputs:
                    dbc.Col(dbc.Input(id="zotero_library_id", type="number", placeholder="Zotero Library ID")),
                    dbc.Col(dbc.Input(id="zotero_api_key", type="text", placeholder="Zotero API Key")),
                    dbc.Col(dbc.Button("No Data Found", color="danger", id="status_button")),
                    dbc.Col(dbc.Button("Help", id="help_button", color="info", className="me-1"))
                ]),

                dbc.Tooltip(
                    "This is your userID from your Zotero account.",
                    target="zotero_library_id",
                    placement="bottom"
                ),
                dbc.Tooltip(
                    "This is your web API key for your Zotero account.",
                    target="zotero_api_key",
                    placement="bottom"
                )
            ]
        )
        #dbc.NavItem(dbc.NavLink(page['name'], href=page['path'])) for page in dash.page_registry.values()
    ]),
    
    # Adding full zotero library data to the browser session:
    dcc.Store(id="main_zotero_collection"),
    dcc.Store(id="all_zotero_collections"),

    dash.page_container

])

# Displaying the Help/Tutorial Tooltip:
@app.callback(
    Output("inital-tutorial-popup", "is_open"),
    Input("help_button", "n_clicks"),
    State("inital-tutorial-popup", "is_open")
)
def toggle_modal(n1, is_open):
    if n1 :
        return not is_open
    return is_open

# Main data extraction:
@app.callback(
    Output("main_zotero_collection", "data"),
    Output("all_zotero_collections", "data"),
    Output("status_button", "children"),
    Output("status_button", "color"),

    Input("zotero_library_id", "value"),
    Input("zotero_api_key", "value")
)
def store_zotero_library(library_id=None, api_key=None):
    """The method that uses the provided zotero library ID and API key to query 
    all zotero collections and write said collection to the browser session through
    the dcc.Store.

    It also returns the data that is used to the format the status checks assocaited with
    the API query being successful.

    Args:
        library_id (int): The zotero API user ID.
        
        api_key (str): The zotero API user key.

    Returns:
        lst: The JSON object of the zotero collection to be pushed to the Browser session.

        str: The strings used to update the status checks in the front-end

        int: The number of Zotero items collected.



    """ 
    # Using the Zotero API to query the full collection:
    if library_id and api_key != None:

        # Querying the Zotero API:
        data = get_zotero_collection(
            library_id=library_id,
            api_key=api_key)

        collection_data = get_all_collections(
            library_id=library_id,
            api_key=api_key)

        # If Zotero data is successfully queried, generating the status check values:
        if data != None and len(data) > 0:
            
            # Building the Button children components with a badge item: 
            color = "success"
            num_items = len(data)
            status = [
                "Data Found Successfully",
                dbc.Badge(num_items, color="light", text_color="primary", className="ms-1", style={"padding-left": "0.25rem"})
            ]

        return data, collection_data, status, color
    
    else:
        return None, None, "No Data Found", "danger"

#if __name__ == "__main__":
#    app.run_server(host="0.0.0.0", port=8050, debug=True)
