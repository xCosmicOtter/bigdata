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
from init_dashboard import engine,app,server

files_to_process = 271325



def getAllMarket():
    query = '''select alias from markets;'''
    df = pd.read_sql_query(query, engine)
    return list(df['alias'])


def getAllName():
    query = '''select name, symbol from companies;'''
    df = pd.read_sql_query(query, engine)
    name_symbol_tuple = list(zip(df['name'], df['symbol']))
    list_name_symbol = [name + ' • ' +
                        symbol for name, symbol in name_symbol_tuple]
    return list_name_symbol


def getAllNameFromMarket(mids, isPea, isBoursorama: str):
    if (mids == []):
        return []
    str = []
    for i in mids:
        str.append(f' mid = {i} ')
    whstr = "where (" + "or".join(str) + ")" if len(str) != 0 else ""

    peastr = ""
    if (isPea != None):
        peastr = (" where " if whstr == "" else " and ") + f"pea = {isPea}"

    bourstr = ""
    if (isBoursorama != None):
        bourstr = " and " + f"boursorama = \'{isBoursorama}\'"

    query = f'''select name, symbol from companies {whstr + peastr + bourstr};'''
    df = pd.read_sql_query(query, engine)
    name_symbol_tuple = list(zip(df['name'], df['symbol']))
    list_name_symbol = [name + ' • ' +
                        symbol for name, symbol in name_symbol_tuple]
    return list_name_symbol


# ==================

@ app.callback(
    ddep.Output('log-button', 'className'),
    ddep.Input('log-button', 'n_clicks')
)
def update_log_button_class(n_clicks):
    if n_clicks % 2 == 0:
        return 'toggle-button toggle-off'
    else:
        return 'toggle-button toggle-on'


@ app.callback(
    ddep.Output('bollinger-button', 'className'),
    ddep.Input('bollinger-button', 'n_clicks')
)
def update_bollinger_button_class(n_clicks):
    if n_clicks % 2 == 0:
        return 'toggle-button toggle-off'
    else:
        return 'toggle-button toggle-on'


@ app.callback(
    ddep.Output('all-button', 'className'),
    ddep.Output('all-button', 'children'),
    ddep.Input('all-button', 'n_clicks')
)
def update_all_button_class(n_clicks):
    if n_clicks % 2 == 1:
        return 'toggle-button toggle-off', 'ALL'
    else:
        return 'toggle-button toggle-on', [
            html.I(id="done-all-button",
                   className="material-symbols-outlined", children="done"),
            html.Div(className="all-text-button", children='ALL')
        ]


@ app.callback(
    ddep.Output('compA-button', 'className'),
    ddep.Output('compA-button', 'children'),
    ddep.Input('compA-button', 'n_clicks')
)
def update_compA_button_class(n_clicks):
    if n_clicks % 2 == 0:
        return 'toggle-button toggle-off', 'COMP A'
    else:
        return 'toggle-button toggle-on', [
            html.I(id="done-compA-button",
                   className="material-symbols-outlined", children="done"),
            html.Div(className="compA-text-button", children='COMP A')
        ]


@ app.callback(
    ddep.Output('compB-button', 'className'),
    ddep.Output('compB-button', 'children'),
    ddep.Input('compB-button', 'n_clicks')
)
def update_compB_button_class(n_clicks):
    if n_clicks % 2 == 0:
        return 'toggle-button toggle-off', 'COMP B'
    else:
        return 'toggle-button toggle-on', [
            html.I(id="done-compB-button",
                   className="material-symbols-outlined", children="done"),
            html.Div(className="compB-text-button", children='COMP B')
        ]


@ app.callback(
    ddep.Output('peapme-button', 'className'),
    ddep.Output('peapme-button', 'children'),
    ddep.Input('peapme-button', 'n_clicks')
)
def update_PEA_PME_button_class(n_clicks):
    if n_clicks % 2 == 0:
        return 'toggle-button toggle-off', 'PEA-PME'
    else:
        return 'toggle-button toggle-on', [
            html.I(id="done-peapme-button",
                   className="material-symbols-outlined", children="done"),
            html.Div(className="peapme-text-button", children='PEA-PME')
        ]


@ app.callback(
    ddep.Output('amsterdam-button', 'className'),
    ddep.Output('amsterdam-button', 'children'),
    ddep.Input('amsterdam-button', 'n_clicks')
)
def update_amsterdam_button_class(n_clicks):
    if n_clicks % 2 == 0:
        return 'toggle-button toggle-off', 'AMSTERDAM'
    else:
        return 'toggle-button toggle-on', [
            html.I(id="done-amsterdam-button",
                   className="material-symbols-outlined", children="done"),
            html.Div(className="amsterdam-text-button", children='AMSTERDAM')
        ]


