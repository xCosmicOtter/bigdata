import dash
from dash import dcc, dash_table
from dash import html
import dash.dependencies as ddep
import pandas as pd
import sqlalchemy
from plotly.subplots import make_subplots
from datetime import datetime,timezone
import plotly.express as px
import plotly.graph_objs as go

external_stylesheets = [
    #'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://fonts.googleapis.com/css2?family=Material+Icons&display=block',
    'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0'
]

DATABASE_URI = 'timescaledb://ricou:monmdp@db:5432/bourse'    # inside docker
# DATABASE_URI = 'timescaledb://ricou:monmdp@localhost:5432/bourse'  # outisde docker
engine = sqlalchemy.create_engine(DATABASE_URI)

app = dash.Dash(__name__,  title="Bourse", suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)
server = app.server

graph_options = [
    {"label": html.Span([html.Img(src="/assets/line.png", height=30), html.Span("Ligne", style={'font-size': 15, 'padding-left': 10})]), "value": "line"},
    {"label": html.Span([html.Img(src="/assets/candlestick.png", height=30), html.Span("Bougies", style={'font-size': 15, 'padding-left': 10})]), "value": "candlestick"},
    {"label": html.Span([html.Img(src="/assets/area.png", height=30), html.Span("Aire", style={'font-size': 15, 'padding-left': 10})]), "value": "area"},
]

def getAllName():
    query = '''select name, symbol from companies;'''
    df = pd.read_sql_query(query,engine)
    name_symbol_tuple = list(zip(df['name'], df['symbol']))
    list_name_symbol = [ name + ' • ' + symbol for name, symbol in name_symbol_tuple]
    return list_name_symbol

