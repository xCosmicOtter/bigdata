import dash
from dash import dcc, dash_table
from dash import html
import dash.dependencies as ddep
import pandas as pd
import sqlalchemy
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, timezone
import plotly.express as px
import plotly.graph_objs as go

external_stylesheets = [
    # 'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://fonts.googleapis.com/css2?family=Material+Icons&display=block',
    'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0'
]

DATABASE_URI = 'timescaledb://ricou:monmdp@db:5432/bourse'    # inside docker
# DATABASE_URI = 'timescaledb://ricou:monmdp@localhost:5432/bourse'  # outisde docker
engine = sqlalchemy.create_engine(DATABASE_URI)

app = dash.Dash(__name__,  title="Bourse", suppress_callback_exceptions=True,
                external_stylesheets=external_stylesheets)
server = app.server

graph_options = [
    {"label": html.Span([html.Img(src="/assets/line.png", height=30), html.Span(
        "Ligne", style={'font-size': 15, 'padding-left': 10})]), "value": "line"},
    {"label": html.Span([html.Img(src="/assets/candlestick.png", height=30), html.Span(
        "Bougies", style={'font-size': 15, 'padding-left': 10})]), "value": "candlestick"},
    {"label": html.Span([html.Img(src="/assets/area.png", height=30), html.Span(
        "Aire", style={'font-size': 15, 'padding-left': 10})]), "value": "area"},
]


def getAllName():
    query = '''select name, symbol from companies;'''
    df = pd.read_sql_query(query, engine)
    name_symbol_tuple = list(zip(df['name'], df['symbol']))
    list_name_symbol = [name + ' • ' +
                        symbol for name, symbol in name_symbol_tuple]
    return list_name_symbol


