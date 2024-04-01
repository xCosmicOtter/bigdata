import dash
from dash import dcc
from dash import html
import dash.dependencies as ddep
import pandas as pd
import sqlalchemy

import plotly.express as px

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

DATABASE_URI = 'timescaledb://ricou:monmdp@db:5432/bourse'    # inside docker
# DATABASE_URI = 'timescaledb://ricou:monmdp@localhost:5432/bourse'  # outisde docker
engine = sqlalchemy.create_engine(DATABASE_URI)

query='''SELECT date, high from daystocks where cid = 105 order by date'''
df = pd.read_sql_query(query,engine)

fig = px.line(df, x='date', y=['high'], title='Stock Prices')

app = dash.Dash(__name__,  title="Bourse", suppress_callback_exceptions=True) # , external_stylesheets=external_stylesheets)
server = app.server

graph_options = [
    {"label": html.Span([html.Img(src="/assets/line.png", height=30), html.Span("Ligne", style={'font-size': 15, 'padding-left': 10})]), "value": "line"},
    {"label": html.Span([html.Img(src="/assets/candlestick.png", height=30), html.Span("Bougies", style={'font-size': 15, 'padding-left': 10})]), "value": "candlestick"},
    {"label": html.Span([html.Img(src="/assets/area.png", height=30), html.Span("Aire", style={'font-size': 15, 'padding-left': 10})]), "value": "area"},
]

app.layout = html.Div(children=[
    html.Div(
        className="three columns div-left-panel",
        children=[
        # Div for Left Panel App Info
        html.Div(
            children=[
                html.Div(
                    className= "logo-text",
                    children = [
                        html.Img(
                            className="logo",
                            src=app.get_asset_url("analytics.png"),
                        ),
                        dcc.Markdown(
                            """Analytics""")
                    ]
                )]
        ),
        html.Div(
            className = "project-description",
            children = [
                dcc.Markdown(
                    """
                    Projet Python Big Data for EPITA.

                    [Source Code](https://github.com/xCosmicOtter/bigdata.git)
                    """
                ),
            ]),
        ]),
    html.Div(
        className="nine columns div-right-panel",
        children=[
        html.Div(
                className='flex-container',
                children=[
                    html.Div(
                        className='search-bar',
                        children=[
                            dcc.Dropdown(['NYC', 'MTL', 'SF'], placeholder="Select a company", id='companyName'),
                            html.Div(id='dd-output-graph')
                        ]
                    ),
                    html.Div(
                        className='chart-options',
                        children=[
                            # Image cliquable pour ouvrir la liste déroulante
                            html.Img(src="/assets/line.png", id="chart-img", height=50, style={'cursor': 'pointer'}),
                            html.Div(
                                id="submenu",
                                className="not-visible",
                                children=[
                                    # Liste déroulante d'options de type de graphique
                                    dcc.RadioItems(
                                        id='graph-type-dropdown',
                                        options=graph_options,
                                    ),
                                ],
                            ),
                            # Div pour afficher le type de graphique sélectionné
                            html.Div(id='selected-graph-type')
                        ]
                    )
                ]
            ),
        dcc.Tabs(
            colors={
                "primary": "#119DFF",
            },
        children=[
            dcc.Tab(label='1J',className='tab-style-left',selected_className='tab-selected-style',children=[
                dcc.Graph(
                    figure=fig
                )
            ]),

            dcc.Tab(label='5J',className='tab-style-sep',selected_className='tab-selected-style', children=[
                dcc.Graph(
                    figure={
                        'data': [
                            {'x': [1, 2, 3], 'y': [1, 4, 1],
                                'type': 'bar', 'name': 'SF'},
                            {'x': [1, 2, 3], 'y': [1, 2, 3],
                            'type': 'bar', 'name': 'Montréal'},
                        ]
                    }
                )
            ]),
            dcc.Tab(label='1M',className='tab-style',selected_className='tab-selected-style',children=[
                dcc.Graph(
                    figure={
                        'data': [
                            {'x': [1, 2, 3], 'y': [2, 4, 3],
                                'type': 'bar', 'name': 'SF'},
                            {'x': [1, 2, 3], 'y': [5, 4, 3],
                            'type': 'bar', 'name': 'Montréal'},
                        ]
                    }
                )
            ]),
            dcc.Tab(label='3M',className='tab-style', selected_className='tab-selected-style',children=[
                dcc.Graph(
                    figure={
                        'data': [
                            {'x': [1, 2, 3], 'y': [2, 4, 3],
                                'type': 'bar', 'name': 'SF'},
                            {'x': [1, 2, 3], 'y': [5, 4, 3],
                            'type': 'bar', 'name': 'Montréal'},
                        ]
                    }
                )
            ]),
            dcc.Tab(label='6M', className='tab-style-sep',selected_className='tab-selected-style',children=[
                dcc.Graph(
                    figure={
                        'data': [
                            {'x': [1, 2, 3], 'y': [2, 4, 3],
                                'type': 'bar', 'name': 'SF'},
                            {'x': [1, 2, 3], 'y': [5, 4, 3],
                            'type': 'bar', 'name': 'Montréal'},
                        ]
                    }
                )
            ]),
            dcc.Tab(label='1A',className='tab-style', selected_className='tab-selected-style',children=[
                dcc.Graph(
                    figure={
                        'data': [
                            {'x': [1, 2, 3], 'y': [2, 4, 3],
                                'type': 'bar', 'name': 'SF'},
                            {'x': [1, 2, 3], 'y': [5, 4, 3],
                            'type': 'bar', 'name': 'Montréal'},
                        ]
                    }
                )
            ]),
            dcc.Tab(label='2A',className='tab-style', selected_className='tab-selected-style',children=[
                dcc.Graph(
                    figure={
                        'data': [
                            {'x': [1, 2, 3], 'y': [2, 4, 3],
                                'type': 'bar', 'name': 'SF'},
                            {'x': [1, 2, 3], 'y': [5, 4, 3],
                            'type': 'bar', 'name': 'Montréal'},
                        ]
                    }
                )
            ]),
            dcc.Tab(label='5A', className='tab-style-right',selected_className='tab-selected-style',children=[
                dcc.Graph(
                    figure={
                        'data': [
                            {'x': [1, 2, 3], 'y': [2, 4, 3],
                                'type': 'bar', 'name': 'SF'},
                            {'x': [1, 2, 3], 'y': [5, 4, 3],
                            'type': 'bar', 'name': 'Montréal'},
                        ]
                    }
                )
            ]),
        ])]),
        dcc.Textarea(
        id='sql-query',
        value='''
            SELECT * FROM pg_catalog.pg_tables
                WHERE schemaname != 'pg_catalog' AND
                        schemaname != 'information_schema';
        ''',
        style={'width': '100%', 'height': 100},
        ),
        html.Button('Execute', id='execute-query', n_clicks=0),
        html.Div(id='query-result'),
])

