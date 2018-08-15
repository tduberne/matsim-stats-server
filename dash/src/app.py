import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas.io.sql as psql
import plotly.graph_objs as go
import psycopg2 as pg
from dash.dependencies import Output, Input, State
from flask_caching import Cache
import os
import logging

from werkzeug.contrib.fixers import ProxyFix

app = dash.Dash(__name__)
app.server.secret_key = os.environ.get('SECRET_KEY', 'default-value-used-in-development')

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


# Store the "State" objects in the order they appear in the arguments list.
# This allows to only have to modify this list and the global store when adding filters,
# instead of all possible callbacks
filter_states = [State('os-name-dropdown', 'value' ),
                 State('os-arch-dropdown', 'value'),
                 State('matsim-version-dropdown', 'value'),
                 State('jvm-vendor-dropdown', 'value'),
                 State('jvm-version-dropdown', 'value')]


@cache.memoize()
def global_store(os_name, os_arch, matsim_version, jvm_vendor, jvm_version):
    """Gets the data, possibly filtered by the parameters.
       Data is cached using Redis, avoiding to recompute already known data as much as possible."""
    connection = pg.connect(host="postgres", database="matsim_stats_db",
                            user="postgres", password="password")

    # TODO apply filter
    return psql.read_sql("SELECT * FROM usage_stats", connection)


@cache.memoize()
def key_store():
    """Gets the data, possibly filtered by the parameters.
       Data is cached using Redis, avoiding to recompute already known data as much as possible."""
    connection = pg.connect(host="postgres", database="matsim_stats_db",
                            user="postgres", password="password")

    # get a table with unique combinations of keys used for filtering.
    # This will work as long as there are not too many combinations possible
    def uniques(column):
        return psql.read_sql("""SELECT DISTINCT {column}
                                FROM usage_stats""".format(column=column), connection)[column].tolist()
    return {
        "os_name": uniques("os_name"),
        "os_arch": uniques("os_arch"),
        "matsim_version": uniques("matsim_version"),
        "jvm_vendor": uniques("jvm_vendor"),
        "jvm_version": uniques("jvm_version")
    }


def dropdown(name, key):
    return dcc.Dropdown(
        id=name,
        options=[{'label': i, 'value': i} for i in key_store()[key]],
        value=key_store()[key],
        multi=True
    )


# Defining this in a function allows to update the layout at page load.
# This is important, as this for instance allows to update the values in dropdown based on what is
# available in the database.
def serve_layout():
    return html.Div(children=[
        html.H1(children='MATSim Usage Statistics Dashboard'),

        html.Div(children='''
            Summary of data collected about MATSim usage. Have fun!
        '''),

        dropdown('os-name-dropdown', 'os_name'),
        dropdown('os-arch-dropdown', 'os_arch'),
        dropdown('matsim-version-dropdown', 'matsim_version'),
        dropdown('jvm-vendor-dropdown', 'jvm_vendor'),
        dropdown('jvm-version-dropdown', 'jvm_version'),

        html.Button('Apply Filters', id='filter-button'),


        dcc.Graph(id='memory-graph'),

        # hidden divs used to "signal" data changes to callbacks
        # They store value of various dropdowns etc, but provide them only after data was queried and cached.
        html.Div(id='signal', style={'display': 'none'})
    ])


app.layout = serve_layout

@app.callback(Output('signal', 'children'),
              [Input('filter-button', 'n_clicks')],
              filter_states)
def compute_value(n_clicks, *args):
    # compute value and send a signal when done
    global_store(*args)
    return n_clicks


@app.callback(Output('memory-graph', 'figure'),
              [Input('signal', 'children')],
              filter_states)
def memory_graph(signal, *args):
    d = global_store(*args)
    return go.Figure(
        data=[go.Scatter(
            x=d.population_size,
            y=d.peak_heapmb,
            mode='markers'
        )]
    )


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
else:
    # make Flask log messages visible on the console when running through gunicorn
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.server.logger.handlers = gunicorn_logger.handlers
    app.server.logger.setLevel(gunicorn_logger.level)

    # To make server understand the "Forwarded" header set by nginx when serving the app somewhere else than the root.
    # Otherwise, the app does not manage to link to other parts of itself and crashes.
    app.server.wsgi_app = ProxyFix(app.server.wsgi_app)
