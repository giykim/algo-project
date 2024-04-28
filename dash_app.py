import dash
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go


class App:
    def __init__(self, data, blotter, portfolio_stats):
        self.data = data
        self.blotter = blotter
        self.portfolio_stats = [portfolio_stats]

        self.app = dash.Dash(__name__)
        self.init_callbacks()

    def run_app(self):
        self.app.layout = html.Div([
            # Main Selector
            html.H1("Palantir Prices"),
            dcc.Dropdown(
                id="Dropdown",
                options=[
                    {"label": "Candlestick", "value": "Candlestick"},
                    {"label": "Blotter", "value": "Blotter"},
                    {"label": "Stats", "value": "Stats"},
                ],
                value="Candlestick",
                style={'margin-top': '20px',
                       'margin-bottom': '20px'},
            ),
            # Candlestick Graph
            html.Div(id="Candlestick",
                     children=[
                         dcc.Checklist(
                             id="ToggleOrders",
                             options=[
                                 {"label": "Prices", "value": "Prices"},
                                 {"label": "Buy Orders", "value": "Buy Orders"},
                                 {"label": "Sell Orders", "value": "Sell Orders"}
                             ],
                             value=["Prices"],
                             labelStyle={"display": "inline-block"},
                         ),
                         dcc.Graph(
                             id="CandlestickGraph",
                             figure=self.candlestick(["Prices",
                                                      "Buy Orders",
                                                      "Sell Orders",
                                                      ]),
                         )
                     ]),
            # Matched Blotter
            html.Div(id="Blotter",
                     children=[
                         dash_table.DataTable(
                             id="BlotterTable",  # ID for the table component
                             data=self.blotter.to_dict('records'),  # Convert DataFrame to dictionary format
                             columns=[{"name": i, "id": i} for i in self.blotter.columns],  # Column definitions
                             page_size=10,  # Number of rows per page
                        )
                     ]),
            # Statistics
            html.Div(id="Stats",
                     children=[
                         dash_table.DataTable(
                             id="StatsTable",  # ID for the table component
                             data=self.portfolio_stats,
                             columns=[{"name": key, "id": key} for key in self.portfolio_stats[0].keys()],
                             page_size=10,  # Number of rows per page
                         )
                     ]),
        ])

        self.app.run_server(debug=True)

    def candlestick(self, selected):
        if "Prices" in selected:
            fig = go.Figure(
                data=[
                    go.Candlestick(
                    x=self.data["Date"],
                    open=self.data["Open Price"],
                    high=self.data["High Price"],
                    low=self.data["Low Price"],
                    close=self.data["Close Price"],
                    name = "Price",
                    )
                ]
            )
        else:
            fig = go.Figure()


        # Control margins to keep a consistent layout
        fig.update_layout(
            margin=dict(l=50, r=50, t=50, b=50),  # Consistent margins
            showlegend=False  # Show legend if needed
        )

        buy_timestamps = self.blotter["EntryTimestamp"]
        buy_prices = self.blotter["EntryPrice"]
        sell_timestamps = self.blotter["ExitTimestamp"]
        sell_prices = self.blotter["ExitPrice"]

        if "Buy Orders" in selected:
            fig.add_trace(
                go.Scatter(
                    x=buy_timestamps,
                    y=buy_prices,
                    mode="markers",
                    marker=dict(symbol="x", color="gray", size=5),
                    name="Buy Orders"
                )
            )

        if "Sell Orders" in selected:
            fig.add_trace(
                go.Scatter(
                    x=sell_timestamps,
                    y=sell_prices,
                    mode="markers",
                    marker=dict(symbol="circle", color="gray", size=5),
                    name="Sell Orders"
                )
            )

        return fig

    def init_callbacks(self):
        @self.app.callback(
            Output("CandlestickGraph", "figure"),
            [Input("ToggleOrders", "value")]
        )
        def update_figure(selected_traces):
            return self.candlestick(selected_traces)

        @self.app.callback(
            [
                Output("Candlestick", "style"),
                Output("Blotter", "style"),
                Output("Stats", "style"),
            ],
            [
                Input('Dropdown', 'value'),
            ]
        )
        def toggle_checklist(selected_value):
            show = {"display": "block"}
            hide = {"display": "none"}

            candlestick = hide
            blotter = hide
            stats = hide

            if selected_value == 'Candlestick':
                candlestick = show
            elif selected_value == "Blotter":
                blotter = show
            elif selected_value == "Stats":
                stats = show

            return candlestick, blotter, stats
