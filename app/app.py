# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 16:24:10 2023

@author: danid
"""

import dash
from dash import dcc  # dash core components
from dash import html # dash html components
from dash.dependencies import Input, Output, State
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
api_url = "http://{}:8002/predict/".format(api_url)

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
    html.Br(),
    html.Button('Haga clic para obtener el sector', id='boton', 
                style={"font-family": "Helvetica",
                       'font-size': 20, 
                        'text-align': "center", 
                        'width': '200px', 
                        'margin-left': '550px'} ),
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
    [Input(component_id='boton', component_property='n_clicks')],
    [State(component_id='input', component_property='value')],
    prevent_initial_call=True
)
def update_output_div(n_clicks, input_value):
    if n_clicks is None:
        return dash.no_update
    
    if input_value is None or input_value.strip() == '':
        return None 
    else:
       myreq = {
               "text": input_value
               }
       headers =  {"Content-Type":"application/json", "accept": "application/json"}

       # POST call to the API
       try:
           response = requests.post(api_url, data=json.dumps(myreq), headers=headers)
           response.raise_for_status()
           data = response.json()
           logger.info("Response: {}".format(data))
           cluster_label = data.get("cluster_label")
           label=""
           if cluster_label == 11: 
               label="PRESTACIÓN DE SERVICIOS"
           elif cluster_label==22: 
               label="SALUD"
           else:
               label= "OTROS"

           if cluster_label is not None:
                result = "EL SECTOR CORRESPONDIENTE ES: " + label
           else:
                result = "La respuesta no tiene la clave 'cluster_label'."
       except requests.exceptions.RequestException as e:
            logger.error("Error en la solicitud a la API: {}".format(e))
            result = "Error al comunicarse con la API."
       except json.decoder.JSONDecodeError as e:
            logger.error("Error al decodificar la respuesta JSON: {}".format(e))
            result = "Error al procesar la respuesta JSON de la API."
    
    return json.dumps(myreq) + "    " + result + "    " 

if __name__ == "__main__":
    app.run_server(debug=True)
