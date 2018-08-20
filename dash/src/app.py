import re

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas.io.sql as psql
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import psycopg2 as pg
from dash.dependencies import Output, Input, State
from flask_caching import Cache
import os
import logging
import datetime as dt

from werkzeug.contrib.fixers import ProxyFix

app = dash.Dash(__name__, url_base_pathname='/dashboard')
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
filter_states = [State('os-name-dropdown', 'value'),
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

    return psql.read_sql("""SELECT *
                            FROM usage_stats
                            WHERE os_name IN {os_name}
                            AND os_arch IN {os_arch}
                            AND matsim_version IN {matsim_version}
                            AND jvm_vendor IN {jvm_vendor}
                            AND jvm_version IN {jvm_version}""".format(
        os_name=to_sql_list(os_name),
        os_arch=to_sql_list(os_arch),
        matsim_version=to_sql_list(matsim_version),
        jvm_vendor=to_sql_list(jvm_vendor),
        jvm_version=to_sql_list(jvm_version)
    ), connection)


@cache.memoize()
def global_store_guice(os_name, os_arch, matsim_version, jvm_vendor, jvm_version):
    """Gets the data, possibly filtered by the parameters.
       Data is cached using Redis, avoiding to recompute already known data as much as possible."""
    connection = pg.connect(host="postgres", database="matsim_stats_db",
                            user="postgres", password="password")

    return psql.read_sql("""SELECT DISTINCT usage_stats.id, guice_binding_data.type
                            FROM usage_stats 
                            JOIN guice_binding_data ON usage_stats.id=guice_binding_data.usage_data_id
                            AND os_name IN {os_name}
                            AND os_arch IN {os_arch}
                            AND matsim_version IN {matsim_version}
                            AND jvm_vendor IN {jvm_vendor}
                            AND jvm_version IN {jvm_version}
                            """.format(
        os_name=to_sql_list(os_name),
        os_arch=to_sql_list(os_arch),
        matsim_version=to_sql_list(matsim_version),
        jvm_vendor=to_sql_list(jvm_vendor),
        jvm_version=to_sql_list(jvm_version)
    ), connection)


def to_sql_list(string_list):
    placeholders = ', '.join(['\'%s\''] * len(string_list))
    return "(" + (placeholders % tuple(string_list)) + ")"


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


def Container(fluid=True, **kwargs):
    if fluid:
        return html.Div(className='container-fluid', **kwargs)
    return html.Div(className='container', **kwargs)


def Row(**kwargs):
    return html.Div(className='row', **kwargs)


def Col(className='col', **kwargs):
    return html.Div(className=className, **kwargs)


def dropdown(name, key):
    return Container(
        children=dcc.Dropdown(
            id=name,
            options=[{'label': i, 'value': i} for i in key_store()[key]],
            value=key_store()[key],
            multi=True)
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

        html.H2(children='Data Filters'),

        Container(
            children=[
                Row(children=[
                    Col('col-1', children='OS Name: '),
                    Col(children=dropdown('os-name-dropdown', 'os_name'))]),
                Row(children=[
                    Col('col-1', children='OS Arch: '),
                    Col(children=dropdown('os-arch-dropdown', 'os_arch'))]),
                Row(children=[
                    Col('col-1', children='MATSim v: '),
                    Col(children=dropdown('matsim-version-dropdown', 'matsim_version'))]),
                Row(children=[
                    Col('col-1', children='JVM vendor: '),
                    Col(children=dropdown('jvm-vendor-dropdown', 'jvm_vendor'))]),
                Row(children=[
                    Col('col-1', children='JVM Version: '),
                    Col(children=dropdown('jvm-version-dropdown', 'jvm_version'))]),
            ]),

        html.Button('Apply Filters', id='filter-button'),

        html.H2(children='Software Versions'),

        Container(
            children=[
                Row(children=[
                    Col(children=[
                        html.H3("Runs over time"),
                        dcc.Graph(id='time-graph')] ),
                    Col(children=[
                        html.H3("Packages bound by Guice"),
                        dcc.Graph(id='guice-graph')] ),
                    Col(children=[
                        html.H3("Server locations"),
                        dcc.Graph(id='run-map')] )
                ])
            ]
        ),

        html.H2(children='MATSim Features Enabled'),

        html.H2(children='Memory Consumption'),

        dcc.Graph(id='memory-graph'),

        # hidden divs used to "signal" data changes to callbacks
        # They store value of various dropdowns etc, but provide them only after data was queried and cached.
        html.Div(id='signal', style={'display': 'none'}),
        html.Div(id='signal-guice', style={'display': 'none'})
    ])


