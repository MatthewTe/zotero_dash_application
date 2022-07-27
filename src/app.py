# Importing dash methods:
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

# Importing zotero data management APIs:
from utils import get_zotero_collection, get_all_collections

app = dash.Dash(
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions = True
)

# Main layout for the Dash Application:
app.layout = dbc.Container([
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
                    dbc.Col(dbc.Input(id="zotero_library_id", type="number", placeholder="Library ID")),
                    dbc.Col(dbc.Input(id="zotero_api_key", type="text", placeholder="API Key")),
                    dbc.Col(dbc.Button("No Data Found", color="danger", id="status_button")),
                    dbc.Col(html.H4(id="collection_value_count"))
                ])
            ]
        )
        #dbc.NavItem(dbc.NavLink(page['name'], href=page['path'])) for page in dash.page_registry.values()
    ]),
    
    # Adding full zotero library data to the browser session:
    dcc.Store(id="main_zotero_collection"),
    dcc.Store(id="all_zotero_collections"),

    dash.page_container

])
# Main data extraction:
@app.callback(
    Output("main_zotero_collection", "data"),
    Output("all_zotero_collections", "data"),
    Output("status_button", "children"),
    Output("status_button", "color"),
    Output("collection_value_count", "children"),

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

        str: The number of Zotero items collected.

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
            status = "Data Found Successfully"
            color = "success"
            num_items = f"{len(data)} Items Found!"

        return data, collection_data, status, color, num_items


if __name__ == "__main__":
    app.run_server(debug=True)