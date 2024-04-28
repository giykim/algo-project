import dash
import plotly.graph_objects as go
from dash import dcc, html


def dash_app(data, buy_orders, sell_orders):
    fig = go.Figure(
        data=[go.Candlestick(
        x=data["Date"],
        open=data["Open Price"],
        high=data["High Price"],
        low=data["Low Price"],
        close=data["Close Price"])]
    )

    buy_timestamps, buy_prices = zip(*buy_orders)
    sell_timestamps, sell_prices = zip(*sell_orders)

    fig.add_trace(
        go.Scatter(
            x=buy_timestamps,
            y=buy_prices,
            mode="markers",
            marker=dict(symbol="x", color="blue", size=5),
            name="Buy Orders"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=sell_timestamps,
            y=sell_prices,
            mode="markers",
            marker=dict(symbol="circle", color="red", size=5),
            name="Sell Orders"
        )
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