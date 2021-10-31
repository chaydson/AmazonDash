# Lendo dados
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import shapely.geometry
import numpy as np

# Localização das pastas e documentos
shpfdir = 'shapefiles/'
nome_rios = 'AmazonDrainage.shp'
input_file = 'data/'
shpfdir = 'shapefiles/'
nome_dados = 'MGB-IPH_DischargeData_AmazonBasin.txt'
nome_rios = 'AmazonDrainage.shp'

# Leitura e armazenamento dos dados
rios = gpd.read_file(shpfdir+nome_rios)          # Leitura do shapefile dos rios
Q =  pd.read_csv(input_file+nome_dados, delimiter="\s+",engine='python',header=None) # Leitura da base de dados da vazões
ti='1998-01-01'
tf='2009-12-31'
M = Q

date = pd.date_range(start=ti, end=tf, freq='D') # Criar um dataframe com as datas
day = date.day                                  # Cria uma lista com o dia do mes
month = date.month                                # Cria uma lista com o mes
year = date.year                                 # Cria uma lista com o ano
ano = [x+1 for x in range(year[0]-1,year[len(year)-1])] # cria um array que contém todos os anos de 1998 até 2009

M['date'] = date
M.set_index('date', inplace = True)
Q = Q.values

# Criação de listas para armazenar coordenadas (latitude-longitude) e nomes dos rios
lats = []
lons = []
names = []

for feature, name in zip(rios.geometry,
                         rios.MINI_12):  # Itera uma lista com o nome e coordenadas das bacias (zip cria uma tupla)
    # Verifica se feature é linestrings ou multilinestring e armazena em uma variavel de forma iteravel
    if isinstance(feature, shapely.geometry.linestring.LineString):
        linestrings = [feature]
    elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
        linestrings = feature.geoms

    for linestrings in linestrings:  # Armazena latitude, longitude e nomes em suas respectivas listas
        x, y = linestrings.xy  # Leitura das coordenadas da geometria do rio
        lats = np.append(lats, y)  # Armazena a latitude em uma variável "lats"
        lons = np.append(lons, x)  # Armazena a latitude em uma variável "lons"
        names = np.append(names, [name] * len(y))  # Armazena a nome do rio em uma variável "names"
        lats = np.append(lats, None)  # espaço vazio
        lons = np.append(lons, None)  # espaço vazio
        names = np.append(names, None)  # espaço vazio