app.layout = html.Div(
    children=[
        # Interval for live clock
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
                            className="logo-text",
                            children=[
                                html.Img(
                                    className="logo",
                                    src=app.get_asset_url("analytics.png"),
                                ),
                                dcc.Markdown("""Analytics""")
                            ]
                        )
                    ]
                ),

                html.Div(
                    className="project-description",
                    children=[
                        dcc.Markdown("""Projet Python Big Data for EPITA."""),
                    ]
                ),
            ]
        ),

        html.Div(
            className="eight columns div-left-panel",
            children=[
                html.Div(
                    id='search',
                    className='search',
                    children=[
                        html.I(className='material-icons', children='search'),
                        dcc.Dropdown(
                            placeholder="Select a company",
                            id='companyName',
                            style={
                                'flex': '1',
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
                        html.Div(id="warning-container",
                                 className="warning-container"),
                    ]
                ),

                html.Br(),
                dcc.Checklist(
                    options=['CompA', 'CompB', 'PEAPME', 'AMSTERDAM'],
                    inline=True
                ),

                html.Br(),
                html.Div(
                    className="card card-shadow",
                    children=[
                        html.Div(id='dd-output-graph'),
                        html.Div(
                            className="toolbar",
                            children=[
                                html.Div(
                                    className="toolbar-left",
                                    children=[
                                        dcc.Tabs(
                                            id="tabs-day",
                                            colors={"primary": "#F1C086", },
                                            value='5J',
                                            children=[
                                                dcc.Tab(
                                                    label='5J',
                                                    className='tab-style',
                                                    selected_className='tab-selected-style',
                                                    value='5J'
                                                ),
                                                dcc.Tab(
                                                    label='1M',
                                                    className='tab-style',
                                                    selected_className='tab-selected-style',
                                                    value='1M'
                                                ),
                                                dcc.Tab(
                                                    label='3M',
                                                    className='tab-style',
                                                    selected_className='tab-selected-style',
                                                    value='3M'
                                                ),
                                                dcc.Tab(
                                                    label='1A',
                                                    className='tab-style',
                                                    selected_className='tab-selected-style',
                                                    value='1A'
                                                ),
                                                dcc.Tab(
                                                    label='2A',
                                                    className='tab-style',
                                                    selected_className='tab-selected-style',
                                                    value='2A'
                                                ),
                                                dcc.Tab(
                                                    label='5A',
                                                    className='tab-style-sep',
                                                    selected_className='tab-selected-style',
                                                    value='5A'
                                                ),
                                            ]
                                        ),

                                        html.Div(
                                            className='calendar',
                                            children=[
                                                dcc.DatePickerRange(
                                                    month_format='DD/MM/YYYY',
                                                    end_date_placeholder_text='JJ/MM/AAAA',
                                                    start_date_placeholder_text='JJ/MM/AAAA',
                                                    display_format='DD/MM/YYYY',
                                                    minimum_nights=4,
                                                    min_date_allowed="2019-01-01",
                                                    max_date_allowed="2023-12-31",
                                                    initial_visible_month="2023-12-01",
                                                    clearable=True
                                                )
                                            ]
                                        ),

                                        html.Div(
                                            className='chart-options',
                                            children=[
                                                # Image cliquable pour ouvrir la liste déroulante
                                                html.Img(
                                                    src="/assets/line.png",
                                                    id="chart-img",
                                                    height=50,
                                                    style={'cursor': 'pointer'}
                                                ),
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
                                    ]
                                ),

                                html.Div(
                                    className='toolbar-right',
                                    children=[
                                        html.Button(
                                            children='Bollinger',
                                            id='bollinger-button',
                                            className='toggle-button toggle-off',
                                            n_clicks=0
                                        ),
                                        html.Button(
                                            children='Log',
                                            id='log-button',
                                            className='toggle-button toggle-off',
                                            n_clicks=0
                                        ),
                                        html.Div(
                                            id='clock',
                                            className='clock'
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ]
                ),

                html.Br(),
                html.Div(
                    id="title-table-daystocks",
                    className="card card-shadow",
                    children=[
                        html.Div(
                            className='historical-text',
                            children=[
                                dcc.Markdown("""Historical Data"""),
                            ]
                        ),
                        dcc.Tabs(
                            className='table-daystocks',
                            id="table-daystocks",
                            colors={"primary": "#F1C086", },
                            children=[]
                        )
                    ]
                ),
            ]
        ),

        html.Div(
            className="three columns day-resume",
            children=[
                html.Div(
                    className="card card-shadow",
                    id="resume-text",
                    children=[
                        html.Div(
                            className="resume-text",
                            children=[
                                dcc.Markdown("""Day Summary""")
                            ]
                        ),
                        dcc.Tabs(
                            className="tabs-summary",
                            id="tabs-summary",
                            colors={"primary": "#F1C086"},
                            vertical=True,
                            children=[]
                        )
                    ]
                )
            ]
        ),
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
    ]
)


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
    [ddep.Output('search', 'style'),
     ddep.Output("companyName", "options"),
     ddep.Output("warning-container", "children")],

    [ddep.Input('companyName', 'value')]
)
def update_search_bar_height(selected_items):
    options = getAllName()
    input_warning = None
    height = 15
    if (selected_items != None):
        row = len(selected_items) // 3
        height = 15 + row * 35  # Adjust as needed
        if len(selected_items) >= 6:
            input_warning = html.P(id="warning-container", children=[
                html.I(className="material-symbols-outlined",
                       children="warning"),
                dcc.Markdown("6 max reached")])
            options = [
                {"label": option, "value": option, "disabled": True}
                for option in options
            ]
    return {'height': f'{height}px'}, options, input_warning


@app.callback(
    ddep.Output('log-button', 'className'),
    ddep.Input('log-button', 'n_clicks')
)
def update_log_button_class(n_clicks):
    if n_clicks % 2 == 0:
        return 'toggle-button toggle-off'
    else:
        return 'toggle-button toggle-on'


@app.callback(
    ddep.Output('bollinger-button', 'className'),
    ddep.Input('bollinger-button', 'n_clicks')
)
def update_bollinger_button_class(n_clicks):
    if n_clicks % 2 == 0:
        return 'toggle-button toggle-off'
    else:
        return 'toggle-button toggle-on'


@app.callback(
    [ddep.Output('dd-output-graph', 'children'),
     ddep.Output('table-daystocks', 'children'),
     ddep.Output('table-daystocks', 'value'),
     ddep.Output('title-table-daystocks', 'style'),
     ddep.Output('resume-text', 'style'),
     ddep.Output('tabs-summary', 'children'),
     ddep.Output('tabs-summary', 'value'),],


    [ddep.Input('companyName', 'value'),
     ddep.Input('graph-type-dropdown', 'value'),
     ddep.Input('tabs-day', 'value'),
     ddep.Input('log-button', 'className'),
     ddep.Input('bollinger-button', 'className')]
)
def display_graph_and_tabs(values, graphType, time_period, class_name_log, class_name_bollinger):
    if not values:
        return (
            html.P(
                children=[
                    html.Span("NO DATA", className="no-data"),
                    html.Span(
                        " - ", style={'color': 'white', 'font-size': '20px'}),
                    html.Span("PLEASE SELECT A COMPANY",
                              className="no-company")
                ]
            ),
            [],
            None,
            {'display': 'none'},
            {'display': 'none'},
            [],
            None,
        )

    def generate_query(symbol, time_period):
        last_day_2023 = datetime(2023, 12, 31)

        if time_period == '5J':
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

        if time_period == '5J':
            query = f"""
                SELECT date, value, volume
                FROM stocks
                WHERE cid = (SELECT id FROM companies WHERE symbol = '{symbol}')
                AND date >= '{start_date.strftime('%Y-%m-%d')}'
                ORDER BY date"""
            return query, False
        else:
            query = f"""
                SELECT date, open, high, low, close, volume, average, standard_deviation
                FROM daystocks
                WHERE cid = (SELECT id FROM companies WHERE symbol = '{symbol}')
                AND date >= '{start_date.strftime('%Y-%m-%d')}'
                ORDER BY date"""
            return query, True

    def decrease_brightness(color, factor):
        """Diminue la clarté d'une couleur donnée par un certain facteur."""
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)

    selected_companies = []
    selected_companies_df = []
    combined_df = pd.DataFrame()

    tabs = []
    is_daystocks = True
    tabs_summary = []

    for value in values:
        symbol = value.split(" • ")[1]
        query, is_daystocks = generate_query(symbol, time_period)
        company_df = pd.read_sql_query(query, engine)

        if not is_daystocks:
            company_df['close'] = company_df['high'] = company_df['low'] = company_df['open'] = company_df['value']

        selected_companies.append(symbol)
        selected_companies_df.append(company_df)

    combined_df = pd.concat(selected_companies_df, keys=selected_companies)

    for symbol in selected_companies:
        df = combined_df.loc[symbol]

        # Create tab content for each value
        tab_content = dash_table.DataTable(
            id={
                'type': 'dynamic-table',
                'index': symbol
            },
            data=df.iloc[::-1].to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df.columns],
            page_size=15,
            style_header={
                'backgroundColor': "#131312",
                'textAlign': 'center',
                'color': 'rgba(255, 255, 255, 0.7)'
            },
            style_data={
                'backgroundColor': "#1A1B1B",
                'textAlign': 'center',
                'color': 'rgba(255, 255, 255, 0.7)'
            }
        )
        tabs.append(dcc.Tab(label=symbol, value=symbol,
                    children=[tab_content]))

        last_date = df['date'].iloc[-1].date() if not df.empty else ''
        volume_last_day = df['volume'].iloc[-1] if not df.empty else ''

        if is_daystocks:
            high_last_day = df['high'].iloc[-1] if not df.empty else ''
            low_last_day = df['low'].iloc[-1] if not df.empty else ''
            close_last_day = df['close'].iloc[-1] if not df.empty else ''
            open_last_day = df['open'].iloc[-1] if not df.empty else ''
            mean_last_day = df['average'].iloc[-1] if not df.empty else ''
            std_last_day = df['standard_deviation'].iloc[-1] if not df.empty else ''
        else:
            high_last_day = low_last_day = close_last_day = open_last_day = ''
            mean_last_day = df['high'].mean() if not df.empty else ''
            std_last_day = df['high'].std() if not df.empty else ''

        tab_summary_content = html.Div([
            html.Div(className="resume-box", children=[
                html.Div(className="box", children=[
                    html.I(className="material-symbols-outlined",
                           children="calendar_month"),
                    dcc.Markdown("Date"),
                    html.Div(id="last-date",
                             children=dcc.Markdown(f"{last_date}"))
                ]),
                html.Div(className="box", children=[
                    html.I(className="material-symbols-outlined",
                           children="monitoring"),
                    dcc.Markdown("Volume"),
                    html.Div(id="volume_last_day",
                             children=dcc.Markdown(f"{volume_last_day}"))
                ])
            ]),
            html.Div(className="resume-box", children=[
                html.Div(className="box", children=[
                    html.I(className="material-symbols-outlined",
                           children="event_available"),
                    dcc.Markdown("Open"),
                    html.Div(id="open_last_day",
                             children=dcc.Markdown(f"{open_last_day}"))
                ]),
                html.Div(className="box", children=[
                    html.I(className="material-symbols-outlined",
                           children="event_busy"),
                    dcc.Markdown("Close"),
                    html.Div(id="close_last_day",
                             children=dcc.Markdown(f"{close_last_day}"))
                ])
            ]),
            html.Div(className="resume-box", children=[
                html.Div(className="box", children=[
                    html.I(className="material-symbols-outlined",
                           children="trending_down"),
                    dcc.Markdown("Low"),
                    html.Div(id="low_last_day",
                             children=dcc.Markdown(f"{low_last_day}"))
                ]),
                html.Div(className="box", children=[
                    html.I(className="material-symbols-outlined",
                           children="trending_up"),
                    dcc.Markdown("High"),
                    html.Div(id="high_last_day",
                             children=dcc.Markdown(f"{high_last_day}"))
                ])
            ]),
            html.Div(className="resume-box", children=[
                html.Div(className="box", children=[
                    html.I(className="material-symbols-outlined",
                           children="trending_down"),
                    dcc.Markdown("Average"),
                    html.Div(id="low_last_day",
                             children=dcc.Markdown(f"{round(mean_last_day or 0, 3)}"))
                ]),
                html.Div(className="box", children=[
                    html.I(className="material-symbols-outlined",
                           children="trending_up"),
                    dcc.Markdown("Standard deviation"),
                    html.Div(id="high_last_day",
                             children=dcc.Markdown(f"{round(std_last_day or 0, 3)}"))
                ])
            ])
        ])
        tabs_summary.append(
            dcc.Tab(
                label=symbol,
                value=symbol,
                children=[tab_summary_content]
            )
        )

    def compute_bollinger(fig, df, line_color):
        if 'toggle-off' in class_name_bollinger:
            return
        light_line_color = decrease_brightness(line_color, 0.65)

        # Moyennes et écarts-types mobiles sur une fenetre de 20 jours
        rolling_mean = df['close'].rolling(window=20).mean()
        rolling_std = df['close'].rolling(window=20).std()

        # Calcul des bandes de Bollinger supérieure et inférieure
        upper_band = rolling_mean + (rolling_std * 2)
        lower_band = rolling_mean - (rolling_std * 2)

        # Ajout des bandes de Bollinger au graphique avec une couleur de remplissage
        fill_color = f'rgba{tuple(int(line_color[i:i+2], 16) for i in (1, 3, 5)) + (0.3,)}'
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=lower_band,  # .shift(10)
                mode='lines',
                line=dict(color=light_line_color, dash='dot'),
                name='Lower Bollinger Band',
                showlegend=False,
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=upper_band,  # .shift(10)
                mode='lines',
                line=dict(color=light_line_color, dash='dot'),
                name='Higher Bollinger Band',
                fill='tonexty',
                fillcolor=fill_color,
                showlegend=False,
            ),
            row=1, col=1
        )

    graph_dimension = min(len(selected_companies), 2)
    # Subplots creation
    if (graph_dimension == 1):
        fig = make_subplots(
            cols=1,
            rows=2,
            shared_xaxes=True,
            subplot_titles=(None, None),
            vertical_spacing=0.01,
            row_heights=[0.8, 0.2]
        )
    else:
        fig = make_subplots(
            cols=1,
            rows=1
        )

    color_list = ['#F1C086', '#86BFF1', '#C1F186',
                  '#D486F1', '#F1E386', '#F186C3']
    if (graphType == 'line'):
        for idx, symbol in enumerate(selected_companies):
            df = combined_df.loc[symbol]
            line_color = color_list[idx]
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['high'],
                    mode='lines',
                    name=symbol,
                    line=dict(color=line_color)
                ),
                row=1, col=1)
            compute_bollinger(fig, df, line_color)

    elif (graphType == 'candlestick'):
        increasing_colors = ['green', 'cyan',
                             'blue', 'orange', 'purple', 'yellow']
        decreasing_colors = ['darkred', 'gray', 'red',
                             'darkgreen', 'darkorange', 'darkblue']

        for idx, symbol in enumerate(selected_companies):
            # Ajout des données Candlesticks
            df = combined_df.loc[symbol]
            line_color = color_list[idx]
            fig.add_trace(
                go.Candlestick(
                    x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name=symbol,
                    increasing_line_color=increasing_colors[idx],
                    decreasing_line_color=decreasing_colors[idx],
                ),
                row=1, col=1)
            compute_bollinger(fig, df, line_color)

        fig.update_layout(xaxis_rangeslider_visible=False)

    elif (graphType == 'area'):
        for idx, symbol in enumerate(selected_companies):
            # Ajout des données Area
            df = combined_df.loc[symbol]
            line_color = color_list[idx]
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['high'],
                    mode='lines',
                    fill='tozeroy',
                    name=symbol,
                    line=dict(color=line_color)
                ),
                row=1, col=1)

    # Ajout des titres et étiquettes des axes
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Stock Prices",
                     row=1, col=1, title_standoff=20)

    if graph_dimension == 1:
        fig.update_yaxes(title_text="Volume", row=2, col=1, rangemode="tozero")

    if 'toggle-on' in class_name_log:
        fig.update_yaxes(type="log", row=1, col=1)
        fig.update_yaxes(type="log", row=2, col=1)

    # Ajout des données Volume avec un graphique à barres
    if graph_dimension == 1:
        fig.add_trace(
            go.Bar(
                x=df['date'],
                y=df['volume'],
                name='Volume',
                marker_color=line_color
            ),
            row=2, col=1
        )

    # Mise à jour des ticks des axes x pour les afficher à l'extérieur et espacement cohérent
    if graph_dimension == 1:
        fig.update_xaxes(
            ticks="outside",
            ticklabelmode="period",
            tickcolor="white",
            ticklen=10,
            row=2, col=1,
        )

    if is_daystocks:
        fig.update_xaxes(
            row=1, col=1,
            rangebreaks=[
                dict(bounds=["sat", "mon"]),
                # dict(bounds=[18, 9], pattern="hour")
            ]
        )
    else:
        fig.update_xaxes(
            row=1, col=1,
            rangebreaks=[
                dict(bounds=["sat", "mon"]),
                dict(bounds=[18, 16], pattern="hour")
            ]
        )

    # Ajout d'un titre général au graphique
    fig.update_layout(
        title_text="Analyse des prix des actions et du volume",
        template="plotly_dark",
        paper_bgcolor='#131312',  # Couleur de fond du graphique
        plot_bgcolor='#131312',
        font=dict(color='rgba(255, 255, 255, 0.7)'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )

    return (
        dcc.Graph(figure=fig),
        tabs,
        values[-1].split(" • ")[1],
        {'display': 'block'} if len(tabs) >= 1 else {'display': 'none'},
        {'display': 'block'},
        tabs_summary,
        values[-1].split(" • ")[1],
    )


@app.callback(ddep.Output('query-result', 'children'),
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