app.layout = serve_layout


@app.callback(Output('signal', 'children'),
              [Input('filter-button', 'n_clicks')],
              filter_states)
def compute_value(n_clicks, *args):
    # compute value and send a signal when done
    global_store(*args)
    return n_clicks


@app.callback(Output('signal-guice', 'children'),
              [Input('filter-button', 'n_clicks')],
              filter_states)
def compute_guice_value(n_clicks, *args):
    # compute value and send a signal when done
    global_store_guice(*args)
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


@app.callback(Output('time-graph', 'figure'),
              [Input('signal', 'children')],
              filter_states)
def memory_graph(signal, *args):
    d = global_store(*args)\
        .assign(count=0,
               day=lambda df: df.date\
                    .astype(dt.datetime)\
                    .apply(lambda d: d.date())\
                    .astype(np.datetime64))\
        [['day', 'count']]\
        .groupby('day')\
        .count()\
        .reset_index()

    all = pd.DataFrame({
        'day': pd.date_range(d.day.min() - np.timedelta64(1,'D'), d.day.max()).to_series()
    }).merge(d, 'outer', 'day', )\
        .fillna(0)

    return go.Figure(
        data=[go.Scatter(
            x=all.day,
            y=all['count']
        )]
    )


@app.callback(Output('run-map', 'figure'),
              [Input('signal', 'children')],
              filter_states)
def client_map(signal, *args):
    d = global_store(*args)

    return go.Figure(
        data=[go.Scattergeo(
            lon=d.x,
            lat=d.y
        )],
        layout=go.Layout(
            geo={
                'showland': True,
                'showcountries': True
            }
        )
    )

# regular expression that is able to get all java classes from a generic type
java_class_re = re.compile('[^<>\s]+')
contrib_re = re.compile('org\.matsim\.contrib\.[^.]+')
domain_re = re.compile('^[^.]+.?[^.]+')


def get_relevant_package(pkg_name):
    if pkg_name.startswith('org.matsim.contrib'):
        return contrib_re.findall(pkg_name)[0]
    domain = domain_re.findall(pkg_name)
    if len(domain) == 0:
        # happens for instance with ? in generics
        return np.nan
    return domain[0]


@app.callback(Output('guice-graph', 'figure'),
              [Input('signal-guice', 'children')],
              filter_states)
def memory_graph(signal, *args):
    d = global_store_guice(*args)
    counts = d.set_index('id').type \
        .apply(java_class_re.findall) \
        .apply(pd.Series)\
        .unstack()\
        .dropna()\
        [lambda x: x != '']\
        .apply(get_relevant_package) \
        .reset_index(level=1)\
        .drop_duplicates()\
        .sort_values(by=0)\
        .groupby(0)\
        .count()

    return go.Figure(
        data=[go.Bar(
            y=counts.index,
            x=counts.id,
            orientation='h'
        )]
    )



app.css.append_css({
    'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css'
})


app.css.append_css({
    'external_url': 'http://www.matsim.org/lib/style.css'
})

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>MATSim Usage Stats</title>
        <link rel='icon' href='http://www.matsim.org/lib/favicon.ico' sizes='16x16' type='image/vnd.microsoft.icon'>
        {%css%}
    </head>
    <body>
        <header>
        <nav class="navbar navbar-default navbar-fixed-top">
        <div class="container">
          <div class="navbar-brand page-scroll title-link"><a href='http://www.matsim.org/'>
                  <img class="banner-logo" src="http://www.matsim.org/images/matsim-logo-white.png" alt="matsim logo" /></a></div>
            <!-- Collect the nav links, forms, and other content for toggling -->
            <!--
            <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">

               <ul class="nav navbar-nav navbar-right">
                  {% for item in site.data.links.nav_links %}
                   <li class="li-header"><a class="page-scroll" href="{{item[1]}}">{{item[0]}}</a></li>
                  {% endfor %}
               </ul>

            </div>
            -->
            <!-- /.navbar-collapse -->
        </div>
        <!-- /.container-fluid -->
    </nav>
    </header>
        {%app_entry%}
        <footer>
         <div id="footer_wrap">
            <footer class="footer" id="footer_content">
                  <p>&copy; 2018 <a href="{{site.url}}/about-us">MATSim Community</a></p>
              </footer>
            </div>
            {%config%}
            {%scripts%}
        </footer>
    </body>
</html>
'''

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

