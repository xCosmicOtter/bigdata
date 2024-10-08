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
import dash_daq as daq
from dash import ALL
import warnings
import os
from init_dashboard import engine,app, server
from update_components import getAllMarket,getAllName,ALL

files_to_process = 271325
graph_options = [
    {"label": html.Div(style={'display': 'flex'}, children=[html.I(
        className="material-symbols-outlined", children="ssid_chart", style={'font-size': '35px', 'padding-top': '10px', 'color': '#F1C086'}), html.Div(
        "Line", style={'font-size': '18px', 'padding': '18px 20px 10px 20px', 'color': '#decfcf'})]), "value": "line"},
    {"label": html.Div(style={'display': 'flex'}, children=[html.I(
        className="material-symbols-outlined", children="candlestick_chart", style={'font-size': '35px', 'padding-top': '10px', 'color': '#F1C086'}), html.Div(
        "Candlestick", style={'font-size': '18px', 'padding': '18px 20px 10px 20px', 'color': '#decfcf'})]), "value": "candlestick"},
    {"label": html.Div(style={'display': 'flex'}, children=[html.I(
        className="material-symbols-outlined", children="area_chart", style={'font-size': '35px', 'padding-top': '10px', 'color': '#F1C086'}), html.Div(
        "Area", style={'font-size': '18px', 'padding': '18px 20px 0px 20px', 'color': '#decfcf'})]), "value": "area"},
]

select_dict = {}