mapa = px.line_mapbox(lat=lats, lon=lons, hover_name=names, height=800) # Plotagem dos rios (com plot express)
mapa.update_layout(mapbox_style="white-bg", mapbox_zoom=4, #"open-street-map" - "white-bg" - "stamen-terrain"
                    margin={"r":0,"t":0,"l":0,"b":0},                   # Mapa de fundo
                   mapbox_layers=[
                    {
                        "below": 'traces',
                        "sourcetype": "raster",
                        "sourceattribution": "United States Geological Survey",
                        "source": [
                            "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                        ]
                    }
                    ])


def minmax_graph(rio):
    Qmean = np.zeros(len(ano));
    Ny_days = np.zeros(len(ano))
    Qmax = np.ones(len(ano)) * (-1000000)  # inicializa o array que contém os valores máximos
    Qmin = np.ones(len(ano)) * (1000000)  # inicializa o array que contém os valores mínimos

    for i in range(len(Q)):  # Laço de dias
        iy = year[i] - year[0]
        Qmean[iy] += Q[i][rio];
        Ny_days[iy] += 1
        if Q[i][rio] > Qmax[iy]:  # verifica se o valor atual é maior que o valor anterior
            Qmax[iy] = Q[i][rio]
        if Q[i][rio] < Qmin[iy]:  # verifica se o valor atual é maior que o valor anterior
            Qmin[iy] = Q[i][rio]
    Qmean = Qmean / Ny_days

    minmax = go.Figure(data=[
        go.Scatter(name='Max', x=ano, y=Qmax, marker_color='rgb(55, 83, 109)'),
        go.Scatter(name='Média', x=ano, y=Qmean, marker_color='rgb(30, 11, 255)'),
        go.Scatter(name='Min', x=ano, y=Qmin, marker_color='rgb(26, 118, 255)')])

    # Plotagem
    minmax.update_layout(
        #         title='Vazão mínima, máxima e média anual ',
        #         title_x=0.5,
        xaxis=dict(
            title='ano',
            titlefont_size=16,
            tickfont_size=14,
        ),
        yaxis=dict(
            title='Vazão (m³/s)',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        margin=dict(
            #             l= 50,
            #             r= 50,
            b=10,
            t=10,
            pad=0
        ),
    )

    return minmax


def vazoes_graph(rio):
    #     vazoes = px.line(Q, x=date, y=rio, color_discrete_sequence=['#37536D'], labels=dict(x="Data", y="Vazão"))
    Qmean = np.zeros(len(Q));
    Qmean[:] = sum(Q[:, rio]) / len(Q)
    vazoes = go.Figure(data=[
        go.Scatter(name='Qdiária', x=date, y=Q[:, rio], marker_color='black', line=dict(width=1)),
        go.Scatter(name='Qmédia', x=date, y=Qmean, marker_color='red', line=dict(width=0.7))]
    )

    vazoes.update_layout(title_text='Vazões diárias', title_x=0.5, titlefont_size=24,
                         titlefont_family='Times New Roman',
                         margin=dict(
                             #             l= 50,
                             #             r= 50,
                             b=10,
                             t=40,
                             pad=0
                         ),
                         legend=dict(x=0, y=1.0)
                         )
    vazoes.update_yaxes(
        title='m³/s',
        titlefont_size=16,
        tickfont_size=14,
    )
    vazoes.update_xaxes(
        title='Ano',
        titlefont_size=16,
        tickfont_size=14,
    )
    return vazoes



def media_mensal_graph(rio):
    [Rows, Columns] = Q.shape  # Extrair número de fila (dias) e colunas (rios) da base de dados
    Nmonth = (year[len(year) - 1] - year[
        0] + 1) * 12  # Número total de mêses na base de dados, assumindo que cada ano tem os 12 meses completos
    Qmean_month = []  # Aloca lista com média de cada mês
    date_month = []

    Qtmp = 0;
    Ntmp = 0;
    cdate = 0
    for i in range(1, Rows):  # Laço de dias
        if month[i] == month[i - 1]:
            Qtmp = Qtmp + Q[i, rio]  # Acumula a vazão do mês 'month[i]'
            Ntmp += 1  # Contador do número de dias do mês 'month[i]'
        else:
            if year[i] == year[i - 1]:  # Cria a data onde vai ser plotada minha média mensal
                cdate = str(year[i]) + '-' + str(month[i - 1]) + '-' + str(int(day[i - 1] / 2))
            else:
                cdate = str(year[i - 1]) + '-' + str(month[i - 1]) + '-' + str(int(day[i - 1] / 2))
            date_month.append(cdate)
            Qmean_month.append(Qtmp / Ntmp)
            Qtmp = Q[i, rio];
            Ntmp = 1  # acumula as vazoes do mes; ver os dias de um determinado mes

    # Definição das variáveis para a plotagem
    data_i = [go.Scatter(x=date_month,
                         y=Qmean_month,
                         marker={'color': 'blue',
                                 'line': {'color': '#FFFFFF',
                                          'width': 1}
                                 },
                         opacity=0.6)]

    # Layout
    configuracoes_layout = go.Layout(yaxis={'title': 'm³/s'},
                                     margin=dict(
                                         #             l= 50,
                                         #             r= 50,
                                         b=10,
                                         t=10,
                                         pad=0
                                     ),
                                     )
    #                                      xaxis={'title':'Meses'})
    # figura
    media_mensal = go.Figure(data=data_i, layout=configuracoes_layout)
    return media_mensal

def ciclo_anual_graph(rio):
    [Rows, Columns] = Q.shape  # Extrair número de fila (dias) e colunas (rios) da base de dados
    Nmonth = 12  # Número de mêses num ano
    Qmonth = np.zeros(Nmonth)  # Aloca lista com média de cada mês
    Qmmax = np.ones(Nmonth) * (-1000000)  # Aloca lista com máxima de cada mês
    Qmmin = np.ones(Nmonth) * (1000000)  # Aloca lista com mínima de cada mês
    Count_days = np.zeros(Nmonth)  # Aloca lista com No. de dias de cada mês
    # for river in range(Columns):  # Laço de Rios
    for i in range(Rows):  # Laço de dias
        mi = month[i] - 1  # Indice do mes 'month[i]'
        Qmonth[mi] = Qmonth[mi] + Q[i, rio]  # Acumula a vazão do mês 'month[i]'
        Count_days[mi] += 1  # Contador do número de dias do mês 'month[i]'
        if Q[i, rio] > Qmmax[mi]:
            Qmmax[mi] = Q[i, rio]
        if Q[i, rio] < Qmmin[mi]:
            Qmmin[mi] = Q[i, rio]
    Qmonth = Qmonth / Count_days  # Faz a média

    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    ciclo_anual = go.Figure([go.Scatter(
        x=meses,
        y=Qmonth,
        line=dict(color='blue'),
        #                                         mode='lines',
        showlegend=False
    ),
        go.Scatter(
            x=meses,  # x, then x reversed
            y=Qmmax,  # upper, then lower reversed
            mode='lines',
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False
        ),
        go.Scatter(
            x=meses,  # x, then x reversed
            y=Qmmin,  # upper, then lower reversed
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        ),
    ]
    )
    ciclo_anual.update_layout(
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='m³/s',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        margin=dict(
            #             l= 50,
            #             r= 50,
            b=50,
            t=10,
            pad=0
        ),
        barmode='group',
        bargap=0.15,  # espaço entre barras de coordenadas de localização adjacentes.
        bargroupgap=0.1  # espaço entre as barras da mesma coordenada de localização.
    )

    return ciclo_anual


def desvio_media(rio):
    Qmean = np.zeros(len(ano));
    Qdesv = np.zeros(len(ano));
    Ny_days = np.zeros(len(ano))  # lista que armazenas as medias que serão plotadas

    for i in range(len(Q)):  # Laço de dias
        iy = year[i] - year[0]
        Qmean[iy] += Q[i][rio];
        Ny_days[iy] += 1
    Qmean = Qmean / Ny_days
    for i in range(len(Q)):  # Laço de dias
        iy = year[i] - year[0]
        Qdesv[iy] = Qdesv[iy] + (Q[i][rio] - Qmean[iy]) ** 2
    Qdesv = (Qdesv / (Ny_days - 1)) ** 0.5

    trace3 = go.Scatter(x=ano, y=Qdesv, mode='markers+lines', name='Desvio padrão anual',
                        marker_color='blue')  # define os desvios padrões anuais em y e a cor da linha
    trace2 = go.Scatter(x=ano, y=Qmean, mode='markers+lines', name='Media anual',
                        marker_color='grey')  # define as médias anuais como sendo y e a cor da linha
    # define o título do gráfico e os títulos dos eixos
    layout = go.Layout(yaxis={'title': 'm³/s'},
                       #                        xaxis={'title': 'Ano'},
                       legend=dict(
                           x=0,
                           y=1.0,
                           bgcolor='rgba(255, 255, 255, 0)',
                           bordercolor='rgba(255, 255, 255, 0)'),
                       margin=dict(t=10, b=50, pad=0)
                       )
    data = [trace3, trace2]  # define as variáveis que serão plotadas
    desvio = go.Figure(data=data, layout=layout)
    return desvio


def vazoes_extremas(rio):  # define a função do dash
    va = 0;
    vb = 0
    Qmean = 0;
    Qdesv = 0;
    Ndays = len(Q)  # lista que armazenas as medias que serão plotadas
    Qmean = sum(Q[:, rio]) / Ndays
    Qdesv = (sum((Q[:, rio] - Qmean) ** 2) / Ndays) ** 0.5

    for i in range(
            len(Q)):  # laço de repetição para percorrer as colunas e separar os dias das vazões acima e abaixo da média.
        if Q[i][rio] > (
                Qmean + Qdesv * 2):  # condicional para separar os dias de vazão acima da média mais duas vezes o desvio padrão.
            va += 1  # armazena a quantidade de dias que a vazão foi maior que média.
        elif Q[i][rio] < (Qmean - Qdesv):  # condicional para separar os dias de vazão abaixo da média.
            vb += 1  # armazena a quantidade de dias que a vazão foi menor que média menos  o desvio padrão.
    x = (len(Q) - (
                va + vb))  # subtrai a soma entre va e vb do total de vazões par saber quantas vazões não estão acima ou abaixo da média com o desvio padrão

    # o gráfico de pizza irá mostrar o total de vazões acima e abaixo da média levando em conta o desvio padrão e também as vazõews que não ficaram nem acima e nem abaixo em cinza
    labels = ['Acima de Qméd anual', 'Abaixo de Qméd anual', 'Vazões Restantes']  # subtítulos do gráfico.
    values = [va, vb, x]  # armazena na variável values a lista dos valores obtidos.
    night_colors = ['blue', 'purple', 'grey']  # altera as cores do gráfico de pizza de acordo com os parâmetros.
    vazoes_ext = go.Figure(data=[go.Pie(labels=labels, values=values,
                                        marker_colors=night_colors)])  # armazena na variável fig a configuração do gráfico.
    vazoes_ext.update_layout(  # atualiza o layout do gráfico.
        #         title_text="Eventos extremos", # adiciona título.
        height=150,
        margin=dict(t=0, b=0, l=0, r=0)),  # adiciona a sigla DVMMMA no meio do gráfico.
    vazoes_ext.update_traces(hole=.4,
                             hoverinfo="label+percent+name")  # configura o tamanho da circunferência no interior do gráfico.
    return vazoes_ext

informacoes = dict([(i, [a, b]) for i, a, b in zip(rios['MINI_12'], rios['Area_km2'], rios['Length_km'])])


def tabela(rio):
    cod = rio['points'][0]['hovertext']
    lat = rio['points'][0]['lat']
    lon = rio['points'][0]['lon']

    area = informacoes[cod][0]
    comprimento = informacoes[cod][1]

    info = go.Figure(
        data=[go.Table(header=dict(values=['Informações do rio'], font=dict(color='black'), align=['left']),
                       cells=dict(values=[['CÓDIGO', 'Latitude', 'Longitude', 'Área (km²)', 'Comprimento (km)'],
                                          [cod, lat, lon, area, comprimento]], align=['left', 'right'],
                                  font=dict(color='black')))
              ])
    info.update_layout(margin=dict(r=0, t=0, b=0))
    return info

rio_inicial = {'points': [{'lon': -60.46041666669555, 'lat': 4.764583333458063, 'hovertext': 1}]}
tabela(rio_inicial)

import json
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.5'}]
                )
#server=app.server

mapa.update_layout(clickmode='event+select')

GRAPH_STYLE = {
    'width': 900,
    'height': 300
}

MAP_STYLE = {
    'border-radius': 100,
    'overflow': 'hidden',
#   'border': '1px solid',
    'height': 800,
    'width': 400
}

NAV_STYLE = {
    'justify-content': 'center',
}

H2_STYLE = {
    'textAlign': 'center',
    'color': "#0e0872"
}

TABLE_STYLE = {
    'height': 130,
    'width': 400
}

NAV = dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Máx/Média/Mín anual", active="exact", href="/minmax")),
                    dbc.NavItem(dbc.NavLink("Média mensal", active="exact", href="/")),
                    dbc.NavItem(dbc.NavLink("Climatologia", active="exact", href="/ciclo")),
                    dbc.NavItem(dbc.NavLink("Média e desvio padraõ", active="exact", href="/desvio"))
                ],pills=True, style=NAV_STYLE)

