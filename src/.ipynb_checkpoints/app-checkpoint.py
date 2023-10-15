import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output # dcc - Dash core components

df = pd.read_excel('./data/bike-counter-annarbor.xlsx', skiprows=3, names=['datetime','in','out'])

df_weather = pd.read_csv("./data/weather-annarbor.csv", 
                         parse_dates=['DATE'],
                         usecols = ['DATE', 'PRCP', 'TMAX', 'TMIN']
                        )


df_weather.set_index('DATE').head()

app = Dash(__name__) # mnake an instance of the dashboard application

# specify the layout of the dashboard
app.layout = html.Div([
    
    html.H1(children=["Bicycle Traffic Dashboard"]),
    
    html.H2(children=dcc.Markdown("Location: [Division St. Ann Arbor, MI](https://www.bing.com/maps?&mepi=23~~TopOfPage~LargeMapLink&ty=18&q=N%20Division%20St%2C%20Ann%20Arbor%2C%20MI%2048104&ppois=42.2813264500011_-83.7438906000112_N%20Division%20St%2C%20Ann%20Arbor%2C%20MI%2048104_~&cp=42.281326~-83.743891&v=2&sV=1&FORM=MIRE&qpvt=Division+St.+Ann+Arbor)")),
    
    dcc.DatePickerRange(id='date_range',
                        start_date='2023-05-01',
                        end_date='2023-09-16',
                       ),
    
    dcc.RadioItems(id='data_res',
                   options={"1_week": "Weekly",
                            "1_day": "Daily",
                            "1_hour": "Hourly"
                           },
                   
                   value='1_day', #default
                   inline = True
                   
                  ),
    
    dcc.Graph(id='trend_graph'),
])

# specify the callback function

@app.callback(
    
    Output(component_id='trend_graph', component_property='figure'),
    Input(component_id='date_range', component_property='start_date'),
    Input(component_id='date_range', component_property='end_date'),
    Input(component_id='data_res', component_property='value'),
)

def update_figure(start_date, end_date, data_res_value):

    if data_res_value == '1_week':
        rule = 'W'
        
    elif data_res_value == '1_day':
        rule = 'd'
        
    elif data_res_value == '1_hour':
        rule = 'H'
    
    df_updated = (
        
        df
          .set_index('datetime')
          .resample(rule)
          .sum()
          .assign
            (
                total = lambda x: x['in'] +x['out'],

                  day_of_week = lambda x: x.index.day_name()
             )

          .loc[start_date:end_date]
          .join(df_weather.set_index('DATE'))
    )
    
    fig = px.bar(df_updated,
                 x=df_updated.index,
                 y='total',
                 hover_data=['in', 'out', 'day_of_week', 'TMAX', 'TMIN', 'PRCP'],
                )
    
    return fig
    

if __name__ == '__main__':
    
    app.run(jupyter_mode='external')