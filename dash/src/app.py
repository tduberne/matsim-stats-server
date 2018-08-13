import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas.io.sql as psql
import plotly.graph_objs as go
import psycopg2 as pg
from dash.dependencies import Output, Input
from flask_caching import Cache
import os

app = dash.Dash()

# Setup Redis caching.
cache = Cache()
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    # Keep data cached for 5 minutes. This basically corresponds to the time after which changes in the database
    # become available (at the cost of more expensive queries)
    # Adding an "invalidate cache" button would be possible, but would make the code messier for a rather limited need...
    # For testing timeout can be reduced using the environment variable (a few seconds allow at least to only compute
    # dataset once for several graphs at filter update
    'CACHE_DEFAULT_TIMEOUT': os.getenv('REDIS_CACHE_DEFAULT_TIMEOUT', 300),
    'CACHE_KEY_PREFIX': 'dash_',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 1,
    'CACHE_REDIS_URL': 'redis://redis:6379/1'}
cache.init_app(app.server, config=CACHE_CONFIG)


@cache.memoize()
def global_store():
    """Gets the data, possibly filtered by the parameters.
       Data is cached using Redis, avoiding to recompute already known data as much as possible."""
    connection = pg.connect(host="postgres", database="matsim_stats_db",
                            user="postgres", password="password")

    return psql.read_sql("SELECT * FROM usage_stats", connection)


# Defining this in a function allows to update the layout at page load.
# This is important, as this for instance allows to update the values in dropdown based on what is
# available in the database.
def serve_layout():
    return html.Div(children=[
        html.H1(children='MATSim Usage Statistics Dashboard'),

        html.Div(children='''
            Summary of data collected about MATSim usage. Have fun!
        '''),

        dcc.Dropdown(
            id='dropdown',
            options=[{'label': i, 'value': i} for i in global_store().os_name.unique().tolist()],
            value='a'
        ),

        dcc.Graph(id='memory-graph'),

        # hidden divs used to "signal" data changes to callbacks
        # They store value of various dropdowns etc, but provide them only after data was queried and cached.
        html.Div(id='signal', style={'display': 'none'})
    ])


app.layout = serve_layout


@app.callback(Output('signal', 'children'), [Input('dropdown', 'value')])
def compute_value(value):
    # compute value and send a signal when done
    global_store()
    return value


@app.callback(Output('memory-graph', 'figure'),
              [Input('signal', 'children')])
def memory_graph(value):
    d = global_store()
    return go.Scatter(
        x=d.population_size,
        y=d.peak_heapmb,
        mode='markers'
    )


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
