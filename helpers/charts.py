

from dash import dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

TEMPLATE = 'simple_white'
GLOBAL_LAYOUT = {
    'font': {'size': 20}, 
    'legend': {
        'orientation': 'h',
        'yanchor': 'bottom',
        'y': 1.02,
        'xanchor': 'right',
        'x': 1
    }
}

def plot_last_24_hours(df_hour):
    df = df_hour.copy()
    df = df.sort_values('time', ascending=False).head(24)

    plots = [            
        go.Bar(x=df['time'], y=df['energy_consumption'], name='Value', text=df['energy_consumption']), 
        go.Scatter(x=df['time'], y=df['avg_energy_consumption'], name='Average', mode='lines')
    ]

    fig =  go.Figure(
        data=plots,
        layout=go.Layout(
            title=go.layout.Title(text="Energy consumption per hour")
        ),
    )
    fig.update_yaxes(title_text='Wh')
    fig.update_layout(template=TEMPLATE, **GLOBAL_LAYOUT)
    return fig

def plot_last_24_hours_gas(df_hour):
    df = df_hour.copy()
    df = df.sort_values('time', ascending=False).head(24)

    plots = [            
        go.Bar(x=df['time'], y=df['energy_consumption'], name='Value', text=df['energy_consumption']), 
        go.Scatter(x=df['time'], y=df['avg_energy_consumption'], name='Average', mode='lines')
    ]

    fig =  go.Figure(
        data=plots,
        layout=go.Layout(
            title=go.layout.Title(text="Energy consumption per hour")
        ),
    )
    fig.update_yaxes(title_text='L')
    fig.update_layout(template=TEMPLATE, **GLOBAL_LAYOUT)
    return fig

def plot_current(df_minute):
    df = df_minute.copy()
    df = df.sort_values('time', ascending=False).head(60*12)

    plots = [            
        go.Bar(x=df['time'], y=df['energy_consumption'], name='Value', marker={
            'color': df['energy_consumption'], 
            'colorscale': [(0, '#00c873'), (0.5, '#ffdf40'), (1, '#fd7103')],
            'cmax': 1000,
            'cmin': 200,
            }), 
        #go.Scatter(x=df['time'], y=df['avg_energy_consumption'], name='Average', mode='lines')
    ]

    fig =  go.Figure(
        data=plots,
        layout=go.Layout(
            title=go.layout.Title(text="Energy consumption per minute")
        )
    )
    fig.update_yaxes(title_text='Watt')
    fig.update_layout(template=TEMPLATE, **GLOBAL_LAYOUT)
    return fig

def plot_last_30_days(df_day):
    df = df_day.copy()
    df = df.sort_values('time', ascending=False).head(30)

    plots = [            
        go.Bar(x=df['time'], y=df['energy_consumption'], name='Value', text=df['energy_consumption']), 
        go.Scatter(x=df['time'], y=df['avg_energy_consumption_weekday'], name='Average (weekday)', mode='lines')
    ]

    fig =  go.Figure(
        data=plots,
        layout=go.Layout(
            title=go.layout.Title(text="Energy consumption last 30 days")
        )
    )

    fig.update_xaxes(
        tickformat="%a %d %b\n%Y"
    )
    fig.update_yaxes(title_text='kWh')
    fig.update_layout(template=TEMPLATE, **GLOBAL_LAYOUT)
    return fig

def plot_last_30_days_gas(df_day_g):
    df = df_day_g.copy()
    df = df.sort_values('time', ascending=False).head(30)

    plots = [            
        go.Bar(x=df['time'], y=df['energy_consumption'], name='Value', text=df['energy_consumption']), 
        go.Scatter(x=df['time'], y=df['avg_energy_consumption_weekday'], name='Average (weekday)', mode='lines')
    ]

    fig =  go.Figure(
        data=plots,
        layout=go.Layout(
            title=go.layout.Title(text="Energy consumption last 30 days")
        )
    )

    fig.update_xaxes(
        tickformat="%a %d %b\n%Y"
    )
    fig.update_yaxes(title_text='m³')
    fig.update_layout(template=TEMPLATE, **GLOBAL_LAYOUT)
    return fig


def plot_last_year(df_month):
    df = df_month.copy()
    df = df.sort_values('time').tail(12)

    plots = [            
        go.Bar(x=df['time'], y=df['energy_consumption'], name='Value', text=round(df['energy_consumption'])), 
    ]

    fig =  go.Figure(
        data=plots,
        layout=go.Layout(
            title=go.layout.Title(text="Energy consumption last 12 months")
        )
    )
    fig.update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y"
    )
    fig.update_yaxes(title_text='kWh')
    fig.update_layout(template=TEMPLATE, **GLOBAL_LAYOUT)
    return fig


