# Importing plotly method: 
import plotly.express as px
import plotly.graph_objects as go

def plot_collections_count_radar_figure(r, theta):
    """A method that uses plotly express to create, style and return a radar
    graph given a radial and theta values.

    Args: 

        r (lst): The list of radial values

        theta (lst): The list of theta values used for labelling

    Return:
        go.Figure: The Radial Graph.

    """
    # Creating the main radar graph image:
    radar_graph = go.Figure(data=go.Scatterpolar(r=r, theta=theta, fill="toself"))

    # Styling the Radar Graph:
    # Radrar styling that can be updated by modfying the layout of the figure object returned by the method:
    radar_graph.update_layout(
        polar=dict(
            bgcolor="rgba(255, 255, 255, 0.2)",
            radialaxis=dict(visible=False, showticklabels=False),
            angularaxis=dict(showticklabels=True)
        )
    )

    radar_graph.update_layout(polar_angularaxis_gridcolor="black")

    radar_graph.update

    return radar_graph