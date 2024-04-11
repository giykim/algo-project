import dash
import plotly.graph_objects as go
from dash import dcc, html


def dash_app(data):
    fig = go.Figure(
        data=[go.Candlestick(
        x=data["Date"],
        open=data["Open Price"],
        high=data["High Price"],
        low=data["Low Price"],
        close=data["Close Price"])]
    )

    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1("Palantir Prices"),
        dcc.Graph(
            id="candlestick",
            figure=fig
        )
    ])

    app.run_server(debug=True)