def plot_last_year_gas(df_month_g):
    df = df_month_g.copy()
    df = df.sort_values('time').tail(12)

    plots = [            
        go.Bar(x=df['time'], y=df['energy_consumption'], name='Value', text=round(df['energy_consumption'])), 
    ]

    fig =  go.Figure(
        data=plots,
        layout=go.Layout(
            title=go.layout.Title(text="Energy consumption last 12 months")
        )
    )
    fig.update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y"
    )
    fig.update_yaxes(title_text='m³')
    fig.update_layout(template=TEMPLATE, **GLOBAL_LAYOUT)
    return fig


def plot_indicator_trace(title, value, reference=0, mode='number+delta', **kwargs):
    return go.Indicator(
        mode=mode,
        value=value,
        title={'text': title},
        delta={
            'reference': reference, 
            'relative': False, 
            'valueformat':'.1f', 
            'decreasing': {'color': 'green'},
            'increasing': {'color': 'red'},
        },
        **kwargs
    )

def _indicator_card(**kwargs):
    fig = go.Figure(
        plot_indicator_trace(**kwargs)
    )
    fig.update_layout(
        autosize=True,
    )
    return dbc.Card(dbc.CardBody(dcc.Graph(figure=fig)))

def dashboard_summary_numbers(data):
    tmp = data['hour'].sort_values('time', ascending=False).head(24)[['energy_consumption', 'avg_energy_consumption']].sum()
    # In kwh
    last_24h = round(tmp['energy_consumption']/1000, 2)
    last_24h_avg = round(tmp['avg_energy_consumption']/1000, 2)

    tmp = data['day'].sort_values('time', ascending=False).head(30)[['energy_consumption']].sum()
    last_30d = round(tmp['energy_consumption'], 2)
    # We use the average per month of the last year
    tmp = data['month'].sort_values(['year', 'month'], ascending=False).head(12)[['energy_consumption']].mean()
    month_avg = round(tmp['energy_consumption'], 2)

    tmp = data['day'].sort_values('time', ascending=False).head(365)[['energy_consumption']].sum()
    last_365d = round(tmp['energy_consumption'], 2)
    
    
    tmp = data['hourGas'].sort_values('time', ascending=False).head(24)[['energy_consumption', 'avg_energy_consumption']].sum()
    # In m³
    last_24h_g = round(tmp['energy_consumption']/1000, 2)
    last_24h_avg_g = round(tmp['avg_energy_consumption']/1000, 2)
    
    tmp = data['dayGas'].sort_values('time', ascending=False).head(30)[['energy_consumption']].sum()
    last_30d_g = round(tmp['energy_consumption'], 2)
    # We use the average per month of the last year
    tmp = data['monthGas'].sort_values(['year', 'month'], ascending=False).head(12)[['energy_consumption']].mean()
    month_avg_g = round(tmp['energy_consumption'], 2)

    tmp = data['dayGas'].sort_values('time', ascending=False).head(365)[['energy_consumption']].sum()
    last_365d_g = round(tmp['energy_consumption'], 2)

    card_1 = _indicator_card(
        title='Last 24h',
        number = {'suffix': ' kWh'},
        value=last_24h,
        reference=last_24h_avg, 
        domain={'row': 0, 'column': 0},
    )
    card_2 = _indicator_card(
        title='Last 30d',
        number = {'suffix': ' kWh'},
        value=last_30d,
        reference=month_avg, 
        domain={'row': 0, 'column': 1},
    )
    card_3 = _indicator_card(
        title='Last 365d',
        number = {'suffix': ' kWh'},
        value=last_365d,
        domain={'row': 0, 'column': 2},
        mode='number'
    )
    card_4 = _indicator_card(
        title='Last 24h Gas',
        number = {'suffix': ' m³'},
        value=last_24h_g,
        reference=last_24h_avg_g, 
        domain={'row': 0, 'column': 0},
    )
    card_5 = _indicator_card(
        title='Last 30d Gas',
        number = {'suffix': ' m³'},
        value=last_30d_g,
        reference=month_avg_g, 
        domain={'row': 0, 'column': 1},
    )
    card_6 = _indicator_card(
        title='Last 365d Gas',
        number = {'suffix': ' m³'},
        value=last_365d_g,
        domain={'row': 0, 'column': 2},
        mode='number'
    )
    return dbc.Row([
        dbc.Col([card_1], width=6),
        dbc.Col([card_2], width=6),
        dbc.Col([card_3], width=6),
        dbc.Col([card_4], width=6),
        dbc.Col([card_5], width=6),
        dbc.Col([card_6], width=6)
        
    ])

