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
from datetime import datetime, timedelta

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
            interval=5000,  # Update every 5000 milliseconds (5 seconds)
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
            id='search',
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
                            ),
            ]
        ),
        html.Br(),
        dcc.Checklist(
            options=['CompA', 'CompB', 'PEAPME', 'AMSTERDAM'],
            inline=True
        ),
        html.Br(),
        html.Div(className = "card card-shadow",
                 children = [
                    html.Div(id='dd-output-graph'),
                    html.Div(className = "toolbar",
                             children = [
                                html.Div(className= "toolbar-left",
                                        children = [
                                                dcc.Tabs(
                                                    id = "tabs-day",
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
                                                            month_format='DD/MM/YYYY',
                                                            end_date_placeholder_text='JJ/MM/AAAA',
                                                            start_date_placeholder_text='JJ/MM/AAAA',
                                                            display_format='DD/MM/YYYY'
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
                                        ]),

                                html.Div(
                                    className = 'toolbar-right',
                                    children = [
                                        html.Div(
                                            id='clock',
                                            className='clock'
                                        ),
                                        html.Button('Log', id='log-button',className='toggle-button toggle-off')

                                ]),

                            ]
                        )]
        ),

        html.Br(),
        html.Div(id = "title-table-daystocks",className="card card-shadow", children = [
            html.Div(
            className='historical-text',
            children=[
                dcc.Markdown(
                    """
                    Historical Data
                    """
                ),
                ]),
                dcc.Tabs(
                    className='table-daystocks',
                    id = "table-daystocks",
                    colors={
                        "primary": "#F1C086",
                    },
                children=[])
        ]),

        ]),
    html.Div(
            className="three columns day-resume",
            children=[
                html.Div(className = "card card-shadow",
                         id = "resume-text",
                         children = [
                            html.Div(
                                className="resume-text",
                                children=[
                                            dcc.Markdown(
                                            """
                                            Day Summary
                                            """)
                                        ]),
                            dcc.Tabs(
                                    className="tabs-summary",
                                    id = "tabs-summary",
                                    colors={
                                        "primary": "#F1C086",
                                    },
                                    vertical=True,
                            children=[])
                            ])


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
    ddep.Output('search', 'style'),
    [ddep.Input('companyName', 'value')]
)
def update_search_bar_height(selected_items):
    if (selected_items != None):
        row = len(selected_items) // 3
        height = 15 + row  * 35  # Adjust as needed
        return {'height': f'{height}px'}

@app.callback(
    [ddep.Output('dd-output-graph', 'children'),
     ddep.Output('table-daystocks','children'),
     ddep.Output('table-daystocks', 'value'),
     ddep.Output('title-table-daystocks','style'),
     ddep.Output('resume-text','style'),
     ddep.Output('tabs-summary', 'children'),
     ddep.Output('tabs-summary', 'value'),
     ddep.Output('log-button', 'className'),],


    [ddep.Input('companyName', 'value'),
     ddep.Input('log-button', 'n_clicks'),
     ddep.Input('graph-type-dropdown', 'value'),
     ddep.Input('tabs-day','value')],

    [ddep.State('log-button', 'className')]
)
def display_graph_and_tabs(values, n_clicks, graphType, time_period, class_name):
    if n_clicks:
        if 'toggle-on' in class_name:
            class_name = 'toggle-button toggle-off'
        else:
            class_name = 'toggle-button toggle-on'

    def generate_query(symbol, time_period):
        last_day_2023 = datetime(2023, 12, 31)

        if time_period == '1J':
            start_date = last_day_2023 - timedelta(days=1)
        elif time_period == '5J':
            start_date = last_day_2023 - timedelta(weeks=1)
        elif time_period == '1M':
            start_date = last_day_2023 - timedelta(days=30)
        elif time_period == '3M':
            start_date = last_day_2023 - timedelta(days=90)
        elif time_period == '1A':
            start_date = last_day_2023 - timedelta(days=365)
        elif time_period == '2A':
            start_date = last_day_2023 - timedelta(days=365*2)
        elif time_period == '5A':
            start_date = last_day_2023 - timedelta(days=365*5)
        else:
            raise ValueError("Invalid time period")

        query = """"""
        if time_period in ('last_day', 'last_week'):
            query = f"""
                SELECT date, open, high, low, close, volume
                FROM stocks
                WHERE cid = (SELECT id FROM companies WHERE symbol = '{symbol}')
                AND date >= '{start_date.strftime('%Y-%m-%d')}'
                ORDER BY date
            """
        else:
            query = f"""
                SELECT date, open, high, low, close, volume
                FROM daystocks
                WHERE cid = (SELECT id FROM companies WHERE symbol = '{symbol}')
                AND date >= '{start_date.strftime('%Y-%m-%d')}'
                ORDER BY date
            """
        return query

    if values:
        combined_df = pd.DataFrame()
        selected_companies_df = []
        selected_companies = []
        tabs = []
        tabs_summary = []

        for value in values:
            symbol = value.split(" • ")[1]
            query = generate_query(symbol, time_period)
            company_df = pd.read_sql_query(query, engine)

            selected_companies.append(symbol)
            selected_companies_df.append(company_df)

        combined_df = pd.concat(selected_companies_df, keys=selected_companies)

        for symbol in selected_companies:
            df = combined_df.loc[symbol]
            # Create tab content for each value
            tab_content = dash_table.DataTable(
                id={'type': 'dynamic-table', 'index': symbol},
                data=df.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in df.columns],
                page_size=15
            )
            tabs.append(dcc.Tab(label=symbol, value=symbol, children=[tab_content]))

            last_date = df['date'].iloc[-1].date() if not df.empty else ''
            high_last_day = df['high'].iloc[-1] if not df.empty else ''
            low_last_day = df['low'].iloc[-1] if not df.empty else ''
            close_last_day = df['close'].iloc[-1] if not df.empty else ''
            open_last_day = df['open'].iloc[-1] if not df.empty else ''
            volume_last_day = df['volume'].iloc[-1] if not df.empty else ''

            tab_summary_content = html.Div([
                    html.Div(className="resume-box", children=[
                        html.Div(className="box", children=[
                            html.I(className="material-symbols-outlined", children="calendar_month"),
                            dcc.Markdown("Date"),
                            html.Div(id="last-date", children=dcc.Markdown(f"{last_date}"))
                        ]),
                        html.Div(className="box", children=[
                            html.I(className="material-symbols-outlined", children="monitoring"),
                            dcc.Markdown("Volume"),
                            html.Div(id="volume_last_day", children=dcc.Markdown(f"{volume_last_day}"))
                        ])
                    ]),
                    html.Div(className="resume-box", children=[
                        html.Div(className="box", children=[
                            html.I(className="material-symbols-outlined", children="event_available"),
                            dcc.Markdown("Open"),
                            html.Div(id="open_last_day", children=dcc.Markdown(f"{open_last_day}"))
                        ]),
                        html.Div(className="box", children=[
                            html.I(className="material-symbols-outlined", children="event_busy"),
                            dcc.Markdown("Close"),
                            html.Div(id="close_last_day", children=dcc.Markdown(f"{close_last_day}"))
                        ])
                    ]),
                    html.Div(className="resume-box", children=[
                        html.Div(className="box", children=[
                            html.I(className="material-symbols-outlined", children="trending_down"),
                            dcc.Markdown("Low"),
                            html.Div(id="low_last_day", children=dcc.Markdown(f"{low_last_day}"))
                        ]),
                        html.Div(className="box", children=[
                            html.I(className="material-symbols-outlined", children="trending_up"),
                            dcc.Markdown("High"),
                            html.Div(id="high_last_day", children=dcc.Markdown(f"{high_last_day}"))
                        ])
                    ])
                ])
            tabs_summary.append(dcc.Tab(label=symbol, value=symbol, children=[tab_summary_content]))

        if (graphType == 'line'):
            # Création des subplots avec titres et espacement vertical ajusté
            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True,
                subplot_titles=(None, None),
                vertical_spacing=0.01,
                row_heights=[0.8, 0.2]
            )

            color_list = ['#F1C086', '#86BFF1', '#C1F186', '#D486F1', '#F1E386', '#F186C3']
            for idx, symbol in enumerate(selected_companies):
                # Ajout des données High avec une ligne
                df = combined_df.loc[symbol]
                line_color = color_list[idx]
                fig.add_trace(
                    go.Scatter(x=df['date'], y=df['high'], mode='lines', name=symbol, line=dict(color=line_color)),
                    row=1, col=1
                )

            # Ajout des données Volume avec un graphique à barres
            fig.add_trace(
                go.Bar(x=df['date'], y=df['volume'], name='Volume', marker_color='#F1C086'),
                row=2, col=1
            )

            # Ajout des titres et étiquettes des axes
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="Stock Prices", row=1, col=1, title_standoff=25)
            fig.update_yaxes(title_text="Volume", row=2, col=1)

            if not 'toggle-on' in class_name:
                fig.update_yaxes(type="log", row=1, col=1)

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
        elif (graphType == 'candlestick'):
            # Création des subplots avec titres et espacement vertical ajusté
            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True,
                subplot_titles=(None, None),
                vertical_spacing=0.01,
                row_heights=[0.8, 0.2]
            )

            for idx, symbol in enumerate(selected_companies):
                # Ajout des données Candlesticks
                df = combined_df.loc[symbol]
                fig.add_trace(
                    go.Candlestick(x=df['date'],
                                open=df['open'],
                                high=df['high'],
                                low=df['low'],
                                close=df['close'],
                                name=symbol),
                    row=1, col=1
                )

            # Ajout des données Volume avec un graphique à barres
            fig.add_trace(
                go.Bar(x=df['date'], y=df['volume'], name='Volume', marker_color='#F1C086'),
                row=2, col=1
            )

            # Ajout des titres et étiquettes des axes
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="Stock Prices", row=1, col=1, title_standoff=25)
            fig.update_yaxes(title_text="Volume", row=2, col=1)

            if 'toggle-on' not in class_name:
                fig.update_yaxes(type="log", row=1, col=1)

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
        elif (graphType == 'area'):
            # Création des subplots avec titres et espacement vertical ajusté
            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True,
                subplot_titles=(None, None),
                vertical_spacing=0.01,
                row_heights=[0.8, 0.2]
            )

            for idx, symbol in enumerate(selected_companies):
                # Ajout des données Area
                df = combined_df.loc[symbol]
                fig.add_trace(
                    go.Scatter(x=df['date'], y=df['close'], mode='lines', fill='tozeroy', name=symbol),
                    row=1, col=1
                )

            # Ajout des données Volume avec un graphique à barres
            fig.add_trace(
                go.Bar(x=df['date'], y=df['volume'], name='Volume', marker_color='#F1C086'),
                row=2, col=1
            )

            # Ajout des titres et étiquettes des axes
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="Stock Prices", row=1, col=1, title_standoff=25)
            fig.update_yaxes(title_text="Volume", row=2, col=1)

            if 'toggle-on' not in class_name:
                fig.update_yaxes(type="log", row=1, col=1)

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

        return (
            dcc.Graph(figure=fig),
            tabs,
            values[-1].split(" • ")[1],
            {'display': 'block'} if len(tabs) >= 1 else {'display': 'none'},
            {'display': 'block'},
            tabs_summary,
            values[-1].split(" • ")[1],
            class_name,
        )

    return (
        dcc.Graph(),
        [],
        None,
        {'display': 'none'},
        {'display': 'none'},
        [],
        None,
        class_name,
    )



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
    app.run(debug=True)