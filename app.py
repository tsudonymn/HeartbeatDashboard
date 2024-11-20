from dash import Dash, html, dash_table, dcc
from Dashboard import DashBoard
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime
import time
from mqtt_client import MQTTHeartbeatClient

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

    # Update interval (updates every 10 seconds)
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # in milliseconds
        n_intervals=0
    )
], fluid=True)


@app.callback(
    Output('dashboard-table', 'data'),
    Input('interval-component', 'n_intervals')
)
def update_table(n):
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
