from dash import Dash, html, dash_table, dcc
from Dashboard import DashBoard
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime, timedelta
import time
from mqtt_client import MQTTHeartbeatClient

# Time window options in seconds
TIME_WINDOWS = {
    0: 3600,        # 1 hour
    1: 86400,       # 1 day
    2: 604800,      # 1 week
    3: 1209600,     # 2 weeks
    4: 2592000      # 30 days
}

TIME_WINDOW_LABELS = {
    0: "1 Hour",
    1: "1 Day",
    2: "1 Week",
    3: "2 Weeks",
    4: "1 Month"
}

# Initialize the Dash app with a Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Initialize your Dashboard
dashboard = DashBoard()

# Initialize and start MQTT client
mqtt_client = MQTTHeartbeatClient(dashboard)
mqtt_client.start()

# Layout of the app
app.layout = dbc.Container([
    html.H1("Device Heartbeat Dashboard", className="text-center my-4"),

    # Settings Row
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Dashboard Settings", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Heartbeat Interval (seconds)"),
                            dbc.Input(
                                id="heartbeat-interval",
                                type="number",
                                value=10,
                                min=1,
                                step=1
                            ),
                        ], width=6),
                        dbc.Col([
                            html.Label("Uptime Window"),
                            dcc.Slider(
                                id="uptime-window",
                                min=0,
                                max=4,
                                step=1,
                                value=0,
                                marks=TIME_WINDOW_LABELS
                            ),
                        ], width=6),
                    ]),
                    dbc.Button(
                        "Update Settings",
                        id="update-settings",
                        color="primary",
                        className="mt-3"
                    ),
                ])
            ], className="mb-4")
        ])
    ]),

    # Data table
    dash_table.DataTable(
        id='dashboard-table',
        columns=[
            {'name': 'Device ID', 'id': 'device_id'},
            {'name': 'Last Seen', 'id': 'last_seen'},
            {'name': 'Uptime (%)', 'id': 'uptime'}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'uptime', 'filter_query': '{uptime} >= 90'},
                'color': 'green'
            },
            {
                'if': {'column_id': 'uptime', 'filter_query': '{uptime} < 90'},
                'color': 'orange'
            },
            {
                'if': {'column_id': 'uptime', 'filter_query': '{uptime} < 50'},
                'color': 'red'
            }
        ]
    ),

    # Update interval
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # in milliseconds
        n_intervals=0
    )
], fluid=True)


@app.callback(
    Output('dashboard-table', 'data'),
    Input('interval-component', 'n_intervals'),
    Input('update-settings', 'n_clicks'),
    State('heartbeat-interval', 'value'),
    State('uptime-window', 'value')
)
def update_table(n, n_clicks, heartbeat_interval, uptime_window_index):
    # Update dashboard settings if they've changed
    if heartbeat_interval and uptime_window_index is not None:
        dashboard.heartbeat_interval = heartbeat_interval
        dashboard.uptime_window = TIME_WINDOWS[uptime_window_index]

    # Get the DataFrame from your Dashboard
    df = dashboard.generateViewFrame()
    
    # Convert the DataFrame to records
    records = df.to_dict('records')
    
    # Format the timestamps in the records
    for record in records:
        if 'last_seen' in record:
            record['last_seen'] = record['last_seen'].strftime('%Y-%m-%d %H:%M:%S %Z')
    
    return records


if __name__ == '__main__':
    try:
        app.run_server(debug=True)
    finally:
        # Ensure MQTT client is properly stopped when the app exits
        mqtt_client.stop()