app.layout = dbc.Container([
    html.H2("VAZÕES SIMULADAS NA BACIA AMAZÔNICA", style=H2_STYLE, className='mt-3 mb-3'),
    dbc.Row([
        dcc.Location(id="url"),
        dbc.Col(dcc.Graph(id='mapa',figure=mapa), style=MAP_STYLE, className='mt-3'),
        dbc.Col([
            dcc.Graph(id='vazoes',figure=vazoes_graph(0), style=GRAPH_STYLE),
            NAV,
            html.Div(id="page-content", style=GRAPH_STYLE),
            dbc.Row([
                dbc.Col(dcc.Graph(id='tabela', figure=tabela(rio_inicial), style=TABLE_STYLE)),
                dbc.Col(dcc.Graph(id='rosquinha', figure=vazoes_extremas(0), style={'width': 400, 'margin-top':0}))
            ])
        ])
    ])
], fluid=True)


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)

def render_page_content(pathname):
    if pathname == "/":
        return dcc.Graph(id='media_mensal',figure=media_mensal_graph(0), style=GRAPH_STYLE)
    elif pathname == "/ciclo":
        return dcc.Graph(id='ciclo_anual',figure=ciclo_anual_graph(0), style=GRAPH_STYLE)
    elif pathname == "/desvio":
        return dcc.Graph(id='desvio',figure=desvio_media(0), style=GRAPH_STYLE)
    elif pathname == "/minmax":
        return dcc.Graph(id='minmax',figure=minmax_graph(0), style=GRAPH_STYLE)