app.layout = html.Div(children=[
    #Interval for live clock
    dcc.Interval(
            id='interval-component',
            interval=5000,  # Update every 5000 milliseconds (5 second)
            n_intervals=0
        ),
    html.Div(
        className="div-top-panel",
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
                    """
                ),
            ]),
        ]),
    html.Div(
        className="eight columns div-left-panel",
        children=[
        html.Div(
                    className='search',
                    children=[
                        html.I(className='material-icons', children='search'),
                        dcc.Dropdown(placeholder="Select a company", id='companyName',
                                    style={
                                        'flex': '1',
                                        'border-radius': '28px',
                                        'background': '#f6f6f6',
                                        'transition': 'box-shadow 0.25s',
                                        'border': 'none',     # Apply border style
                                        'outline': 'none',    # Apply outline style
                                        'background-color': 'transparent',  # Apply background color style
                                        'box-shadow': 'none',
                                        },
                                    options=getAllName(),
                                    multi=True,
                                    )
                    ]
                ),
        html.Br(),
        html.Div(id='dd-output-graph'),
        html.Div(className = "toolbar",children = [
            dcc.Tabs(
            colors={
                "primary": "#F1C086",
            },
            value='5J',
        children=[
            dcc.Tab(label='1J',className='tab-style',selected_className='tab-selected-style',value='1J'),
            dcc.Tab(label='5J',className='tab-style',selected_className='tab-selected-style',value='5J'),
            dcc.Tab(label='1M',className='tab-style',selected_className='tab-selected-style',value='1M'),
            dcc.Tab(label='3M',className='tab-style', selected_className='tab-selected-style',value='3M'),
            dcc.Tab(label='1A',className='tab-style', selected_className='tab-selected-style',value='1A'),
            dcc.Tab(label='2A',className='tab-style', selected_className='tab-selected-style',value='2A'),
            dcc.Tab(label='5A', className='tab-style-sep',selected_className='tab-selected-style',value='5A'),
        ]),
        html.Div(
            className='calendar',
            children=[
                dcc.DatePickerRange(
                    month_format='D/M/Y',
                    end_date_placeholder_text='JJ/MM/AAAA',
                    start_date_placeholder_text='JJ/MM/AAAA'
                )
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
                            value='line'
                        ),
                    ],
                ),
            ]
        ),

        html.Div(
            className='clock',
            id='clock',
        ),

        ]),
        html.Br(),
        html.Div(
            className='title',
            children=[
                dcc.Markdown(
                    """
                    Historical Data
                    """
                ),
            ]
        ),
        html.Div(
            className='table-daystocks',
            id = "table-daystocks"),

    ]),
    html.Div(
            className="three columns day-resume",
            children=[
                html.Div(
                    className="resume-text",
                    children=[
                        dcc.Markdown(
                                """
                                Day Summary
                                """)]),
                html.Div(
                    className="resume-box",
                    children=[
                        html.Div(
                        className="box",
                        children= [
                             html.I(className="material-symbols-outlined", children="calendar_month"),
                             dcc.Markdown(
                                """
                                Date
                                """ ),
                                html.Div(id = "last-date")
                        ]),
                        html.Div(
                        className="box",
                        children= [
                            html.I(className="material-symbols-outlined", children="monitoring"),
                             dcc.Markdown(
                                """
                                Volume
                                """ ),
                            html.Div(
                                id = "volume_last_day")
                        ])]
                ),
                 html.Div(
                    className="resume-box",
                    children=[
                        html.Div(
                        className="box",
                        children= [
                            html.I(className="material-symbols-outlined", children="event_available"),
                             dcc.Markdown(
                                """
                                Open
                                """ ),
                            html.Div(
                                id = "open_last_day")
                        ]),
                        html.Div(
                        className="box",
                        children= [
                            html.I(className="material-symbols-outlined", children="event_busy"),
                             dcc.Markdown(
                                """
                                Close
                                """ ),
                            html.Div(
                                id = "close_last_day")
                        ])]
                ),
                html.Div(
                    className="resume-box",
                    children=[
                        html.Div(
                        className="box",
                        children= [
                            html.I(className="material-symbols-outlined", children="trending_down"),
                             dcc.Markdown(
                                """
                                Low
                                """ ),
                            html.Div(
                                id = "low_last_day")
                        ]),
                        html.Div(
                        className="box",
                        children= [
                            html.I(className="material-symbols-outlined", children="trending_up"),
                             dcc.Markdown(
                                """
                                High
                                """ ),
                            html.Div(
                                id = "high_last_day")

                        ])]
                ),

            ])])

        # dcc.Textarea(
        # id='sql-query',
        # value='''
        #    SELECT * FROM pg_catalog.pg_tables
        #        WHERE schemaname != 'pg_catalog' AND
        #                schemaname != 'information_schema';
        # ''',
        # style={'width': '100%', 'height': 100},
        # ),
        # html.Button('Execute', id='execute-query', n_clicks=0),
        # html.Div(id='query-result'),

@app.callback(
    ddep.Output('clock', 'children'),
    [ddep.Input('interval-component', 'n_intervals')]
)
def update_clock(n_intervals):

    local_time = datetime.now().strftime("%H:%M:%S")
    utc_offset = datetime.now(timezone.utc).astimezone().utcoffset()

    # Convert the offset to hours
    utc_offset_hours = utc_offset.total_seconds() / 3600

    return f"{local_time} (UTC+{int(utc_offset_hours)})"



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
    [ddep.Output('dd-output-graph', 'children'),ddep.Output('table-daystocks','children'),ddep.Output('last-date','children'),ddep.Output('high_last_day','children'),ddep.Output('low_last_day','children'),ddep.Output('close_last_day','children'),ddep.Output('open_last_day','children'),ddep.Output('volume_last_day','children')],

    [ddep.Input('companyName', 'value'),ddep.Input('graph-type-dropdown', 'value')]
)
def display_graph_by_name(value,graphType):
    if (value != None):
        value = value.split(" • ")[1]
        query=f"SELECT date, open, high, low, close, volume FROM daystocks where cid = (SELECT id from companies where symbol = '{value}') order by date"
        df = pd.read_sql_query(query,engine)
        if (graphType == 'line'):
            # Création des subplots avec titres et espacement vertical ajusté
            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True,
                subplot_titles=('Évolution des prix des actions', None),
                vertical_spacing=0.01,
                row_heights=[0.8, 0.2]
            )

            # Ajout des données High avec une ligne
            fig.add_trace(
                go.Scatter(x=df['date'], y=df['high'], mode='lines', name='High', line=dict(color='#F1C086')),
                row=1, col=1
            )

            # Ajout des données Volume avec un graphique à barres
            fig.add_trace(
                go.Bar(x=df['date'], y=df['volume'], name='Volume', marker_color='#F1C086'),
                row=2, col=1
            )

            # Ajout des titres et étiquettes des axes
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="Prix des actions", row=1, col=1, title_standoff=25)
            fig.update_yaxes(title_text="Volume", row=2, col=1)

            # Ajout d'un titre général au graphique
            fig.update_layout(
                title_text="Analyse des prix des actions et du volume",
                template="plotly_dark",
                paper_bgcolor='#131312',  # Couleur de fond du graphique
                plot_bgcolor='#131312',
                font=dict(color='rgba(255, 255, 255, 0.7)')
            )

            # Mise à jour des ticks des axes x pour les afficher à l'extérieur et espacement cohérent
            fig.update_xaxes(
                ticks="outside",
                ticklabelmode="period",
                tickcolor="black",
                ticklen=10,
                row=2, col=1
            )

            # Ajout d'une légende
            fig.update_layout(legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))

            fig.update_layout(hovermode="x unified")


        if (graphType == 'candlestick'):
            trace = go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
            )

            # Create layout
            layout = go.Layout(
                title='Stock Prices',
                xaxis=dict(title='Date'),
                yaxis=dict(title='Price')
            )

            # Create figure
            fig = go.Figure(data=[trace], layout=layout)

        table_daystocks = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df.columns],
            page_size=15
        )
        return dcc.Graph(figure=fig),table_daystocks,dcc.Markdown(f"{df['date'].iloc[-1].date()}"),dcc.Markdown(f"{df['high'].iloc[-1]}"),dcc.Markdown(f"{df['low'].iloc[-1]}"),dcc.Markdown(f"{df['close'].iloc[-1]}"),dcc.Markdown(f"{df['open'].iloc[-1]}"),dcc.Markdown('''''')
    return dcc.Graph(),dcc.Markdown('''No Data Found''', style={'display':'inline-block', 'textAlign':'left'}), dcc.Markdown(''''''),dcc.Markdown(''''''),dcc.Markdown(''''''),dcc.Markdown(''''''),dcc.Markdown(''''''),dcc.Markdown('''''')


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