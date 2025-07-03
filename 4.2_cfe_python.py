import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

df = pd.read_csv("gastos_luz_espanol.csv")
df['Fecha'] = pd.to_datetime(df['Fecha'])
df['Mes'] = df['Fecha'].dt.to_period('M').astype(str)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("Dashboard de Consumo Eléctrico", className="text-center my-4"),
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='proveedor-filter',
            options=[{'label': p, 'value': p} for p in df['Proveedor'].unique()],
            value=None, placeholder="Filtrar por Proveedor"
        ), md=6),
        dbc.Col(dcc.DatePickerRange(
            id='date-filter',
            start_date=df['Fecha'].min(),
            end_date=df['Fecha'].max(),
            display_format='YYYY-MM-DD'
        ), md=6),
    ], className='mb-4'),

    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("Consumo Total (kWh)"),
                          dbc.CardBody(html.H4(id='consumo-total'))]), md=3),
        dbc.Col(dbc.Card([dbc.CardHeader("Costo Total (MXN)"),
                          dbc.CardBody(html.H4(id='costo-total'))]), md=3),
        dbc.Col(dbc.Card([dbc.CardHeader("Promedio Mensual"),
                          dbc.CardBody(html.H4(id='promedio-mensual'))]), md=3),
        dbc.Col(dbc.Card([dbc.CardHeader("Precio Promedio por kWh"),
                          dbc.CardBody(html.H4(id='precio-promedio'))]), md=3),
    ], className='mb-4'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='grafica-linea'), md=6),
        dbc.Col(dcc.Graph(id='grafica-puntos'), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafica-barras'), md=6),
        dbc.Col(dcc.Graph(id='grafica-tendencia'), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafica-horaspico'), md=6),
        dbc.Col(dcc.Graph(id='grafica-pastel'), md=6),
    ])
], fluid=True)

@app.callback(
    Output('consumo-total', 'children'),
    Output('costo-total', 'children'),
    Output('promedio-mensual', 'children'),
    Output('precio-promedio', 'children'),
    Output('grafica-linea', 'figure'),
    Output('grafica-puntos', 'figure'),
    Output('grafica-barras', 'figure'),
    Output('grafica-tendencia', 'figure'),
    Output('grafica-horaspico', 'figure'),
    Output('grafica-pastel', 'figure'),
    Input('proveedor-filter', 'value'),
    Input('date-filter', 'start_date'),
    Input('date-filter', 'end_date')
)
def actualizar_dashboard(proveedor, start_date, end_date):
    dff = df.copy()
    if proveedor:
        dff = dff[dff['Proveedor'] == proveedor]
    dff = dff[(dff['Fecha'] >= start_date) & (dff['Fecha'] <= end_date)]

    consumo_total = f"{dff['Consumo_kWh'].sum():,.2f}"
    costo_total = f"${dff['Costo_Total_MXN'].sum():,.2f}"
    promedio_mensual = f"${dff.groupby('Mes')['Costo_Total_MXN'].sum().mean():,.2f}"
    precio_promedio = f"${dff['Costo_por_kWh_MXN'].mean():.2f}"

    fig_linea = px.line(dff.groupby('Mes').sum(numeric_only=True).reset_index(),
                        x='Mes', y='Consumo_kWh', title='Consumo Mensual')

    fig_puntos = px.scatter(dff, x='Consumo_kWh', y='Costo_Total_MXN',
                            color='Proveedor', title='Costo vs. Consumo')

    fig_barras = px.bar(dff.groupby('Proveedor').sum(numeric_only=True).reset_index(),
                        x='Proveedor', y='Consumo_kWh', title='Consumo por Proveedor')

    fig_tendencia = px.line(dff.groupby('Mes').sum(numeric_only=True).reset_index(),
                            x='Mes', y='Costo_Total_MXN', title='Tendencia de Costos')

    fig_horas = px.bar(dff, x='Fecha', y=['Horas_Pico_kWh', 'Consumo_kWh'],
                       title='Horas Pico vs Total kWh', barmode='group')

    fig_pastel = px.pie(dff, values='Costo_Total_MXN', names='Proveedor',
                        title='Distribución de Costos por Proveedor')

    return consumo_total, costo_total, promedio_mensual, precio_promedio, \
        fig_linea, fig_puntos, fig_barras, fig_tendencia, fig_horas, fig_pastel

if __name__ == "__main__":
    #app.run_server(debug=True, port=8051)
    app.run(debug=True, port=8051)