@app.callback(
    ddep.Output("submenu", "className"),
    [ddep.Input("chart-img", "n_clicks"),
     ddep.Input('graph-type-dropdown', 'value')],
    [ddep.State("submenu", "className")]
)
def toggle_submenu(n_clicks, selected_value, class_name):
    # Toggle the submenu visibility when the chart image is clicked
    if selected_value and class_name == "visible":
        return "not-visible"
    if n_clicks and class_name == "not-visible":
        return "visible"
    else:
        return "not-visible"

@app.callback(
    ddep.Output('chart-img', 'src'),
    [ddep.Input('graph-type-dropdown', 'value')]
)
def change_image(selected_value):
    if selected_value == 'line':
        return "/assets/line.png"
    elif selected_value == 'candlestick':
        return "/assets/candlestick.png"
    elif selected_value == 'area':
        return "/assets/area.png"
    else:
        return "/assets/line.png"

@app.callback(
    ddep.Output('selected-graph-type', 'children'),
    [ddep.Input('graph-type-dropdown', 'value')]
)
def display_selected_graph_type(selected_value):
    if selected_value:
        return f"Type de graphique sélectionné : {selected_value.capitalize()}"
    else:
        return ""


@app.callback(
    ddep.Output('dd-output-graph', 'children'),
    ddep.Input('companieName', 'value')
)
def update_output(value):
    return f'{value} selected'

@app.callback( ddep.Output('query-result', 'children'),
               ddep.Input('execute-query', 'n_clicks'),
               ddep.State('sql-query', 'value'),
             )

def run_query(n_clicks, query):
    if n_clicks > 0:
        try:
            result_df = pd.read_sql_query(query, engine)
            return html.Pre(result_df.to_string())
        except Exception as e:
            return html.Pre(str(e))
    return "Enter a query and press execute."

if __name__ == '__main__':
    app.run(debug=True, port=8051)