app.layout = html.Div(
    children=[
        # html.Meta(httpEquiv="refresh", content="60"),
        dcc.Store(id='select-dict-store', data=select_dict),
        # Interval for live clock
        dcc.Interval(
            id='interval-component',
            interval=5000,  # Update every 5000 milliseconds (5 seconds)
            n_intervals=0,
            max_intervals=-1
        ),
        dcc.Interval(
            id='interval-component-search',
            interval=60*1000,
            n_intervals=0,
            max_intervals=-1
        ),
        html.Div(
            className="div-top-panel",
            children=[
                # Div for Left Panel App Info
                html.Div(
                    children=[
                        html.Img(
                            className="logo",
                            src=app.get_asset_url("logo.png"),
                        ),
                    ]
                ),

            ]
        ),

        html.Div(
            className="eight columns div-left-panel",
            children=[
                html.Div(className="main-container", children=[
                    html.Div(
                        id='search',
                        className='search',
                        children=[
                            html.I(className='material-icons',
                                   children='search'),
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
                        ],
                    ),
                    html.Div(
                        className="card-progression-bar-shadow",
                        id="progression-bar-text",
                        children=[
                            html.Div(
                                className="progression-bar-text",
                                children=[
                                    dcc.Markdown(
                                        id="progress-text-pertg",
                                        children="""Processing Progression"""
                                    )
                                ]
                            ),
                            dcc.Interval(
                                id='interval-component-progress',
                                interval=10*1000,  # in milliseconds
                                n_intervals=0,
                                max_intervals=-1
                            ),
                            html.Progress(
                                id='progress-bar',
                                value=0,
                                max=files_to_process
                            ),
                        ]
                    ),
                ]),

                html.Br(),
                html.Div(className="filter", children=[
                    html.Div(className="filter-img", children=[
                        html.I(
                            className="material-symbols-outlined", id="filter-img", children="filter_alt")]
                    ),
                    html.Div(
                        className="selector",
                        children=[
                            html.Div(className="markets-filter",
                                     children='Markets'),
                            html.Div(
                                className='market-selector',
                                children=[
                                    html.Button(
                                        children='All',
                                        id='all-button',
                                        className='toggle-button toggle-on',
                                        n_clicks=0
                                    ),
                                    html.Button(
                                        children='COMP A',
                                        id='compA-button',
                                        className='toggle-button toggle-off',
                                        n_clicks=0
                                    ),
                                    html.Button(
                                        children='COMP B',
                                        id='compB-button',
                                        className='toggle-button toggle-off',
                                        n_clicks=0
                                    ),
                                    html.Button(
                                        children='Amsterdam',
                                        id='amsterdam-button',
                                        className='toggle-button toggle-off',
                                        n_clicks=0
                                    ),
                                ]
                            ),
                            html.Div(className="eligility-filter",
                                     children='Eligibility'),
                            html.Div(
                                className='eligility-selector',
                                children=[
                                    html.Button(
                                        children='All',
                                        id='all-eli-button',
                                        className='toggle-button toggle-on',
                                        n_clicks=0
                                    ),
                                    html.Button(
                                        children='Boursorama',
                                        id='boursorama-button',
                                        className='toggle-button toggle-off',
                                        n_clicks=0
                                    ),
                                    html.Button(
                                        children='PEA-PME',
                                        id='peapme-button',
                                        className='toggle-button toggle-off',
                                        n_clicks=0
                                    )
                                ]
                            ),
                        ])
                ]),


                html.Br(),
                html.Div(
                    className="card card-shadow", id="info-select", children=[html.P(
                        children=[
                            html.Span("NO DATA", className="no-data"),
                            html.Span(
                                " - ", style={'color': 'white', 'font-size': '20px'}),
                            html.Span("PLEASE SELECT A COMPANY",
                                      className="no-company")
                        ]
                    ),]),
                html.Br(),
                html.Div(
                    className="card card-shadow",
                    id="graph",
                    children=[
                        html.Div(id='dd-output-graph'),
                        html.Div(
                            className="toolbar",
                            id="toolbar",
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
                                                    value='1M',
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
                                            ],
                                        ),

                                        html.Div(
                                            className='calendar',
                                            children=[
                                                dcc.DatePickerRange(
                                                    id="calendar-picker",
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
                                                html.I(
                                                    className="material-symbols-outlined", id="chart-img", style={'cursor': 'pointer'}, children="ssid_chart"),
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
                    id="title-pie-chart",
                    className="card card-shadow",
                    children=[
                        html.Div(
                            className='value-rep-text',
                            children=[
                                dcc.Markdown("""Value Repartition"""),
                            ]
                        ),

                        html.Div(className="box-chart", children=[
                            html.Div(
                                 id="pie-chart"
                                 ),
                            html.Div(
                                id="input-chart",
                                className="input-chart"
                            ),
                        ]),
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
            id="stick-resume",
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
        dcc.Textarea(className="for-sticky", disabled=True, value=''''''),
        # dcc.Textarea(
        #     id='sql-query',
        #     value='''
        #     SELECT * FROM pg_catalog.pg_tables
        #         WHERE schemaname != 'pg_catalog' AND
        #             schemaname != 'information_schema';
        #     ''',
        #     style={'width': '100%', 'height': 100},
        # ),
        # html.Button('Execute', id='execute-query', n_clicks=0),
        # html.Div(id='query-result'),
    ]
)



@ app.callback(
    [ddep.Output('dd-output-graph', 'children'),
     ddep.Output('info-select', 'children'),
     ddep.Output('table-daystocks', 'children'),
     ddep.Output('table-daystocks', 'value'),
     ddep.Output('title-table-daystocks', 'style'),
     ddep.Output('resume-text', 'style'),
     ddep.Output('tabs-summary', 'children'),
     ddep.Output('tabs-summary', 'value'),
     ddep.Output('toolbar', 'style'),
     ddep.Output('graph', 'style'),
     ddep.Output('input-chart', 'children'),
     ddep.Output('title-pie-chart', 'style')],


    [ddep.Input('companyName', 'value'),
     ddep.Input('graph-type-dropdown', 'value'),
     ddep.Input('tabs-day', 'value'),
     ddep.Input('log-button', 'className'),
     ddep.Input('bollinger-button', 'className'),
     ddep.Input('calendar-picker', 'start_date'),
     ddep.Input('calendar-picker', 'end_date'),],
    [ddep.State('select-dict-store', 'data')]

)
def display_graph_and_tabs(values: list, graphType: str, time_period: str, class_name_log: str,
                           class_name_bollinger: str, start: str, end: str, select_dict):
    """
    Callback function to display graphs and tabs based on selected inputs.

    Args:
        values (list): List of selected company names.
        graphType (str): Type of graph selected.
        time_period (str): Selected time period.
        class_name_log (str): Class name of the log button.
        class_name_bollinger (str): Class name of the Bollinger button.

    Returns:
        tuple: Tuple containing output elements for the Dash app.
    """
    if not values:
        return (
            None,
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
            {'display': 'none'},
            {'display': 'none'},
            None,
            {'display': 'none'}
        )

    def generate_range_query(symbol: str, start: str, end: str, is_few_weeks: bool = False):
        # Check if the total days is less than the days in one month
        if is_few_weeks:
            query = f"""
                SELECT date, value, volume
                FROM stocks
                WHERE cid = (SELECT id FROM companies WHERE symbol = '{symbol}')
                AND date >= '{start}' and date <= '{end}'
                ORDER BY date"""
            return query, start, end
        else:
            query = f"""
                SELECT date, open, high, low, close, volume, average, standard_deviation
                FROM daystocks
                WHERE cid = (SELECT id FROM companies WHERE symbol = '{symbol}')
                AND date >= '{start}' and date <= '{end}'
                ORDER BY date"""
            return query, start, end

    def get_period_first_day(last_day_2023: datetime) -> datetime:
        if time_period == '5J':
            return last_day_2023 - timedelta(weeks=1)
        elif time_period == '1M':
            return last_day_2023 - timedelta(days=30)
        elif time_period == '3M':
            return last_day_2023 - timedelta(days=90)
        elif time_period == '1A':
            return last_day_2023 - timedelta(days=365)
        elif time_period == '2A':
            return last_day_2023 - timedelta(days=365*2)
        elif time_period == '5A':
            return last_day_2023 - timedelta(days=365*5)
        else:
            raise ValueError("Invalid time period")

    # Function to generate SQL query based on time period

    def generate_query(symbol: str, time_period: str, start: str = None, end: str = None, is_few_weeks: bool = False):
        """
        Generate SQL query based on the symbol and time period.

        Args:
            symbol (str): Company symbol.
            time_period (str): Time period.

        Returns:
            tuple: SQL query and flag indicating if it's day stocks.
        """
        is_calendar_available = (start != None and end != None)
        if is_calendar_available:
            return generate_range_query(symbol, start, end, is_few_weeks)

        last_day_2023 = datetime(2023, 12, 31)
        start_date = get_period_first_day(last_day_2023)

        if time_period == '5J':
            query = f"""
                SELECT date, value, volume
                FROM stocks
                WHERE cid = (SELECT id FROM companies WHERE symbol = '{symbol}')
                AND date >= '{start_date.strftime('%Y-%m-%d')}'
                ORDER BY date"""
            return query, start_date, last_day_2023
        else:
            query = f"""
                SELECT date, open, high, low, close, volume, average, standard_deviation
                FROM daystocks
                WHERE cid = (SELECT id FROM companies WHERE symbol = '{symbol}')
                AND date >= '{start_date.strftime('%Y-%m-%d')}'
                ORDER BY date"""
            return query, start_date, last_day_2023

    # Function to decrease brightness of a color
    def decrease_brightness(color, factor):
        """Diminue la clarté d'une couleur donnée par un certain facteur."""
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)

    # Initialize variables
    def process_data(values: list, time_period: str, start: str, end: str):
        """
        Process data for selected companies.

        Returns:
            tuple: Selected companies, their dataframes, and combined dataframe.
        """
        selected_companies = []
        selected_companies_df = []
        selected_companies_5J_df = []
        columns = ['date', 'open', 'close', 'low', 'high',
                   'average', 'standard_deviation', 'volume']

        begining_period = datetime.strptime(
            start, "%Y-%m-%d") if start else None
        ending_period = datetime.strptime(end, "%Y-%m-%d") if end else None

        min_hour, max_hour = 18, 9
        # min_day, max_day = datetime(2023, 12, 31).date(), datetime(2019, 1, 1).date()
        if not (start is None or end is None):
            period = ending_period - begining_period
            is_daystocks = period.days >= 30
        else:
            is_daystocks = time_period != '5J'

        for value in values:
            symbol = value.split(" • ")[1]
            query, starting_date, ending_date = generate_query(
                symbol, time_period, begining_period, ending_period, not is_daystocks)
            company_df = pd.read_sql_query(query, engine)

            # min_day = min(starting_date.date(), company_df['date'].dt.date.min())
            # max_day = max(ending_date.date(), company_df['date'].dt.date.max())

            selected_companies.append(symbol)
            selected_companies_df.append(company_df)

            if is_daystocks:
                continue

            if company_df.empty:
                selected_companies_5J_df.append(pd.DataFrame(columns=columns))
                continue

            min_hour = min(min_hour, company_df['date'].dt.hour.min())
            max_hour = max(max_hour, company_df['date'].dt.hour.max() + 1)

            day_df = company_df.groupby(company_df['date'].dt.date).agg({
                'value': ['first', 'last', "min", "max", "mean", "std"],
                'volume': "last",
            }).reset_index()

            day_df.columns = columns
            day_df['average'] = day_df['average'].round(3)
            day_df['standard_deviation'] = day_df['standard_deviation'].round(
                3)

            selected_companies_5J_df.append(day_df)

        combined_df = pd.concat(selected_companies_df, keys=selected_companies)
        if is_daystocks:
            daystocks_df = combined_df.copy()
            daystocks_df['date'] = daystocks_df['date'].dt.date
        else:
            daystocks_df = pd.concat(
                selected_companies_5J_df, keys=selected_companies)

        # , min_day, max_day
        return selected_companies, combined_df, daystocks_df, is_daystocks, min_hour, max_hour

    def generate_tabs(selected_companies, daystocks_df):
        """
        Generate tabs and summary tabs based on selected companies and their data.

        Returns:
            tuple: Tabs and summary tabs.
        """
        tabs = []
        tabs_summary = []

        for symbol in selected_companies:
            if symbol in daystocks_df.index:
                df = daystocks_df.loc[symbol]
            else:
                df = pd.DataFrame()

            column_available = df.columns if not df.empty else []
            last_data_point = df.iloc[::-1] if not df.empty else df

            tab_content = generate_tab_content(
                symbol, column_available, last_data_point)
            tabs.append(dcc.Tab(label=symbol, value=symbol,
                        children=[tab_content]))

            values = extract_summary_data(df)
            tab_summary_content = generate_summary_tab_content(values)
            tabs_summary.append(
                dcc.Tab(
                    label=symbol,
                    value=symbol,
                    children=[tab_summary_content]
                )
            )

        return tabs, tabs_summary

    def generate_tab_content(symbol: str, column_available: list, last_data_point):
        """
        Generate tab content for each selected company.

        Returns:
            Dash component: Tab content.
        """
        return dash_table.DataTable(
            id={
                'type': 'dynamic-table',
                'index': symbol
            },
            data=last_data_point.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in column_available],
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

    def extract_summary_data(df: pd.DataFrame):
        """
        Extract summary data for a dataframe.

        Returns:
            tuple: Summary data.
        """
        last_date = df['date'].iloc[-1] if not df.empty else ''
        volume_last_day = df['volume'].iloc[-1] if not df.empty else ''
        high_last_day = df['high'].iloc[-1] if not df.empty else ''
        low_last_day = df['low'].iloc[-1] if not df.empty else ''
        close_last_day = df['close'].iloc[-1] if not df.empty else ''
        open_last_day = df['open'].iloc[-1] if not df.empty else ''
        mean_last_day = df['average'].iloc[-1] if not df.empty else ''
        std_last_day = df['standard_deviation'].iloc[-1] if not df.empty else ''

        return last_date, volume_last_day, high_last_day, low_last_day, close_last_day, open_last_day, mean_last_day, std_last_day

    def generate_summary_tab_content(values: tuple):
        last_date, \
            volume_last_day, \
            high_last_day, \
            low_last_day, \
            close_last_day, \
            open_last_day, \
            mean_last_day, \
            std_last_day = values

        """
        Generate summary tab content.

        Returns:
            Dash component: Summary tab content.
        """
        return html.Div([
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
                           children="vital_signs"),
                    dcc.Markdown("Average"),
                    html.Div(id="low_last_day",
                             children=dcc.Markdown(f"{mean_last_day}"))
                ]),
                html.Div(className="box", children=[
                    html.I(className="material-symbols-outlined",
                           children="align_space_around"),
                    dcc.Markdown("Standard deviation"),
                    html.Div(id="high_last_day",
                             children=dcc.Markdown(f"{std_last_day}"))
                ])
            ])
        ])

    selected_companies, combined_df, daystocks_df, \
        is_daystocks, min_hour, max_hour = process_data(
            values, time_period, start, end)
    tabs, tabs_summary = generate_tabs(selected_companies, daystocks_df)

    def compute_bollinger(fig, df, line_color, is_daystocks):
        if 'toggle-off' in class_name_bollinger:
            return

        key = ('close' if is_daystocks else 'value')
        light_line_color = decrease_brightness(line_color, 0.65)

        # Moyennes et écarts-types mobiles sur une fenetre de 20 jours
        rolling_mean = df[key].rolling(window=20).mean()
        rolling_std = df[key].rolling(window=20).std()

        # Calcul des bandes de Bollinger supérieure et inférieure
        upper_band = rolling_mean + (rolling_std * 2)
        lower_band = rolling_mean - (rolling_std * 2)

        # Ajout des bandes de Bollinger au graphique avec une couleur de remplissage
        fill_color = f'rgba{tuple(int(line_color[i:i+2], 16) for i in (1, 3, 5)) + (0.3,)}'
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=lower_band,
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
                y=upper_band,
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
            vertical_spacing=0.035,
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
            # If dataframe is empty, add an empty trace to the figure
            if symbol not in combined_df.index:
                fig.add_trace(
                    go.Scatter(
                        x=[],
                        y=[],
                        mode='lines',
                        name=symbol,
                        line=dict(color=color_list[idx])
                    ),
                    row=1, col=1)
                continue

            df = combined_df.loc[symbol]
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['close' if is_daystocks else 'value'],
                    mode='lines',
                    name=symbol,
                    line=dict(color=color_list[idx])
                ),
                row=1, col=1)
            compute_bollinger(fig, df, color_list[idx], is_daystocks)

    elif (graphType == 'candlestick'):
        increasing_colors = ['green', 'cyan',
                             'blue', 'orange', 'purple', 'yellow']
        decreasing_colors = ['darkred', 'gray', 'red',
                             'darkgreen', 'darkorange', 'darkblue']

        for idx, symbol in enumerate(selected_companies):
            if symbol not in daystocks_df.index:
                fig.add_trace(
                    go.Candlestick(
                        x=[],
                        open=[],
                        high=[],
                        low=[],
                        close=[],
                        name=symbol,
                        increasing_line_color=increasing_colors[idx],
                        decreasing_line_color=decreasing_colors[idx],
                    ),
                    row=1, col=1)
                continue

            # Ajout des données Candlesticks
            df = daystocks_df.loc[symbol].copy()
            df['date'] = pd.to_datetime(df['date']) + timedelta(hours=12)

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

            df['value'] = df['close']
            compute_bollinger(fig, df, color_list[idx], is_daystocks)

        fig.update_layout(xaxis_rangeslider_visible=False)

    elif (graphType == 'area'):
        for idx, symbol in enumerate(selected_companies):
            if symbol not in combined_df.index:
                fig.add_trace(
                    go.Scatter(
                        x=[],
                        y=[],
                        mode='lines',
                        name=symbol,
                        line=dict(color=color_list[idx])
                    ),
                    row=1, col=1)
                continue

            # Ajout des données Area
            df = combined_df.loc[symbol]
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['close' if is_daystocks else 'value'],
                    mode='lines',
                    fill='tozeroy',
                    name=symbol,
                    line=dict(color=color_list[idx])
                ),
                row=1, col=1)

    # Ajout des titres et étiquettes des axes
    fig.update_yaxes(title_text="Stock Prices",
                     row=1, col=1, title_standoff=20, rangemode="tozero")

    if graph_dimension == 1:
        fig.update_yaxes(title_text="Volume", row=2, col=1, rangemode="tozero")

    if 'toggle-on' in class_name_log:
        fig.update_yaxes(type="log", row=1, col=1, rangemode="tozero")
        fig.update_yaxes(type="log", row=2, col=1, rangemode="tozero")

    # Ajout des données Volume avec un graphique à barres
    if graph_dimension == 1:
        if symbol not in daystocks_df.index:
            fig.add_trace(
                go.Bar(
                    x=[],
                    y=[],
                    name='Volume',
                    marker_color='#F1C086'
                ),
                row=2, col=1
            )
        else:
            fig.add_trace(
                go.Bar(
                    x=daystocks_df['date'],
                    y=daystocks_df['volume'],
                    name='Volume',
                    marker_color='#F1C086'
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
        if graphType != 'candlestick':
            fig.update_xaxes(
                row=1, col=1,
                rangebreaks=[
                    dict(bounds=["sat", "mon"]),
                    dict(bounds=[max_hour, min_hour], pattern="hour")
                ]
            )
        else:
            fig.update_xaxes(
                row=1, col=1,
                rangebreaks=[
                    dict(bounds=["sat", "mon"])
                ]
            )

    # Ajout d'un titre général au graphique
    fig.update_layout(
        title_text=f"Stock prices {'and volume ' if graph_dimension == 1 else ''}over time",
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

    def display_info_select(values: list):
        res = []
        markets = getAllMarket()
        for value in values:
            name = value.split(" • ")[0]
            symbol = value.split(" • ")[1]
            query = f'''select mid, boursorama, pea from companies where symbol = \'{symbol}\';'''
            company = pd.read_sql_query(query, engine)
            res.append(html.Div(style={'display': 'flex', 'padding-bottom': '20px'},
                                children=[
                                html.Div(children=f'{name}', style={
                                         'padding-right': '20px', 'width': '200px', 'border-right': '1px dotted rgb(168, 162, 162)'}),
                                html.Div(children=[
                                    html.Div(f'SYMBOL : ', style={
                                             'display': 'inline', 'padding-right': '10px'}),
                                    html.Div(children=f'{symbol}', style={
                                             'display': 'inline', 'width': '200px', 'background': '#F1C086', 'color': 'black', 'padding': '.5rem', 'border': '1px solid #3d3d3d2f'})
                                ], style={'display': 'inline', 'padding-right': '20px', 'padding-left': '20px', 'width': '200px', 'border-right': '1px dotted rgb(168, 162, 162)'}),
                                html.Div(children=[
                                    html.Div(f'MARKET : ', style={
                                             'display': 'inline', 'padding-right': '10px'}),
                                    html.Div(children=f'{markets[company['mid'][0] - 1].upper()}', style={'display': 'inline', 'width': '200px', 'background': '#F1C086', 'color': 'black', 'padding': '.5rem', 'border': '1px solid #3d3d3d2f'})
                                ], style={'display': 'inline', 'padding-right': '20px', 'padding-left': '20px', 'width': '200px', 'border-right': '1px dotted rgb(168, 162, 162)'}),
                                html.Div(children=[
                                    html.Div(f'ELIGIBILITY : ', style={
                                             'display': 'inline', 'padding-right': '10px', 'padding-left': '20px'}),
                                    html.Div(children=f'BOURSORAMA' if company['boursorama'][0] == 'true' else None,
                                             style={'display': 'inline', 'width': '200px', 'background': '#F1C086', 'color': 'black', 'padding': '.5rem', 'border': '1px solid #3d3d3d2f', 'display': 'none' if (company['boursorama'][0] != 'true') else 'inline'}),
                                    html.Div(children=f'PEA-PME' if company['pea'][0] == True else None,
                                             style={'display': 'inline', 'width': '200px', 'background': '#F1C086', 'color': 'black', 'padding': '.5rem', 'border': '1px solid #3d3d3d2f', 'margin-left': '20px', 'display': 'none' if (company['pea'][0] != True) else 'inline'})
                                ])
                                ]))
        return res

    info_select = display_info_select(values)

    def create_input_pie_chart(selected_items):
        selected_options = []
        for i, companie in enumerate(selected_items):
            companie_name = companie.split(" • ")[0]
            selected_options.append(
                daq.NumericInput(
                    id={"item": str(i)},
                    label={'label': companie.split(" • ")[0], 'style': {
                        'color': 'white', 'font-size': '16px', 'padding-left': '20px',
                    }},
                    value=select_dict.get(companie_name, 1),
                    max=9999,
                    labelPosition='right',
                    style={'padding': '10px 10px 10px 50px',
                           'justify-content': 'start'},
                    theme={
                        'dark': True,
                        'primary': '#00EA64',
                        'secondary': '#6E6E6E',
                    }
                )
            )
        return selected_options
    inputs_chart = create_input_pie_chart(values)
    return (
        dcc.Graph(figure=fig),
        info_select,
        tabs,
        values[-1].split(" • ")[1],
        {'display': 'block'} if len(tabs) >= 1 else {'display': 'none'},
        {'display': 'block'},
        tabs_summary,
        values[-1].split(" • ")[1],
        {'display': 'flex'},
        {'display': 'block'},
        inputs_chart,
        {'display': 'block'}
    )




@ app.callback(ddep.Output('query-result', 'children'),
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
