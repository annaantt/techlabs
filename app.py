import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input

data = pd.read_csv("testdb.csv")
data.rename(columns={'timestamp':'Date','numberoftweets':'Number of Tweets','sentiment': 'Sentiment','Close':'Price',}, inplace=True)
data["Date"] = pd.to_datetime(data["Date"], format="%Y-%m-%d")
data.sort_values("Date", inplace=True)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "deCrypto: Understand Your Cryptocurrencies!"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🚀", className="header-emoji"),
                html.H1(
                    children="deCrypto", className="header-title"
                ),
                html.P(
                    children="Analyze the behavior of cryptocurrencies"
                    " and the effect of social sentiment on Twitter",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Cryptocurrency", className="menu-title"),
                        dcc.Dropdown(
                            id="region-filter",
                            options=[
                                {"label": Cryptocurrency, "value": Cryptocurrency}
                                for Cryptocurrency in np.sort(data.Cryptocurrency.unique())
                            ],
                            value="Dogecoin",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.Date.min().date(),
                            max_date_allowed=data.Date.max().date(),
                            start_date=data.Date.min().date(),
                            end_date=data.Date.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="sentiment-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="mentions-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    [Output("price-chart", "figure"), Output("sentiment-chart", "figure"), Output("mentions-chart", "figure")],
    [
        Input("region-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)

def update_charts(Cryptocurrency, start_date, end_date):
    mask = (
        (data.Cryptocurrency == Cryptocurrency)
        & (data.Date >= start_date)
        & (data.Date <= end_date)
    )
    filtered_data = data.loc[mask, :]
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Price"],
                "type": "lines",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Price",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "xaxis": dict(type = "category"),
            "colorway": ["#17B897"],
            "xaxis": {"tickformat": "%y/%m/%d"},
        },
    }

    sentiment_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data["Sentiment"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "Twitter sentiment", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "xaxis": dict(type = "category"),
            "yaxis": {"fixedrange": True},
            "colorway": ["#17B897"],
            "xaxis": {"tickformat": "%y/%m/%d"},
        },
    }

    mentions_chart_figure = {
        "data": [
            {
                "x": filtered_data["Date"],
                "y": filtered_data['Number of Tweets'],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "Number of Tweets", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "xaxis": dict(type = "category"),
            "yaxis": {"fixedrange": True},
            "colorway": ["#17B897"],
            "xaxis": {"tickformat": "%y/%m/%d"},
        },
    }
    return price_chart_figure, sentiment_chart_figure, mentions_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)