@ app.callback(
    ddep.Output('all-eli-button', 'className'),
    ddep.Output('all-eli-button', 'children'),
    ddep.Input('all-eli-button', 'n_clicks')
)
def update_all_button_class(n_clicks):
    if n_clicks % 2 == 1:
        return 'toggle-button toggle-off', 'ALL'
    else:
        return 'toggle-button toggle-on', [
            html.I(id="done-all-eli-button",
                   className="material-symbols-outlined", children="done"),
            html.Div(className="all-eli-text-button", children='ALL')
        ]


@ app.callback(
    ddep.Output('boursorama-button', 'className'),
    ddep.Output('boursorama-button', 'children'),
    ddep.Input('boursorama-button', 'n_clicks')
)
def update_all_button_class(n_clicks):
    if n_clicks % 2 == 0:
        return 'toggle-button toggle-off', 'BOURSORAMA'
    else:
        return 'toggle-button toggle-on', [
            html.I(id="done-boursorama-button",
                   className="material-symbols-outlined", children="done"),
            html.Div(className="boursorama-text-button", children='BOURSORAMA')
        ]

@ app.callback(
    ddep.Output('select-dict-store', 'data'),
    [ddep.Input({"item": ALL}, 'value'), ddep.Input({"item": ALL}, 'label')],
    [ddep.State('select-dict-store', 'data')]
)
def update_select_dict(values_list, labels_list, select_dict):
    for label, value in zip(labels_list, values_list):
        select_dict[label['label']] = value
    return select_dict


@ app.callback(
    ddep.Output('pie-chart', 'children'),
    [ddep.Input('companyName', 'value'),
     ddep.Input('select-dict-store', 'data')]
)
def update_chart(selected_items, select_dict):
    color_list = ['#F1C086', '#86BFF1', '#C1F186',
                  '#D486F1', '#F1E386', '#F186C3']
    if (selected_items == None):
        return None
    last_values = []
    for i, companie in enumerate(selected_items):
        companie_name = companie.split(" • ")[0]
        symbol = companie.split(" • ")[1]
        query = f"""
                SELECT date, close
                FROM daystocks
                WHERE cid = (SELECT id FROM companies WHERE symbol = '{symbol}')
                ORDER BY date desc limit 1"""
        current_df = pd.read_sql_query(query, engine)
        current_df['name'] = companie_name
        current_df['total_value'] = current_df['close'] * \
            select_dict.get(companie_name, 1)
        last_values.append(current_df)

    # Create initial pie chart
    if len(last_values) == 0:
        return None
    df_final = pd.concat(last_values)
    fig = px.pie(df_final, values='total_value', names='name', hole=0.3)
    fig.update_traces(marker=dict(
        colors=[color_list[i] for i, _ in enumerate(df_final['name'])]))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='#131312',
        plot_bgcolor='#131312',
        width=800,
        height=400)
    # Create input
    return dcc.Graph(figure=fig)