@app.callback(
    Output('mapa', 'children'),
    Input('mapa', 'clickData'))
def display_click_data(clickData):
    print(clickData)
    return json.dumps(clickData, indent=2)

@app.callback(
    Output('tabela', 'figure'),
    Input('mapa', 'children'))
def atualizar_tabela(rio):
    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',rio)
    rio = json.loads(rio)
    print('YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',rio)
    print('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ',rio['points'][0]['hovertext'])
    return tabela(rio)

@app.callback(
    Output('vazoes', 'figure'),
    Input('mapa', 'children'))
def atualizar_vazoes(rio):
    rio = json.loads(rio)
    rio = int(float(rio['points'][0]['hovertext']) - 1.0)
    return vazoes_graph(rio)

@app.callback(
    Output('media_mensal', 'figure'),
    Input('mapa', 'children'))
def atualizar_medias_mensais(rio):
    rio = json.loads(rio)
    rio = int(float(rio['points'][0]['hovertext']) - 1.0)
    return media_mensal_graph(rio)

@app.callback(
    Output('desvio', 'figure'),
    Input('mapa', 'children'))
def atualizar_desvio_media(rio):
    rio = json.loads(rio)
    rio = int(float(rio['points'][0]['hovertext']) - 1.0)
    return desvio_media(rio)

@app.callback(
    Output('rosquinha', 'figure'),
    Input('mapa', 'children'))
def atualizar_rosquinha(rio):
    rio = json.loads(rio)
    rio = int(float(rio['points'][0]['hovertext']) - 1.0)
    return vazoes_extremas(rio)

@app.callback(
    Output('ciclo_anual', 'figure'),
    Input('mapa', 'children'))
def atualizar_ciclo_anual(rio):
    rio = json.loads(rio)
    rio = int(float(rio['points'][0]['hovertext']) - 1.0)
    return ciclo_anual_graph(rio)

@app.callback(
    Output('minmax', 'figure'),
    Input('mapa', 'children'))
def atualizar_minmax(rio):
    rio = json.loads(rio)
    rio = int(float(rio['points'][0]['hovertext']) - 1.0)
    return minmax_graph(rio)

if __name__ == '__main__':
    app.run_server(debug=False)

