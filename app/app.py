# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 16:24:10 2023

@author: danid
"""

import dash
from dash import dcc  # dash core components
from dash import html # dash html components
from dash.dependencies import Input, Output
import requests
import json
import os
import pandas as pd
import plotly.express as px
from loguru import logger

app = dash.Dash(__name__)
server = app.server

# PREDICTION API URL 
api_url = os.getenv('API_URL')
api_url = "http://{}:8000/api/predict".format(api_url)

# Load data from csv
def load_data():
    d=pd.read_csv("./datos.csv", low_memory=False)
    d=d[['sector', 'valor_del_contrato', 'objeto_del_contrato']]
    d_agr_rec=d.groupby(by="sector").sum()['valor_del_contrato']
    d_agr_con=d.groupby(by="sector").count()['objeto_del_contrato']
    d_def=pd.concat([d_agr_rec, d_agr_con], axis=1)
    return d_def    

# Cargar datos
data = load_data()

data["valor_del_contrato"]=round(data["valor_del_contrato"]/1000000000, 2)

fig_1 = px.bar(data, x=data.index, y="objeto_del_contrato",
               title="NÚMERO DE CONTRATOS Y RECURSOS POR <br> DELEGADA SECTORIAL", text_auto=True)

fig_1.update_layout(xaxis_title="SECTOR",
                    yaxis_title="NÚMERO DE CONTRATOS",
                    font_color="#52AD9C",
                    title_font_color="#52AD9C",
                    title_x=0.5)


fig_1.update_xaxes(visible=False, showticklabels=False)
fig_1.update_yaxes(showgrid=True, gridwidth=0.25, 
                   gridcolor='#9FFCDF')


fig_2 = px.bar(data, x=data.index, y="valor_del_contrato", text_auto=True)

fig_2.update_layout(xaxis_title="SECTOR",
                    yaxis_title="RECURSOS <br> EN MILES DE MILLONES",
                    font_color="#52AD9C",
                    title_font_color="#52AD9C",
                    title_x=0.5)

fig_2.update_xaxes(showgrid=True, gridwidth=0.25, 
                   gridcolor='#9FFCDF')

fig_2.update_yaxes(showgrid=True, gridwidth=0.25, 
                   gridcolor='#9FFCDF')

app.layout = html.Div([
    html.H4('SECTORIZACIÓN DE LA CONTRATACIÓN PÚBLICA EN COLOMBIA - 2023', 
            style={"font-family": "Helvetica",
                   "text-align": "left", 
                   "color": "blue", 
                   "margin-top": "50px", 
                   "margin-left": "10px", 
                   "font-size": "50px"}),
    html.H4('A continuación puede ingresar el objeto del contrato', 
            style={"font-family": "Helvetica",
                   "text-align": "left", 
                   "color": "gray", 
                   "font-size": "30px"}),
    
    dcc.Input(id="input", type="text", 
              style={"width":"75%" , 
                     "padding": "12px 20px",
                     "box-sizing": "border-box",
                     "border-radius": "4px",
                     "border": "2px solid blue", 
                     "background-color": "#A0B9C6", 
                     "color": "white"}), 
    
    html.Br(),
    
    html.H6(html.Div(id='resultado'), 
            style={"font-family": "Helvetica",
                   "text-align": "center", 
                   "color": "red", 
                   "font-size": "30px"}),
    
    
    dcc.Graph(id="graph_1", figure=fig_1,
              style={'width': '70%', 
                     'display': 'inline-block',
                     "margin-top":"30px"}),
    
    dcc.Graph(id="graph_2", figure=fig_2,
              style={'width': '70%', 
                     'display': 'inline-block',
                     }),
])

@app.callback(
    Output(component_id='resultado', component_property='children'),
    [Input(component_id='input', component_property='value')]
)
def update_output_div(input_value):
    if input_value is None or input_value.strip() == '':
        return None 
    else:
       input_w=f'"{input_value}"'
       myreq = {
        "inputs": 
            {
               "text": input_w
            }
      }
       headers =  {"Content-Type":"application/json", "accept": "application/json"}

       # POST call to the API
       response = requests.post(api_url, data=json.dumps(myreq), headers=headers)
       data = response.json()
       logger.info("Response: {}".format(data))

       # Pick result to return from json format
       result =data
       
       return f'Ha ingresado: {result}' 

if __name__ == "__main__":
    app.run_server(debug=True)