@ app.callback(
    [ddep.Output('search', 'style'),
     ddep.Output("companyName", "options"),
     ddep.Output("warning-container", "children"),
     ],

    [ddep.Input('companyName', 'value'),
     ddep.Input('compA-button', 'className'),
     ddep.Input('compB-button', 'className'),
     ddep.Input('amsterdam-button', 'className'),
     ddep.Input('peapme-button', 'className'),
     ddep.Input('all-button', 'className'),
     ddep.Input('all-eli-button', 'className'),
     ddep.Input('boursorama-button', 'className'),
     ddep.Input('interval-component-search', 'n_intervals')
     ]
)
def update_search_bar(selected_items, compA_class, compB_class, amsterdam_class, pea_class, all_class, all_eli_class, boursorama_class, n_intervals):
    options = []
    markets = getAllMarket()
    isPea = None
    isBoursorama = None

    if "toggle-off" in all_eli_class:
        if "toggle-off" in pea_class:
            isPea = False
        else:
            isPea = True

        if "toggle-off" in boursorama_class:
            isBoursorama = 'false'
        else:
            isBoursorama = 'true'

    if "toggle-on" in all_class:
        getFromMarket = [markets.index(
            'compA') + 1, markets.index('compB') + 1, markets.index('amsterdam') + 1]
        options = getAllNameFromMarket(getFromMarket, isPea, isBoursorama)
    else:
        getFromMarket = []
        if "toggle-on" in compA_class:
            getFromMarket.append(markets.index('compA')+1)
        if "toggle-on" in compB_class:
            getFromMarket.append(markets.index('compB')+1)
        if "toggle-on" in amsterdam_class:
            getFromMarket.append(markets.index('amsterdam')+1)
        options = getAllNameFromMarket(getFromMarket, isPea, isBoursorama)

    input_warning = None
    height = 15
    if (selected_items != None):
        options += selected_items
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
    ddep.Output('tabs-day', 'children'),
    [ddep.Input('calendar-picker', 'start_date'),
     ddep.Input('calendar-picker', 'end_date'),]
)
def disable_tabs(start, end):
    if start != None and end != None:
        return [
            dcc.Tab(
                label='5J',
                className='tab-style',
                selected_className='tab-selected-style',
                disabled_className='tab-disabled-style',
                value='5J',
                disabled=True
            ),
            dcc.Tab(
                label='1M',
                className='tab-style',
                selected_className='tab-selected-style',
                disabled_className='tab-disabled-style',
                value='1M',
                disabled=True
            ),
            dcc.Tab(
                label='3M',
                className='tab-style',
                selected_className='tab-selected-style',
                disabled_className='tab-disabled-style',
                value='3M',
                disabled=True
            ),
            dcc.Tab(
                label='1A',
                className='tab-style',
                selected_className='tab-selected-style',
                disabled_className='tab-disabled-style',
                value='1A',
                disabled=True
            ),
            dcc.Tab(
                label='2A',
                className='tab-style',
                selected_className='tab-selected-style',
                disabled_className='tab-disabled-style',
                value='2A',
                disabled=True
            ),
            dcc.Tab(
                label='5A',
                className='tab-style-sep',
                selected_className='tab-selected-style',
                disabled_className='tab-disabled-style',
                value='5A',
                disabled=True
            ),
        ]
    else:
        return [
            dcc.Tab(
                label='5J',
                className='tab-style',
                selected_className='tab-selected-style',
                value='5J',
                disabled=False
            ),
            dcc.Tab(
                label='1M',
                className='tab-style',
                selected_className='tab-selected-style',
                value='1M',
                disabled=False
            ),
            dcc.Tab(
                label='3M',
                className='tab-style',
                selected_className='tab-selected-style',
                value='3M',
                disabled=False
            ),
            dcc.Tab(
                label='1A',
                className='tab-style',
                selected_className='tab-selected-style',
                value='1A',
                disabled=False
            ),
            dcc.Tab(
                label='2A',
                className='tab-style',
                selected_className='tab-selected-style',
                value='2A',
                disabled=False
            ),
            dcc.Tab(
                label='5A',
                className='tab-style-sep',
                selected_className='tab-selected-style',
                value='5A',
                disabled=False
            ),
        ]

# Define callback to update progress bar
@app.callback(
    [ddep.Output('progress-bar', 'value'),
     ddep.Output('progress-text-pertg', 'children'),
     ddep.Output('interval-component-progress', 'max_intervals'),
     ddep.Output('interval-component-search', 'max_intervals')],
    [ddep.Input('interval-component-progress', 'n_intervals')]
)
def update_progress(n):
    query = """
            SELECT COUNT(DISTINCT name) AS nbr
            FROM file_done;
            """
    get_id = pd.read_sql_query(query, engine)
    progress = int(get_id.loc[0, 'nbr']) if len(get_id['nbr']) != 0 else 0
    pctg = round(progress / files_to_process * 100,
                 1) if progress != files_to_process else 100
    disable = 0 if pctg == 100 else -1
    return progress, f"Processing Progression: {pctg}%", disable, disable


@ app.callback(
    ddep.Output('clock', 'children'),
    [ddep.Input('interval-component', 'n_intervals')]
)
def update_clock(n_intervals):

    local_time = datetime.now().strftime("%H:%M:%S")
    utc_offset = datetime.now(timezone.utc).astimezone().utcoffset()

    # Convert the offset to hours
    utc_offset_hours = utc_offset.total_seconds() / 3600
    return f"{local_time} (UTC+{int(utc_offset_hours)})"


@ app.callback(
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


@ app.callback(
    ddep.Output('chart-img', 'children'),
    [ddep.Input('graph-type-dropdown', 'value')]
)
def change_image(selected_value):
    if selected_value == 'line':
        return "ssid_chart"
    elif selected_value == 'candlestick':
        return "candlestick_chart"
    elif selected_value == 'area':
        return "area_chart"
    else:
        return "ssid_chart"
