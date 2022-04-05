import dash_bootstrap_components as dbc
from dash import html, dcc, Dash
from helpers.data_processing import load_data
from helpers.charts import (
    dashboard_summary_numbers,
    plot_last_24_hours,
    plot_last_30_days,
    plot_last_year,
    plot_current,
    plot_last_24_hours_gas,
    plot_last_30_days_gas,
    plot_last_year_gas,
)
from config import DEBUG_MODE


def serve_layout():
    data = load_data()
    return dbc.Container([
        html.H1(children='Youless energy usage monitoring'),
        dashboard_summary_numbers(data),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody(
                    dbc.Tabs([
                        dbc.Tab(label='Current', children=[
                            dcc.Graph(
                                id='current',
                                figure=plot_current(data['minute']),
                                config={
                                    'displayModeBar': False
                                }
                            ),
                        ]),
                        dbc.Tab(label='24 Hours', children=[
                            dcc.Graph(
                                id='last-24-hours',
                                figure=plot_last_24_hours(data['hour']),
                                config={
                                    'displayModeBar': False
                                }
                            ),
                        ]),
                        dbc.Tab(label='30 Days', children=[
                            dcc.Graph(
                                id='last-30-days',
                                figure=plot_last_30_days(data['day']),
                                config={
                                    'displayModeBar': False
                                }
                            ),
                        ])
                    ])
                )), 
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody(dcc.Graph(
                    id='last-365-days',
                    figure=plot_last_year(data['month']),
                    config={
                        'displayModeBar': False
                    }
                )))
            ])
        ]),
    html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody(
                    dbc.Tabs([
                        dbc.Tab(label='24 Hours Gas', children=[
                            dcc.Graph(
                                id='last-24-hours-gas',
                                figure=plot_last_24_hours_gas(data['hourGas']),
                                config={
                                    'displayModeBar': False
                                }
                            ),
                        ]),
                        dbc.Tab(label='30 Days Gas', children=[
                            dcc.Graph(
                                id='last-30-days-gas',
                                figure=plot_last_30_days_gas(data['dayGas']),
                                config={
                                    'displayModeBar': False
                                }
                            ),
                        ])
                    ])
                )), 
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody(dcc.Graph(
                    id='last-365-days-gas',
                    figure=plot_last_year_gas(data['monthGas']),
                    config={
                        'displayModeBar': False
                    }
                )))
            ])
        ])
    ], fluid=True)

       
app = Dash(external_stylesheets=[dbc.themes.FLATLY])

app.title = 'Energy usage monitoring'
app.layout = serve_layout

if __name__ == '__main__':
    app.run_server(debug=DEBUG_MODE, host='0.0.0.0', port='8050')
