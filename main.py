import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html

from dash_table import DataTable, FormatTemplate
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 1. Clean and read data:
df = pd.read_json('http://20.83.163.174:8000/api/v1/claims_test', orient='table')
# path = os.path.join(os.path.dirname(__file__), 'static/claims_test.csv')
# df = pd.read_csv(path)
df['MONTH'] = df['MONTH'].apply(str)
df['YEAR'] = df['MONTH'].str.slice(0, 4)
df['MONTH'] = df['MONTH'].str.slice(4, 6)
df = df[~df['MONTH'].str.contains('00')]  # Eliminate unknown months
df['FOR_TOTAL'] = 'FOR_TOTAL'

# 2. Year Total
dff = pd.pivot_table(df, values='PAID_AMOUNT', index=['FOR_TOTAL'], columns=['YEAR'], aggfunc=np.sum)

# 3.1 Monthly Total:
dff_1 = pd.pivot_table(df, values='PAID_AMOUNT', index=['MONTH'], columns=['YEAR'], aggfunc=np.sum)
dff_1 = pd.DataFrame(dff_1.to_records())

# 3.2 Monthly Expenses Comparison
line_2018 = df[df['YEAR'] == '2018']
line_2019 = df[df['YEAR'] == '2019']
line_2020 = df[df['YEAR'] == '2020']

line_2018_update = df[df['YEAR'] == '2018']
line_2019_update = df[df['YEAR'] == '2019']
line_2020_update = df[df['YEAR'] == '2020']

line_2018 = line_2018.groupby('MONTH').agg('sum')
line_2019 = line_2019.groupby('MONTH').agg('sum')
line_2020 = line_2020.groupby('MONTH').agg('sum')

# 3.3 Monthly Expenses % Distribution from Year Total
dff_2 = df.groupby(['YEAR', 'MONTH']).agg(
    {"PAID_AMOUNT": "sum"}
).groupby(level=0).apply(
    lambda x:
    x / x.sum()
).unstack().to_records()

dff_temp = []
for row in dff_2:
    dff_temp.append(list(row))

dff_2 = pd.DataFrame(dff_temp, columns=[
    'YEAR', 'Jan %', 'Feb %',
    'Mar %', 'Apr %',
    'May %', 'Jun %',
    'Jul %', 'Aug %',
    'Sep %', 'Oct %',
    'Nov %', 'Dec %'
])

# 4.1 Annual Expenses by Service Category:
dff_3 = df.groupby(['YEAR', 'SERVICE_CATEGORY'])['PAID_AMOUNT'].agg('sum').unstack().to_records()

dff_temp = []
for row in dff_3:
    dff_temp.append(list(row))

dff_3 = pd.DataFrame(dff_temp, columns=[
    'YEAR', 'ASCServices', 'AncillaryFFS',
    'ERServices', 'InpatientServices',
    'OutpatientServices', 'PCPEncounter',
    'PCPFFS', 'SNFServices',
    'SpecialistFFS', 'SpecialistsFFS'
])

# 4.2 Annual Expenses % Distribution from Year Total
dff_4 = df.groupby(['YEAR', 'SERVICE_CATEGORY']).agg(
    {"PAID_AMOUNT": "sum"}
).groupby(level=0).apply(
    lambda x:
    x / x.sum()
).unstack().to_records()

dff_temp = []
for row in dff_4:
    dff_temp.append(list(row))

dff_4 = pd.DataFrame(dff_temp, columns=[
    'YEAR', 'ASCServices %', 'AncillaryFFS %',
    'ERServices %', 'InpatientServices %',
    'OutpatientServices %', 'PCPEncounter %',
    'PCPFFS %', 'SNFServices %',
    'SpecialistFFS %', 'SpecialistsFFS %'
])

# 5.1 Annual Expenses by Service Category:
dff_5 = df.groupby(['YEAR', 'PAYER'])['PAID_AMOUNT'].agg('sum').unstack().to_records()

dff_temp = []
for row in dff_5:
    dff_temp.append(list(row))

dff_5 = pd.DataFrame(dff_temp, columns=[
    'YEAR', 'Payer B', 'Payer CA',
    'Payer CO', 'Payer F',
    'Payer H', 'Payer O',
    'Payer S', 'Payer UL',
    'Payer UN', 'Payer W'
])

# 5.2 Annual Expenses - % Distribution from Year Total
dff_6 = df.groupby(['YEAR', 'PAYER']).agg(
    {"PAID_AMOUNT": "sum"}
).groupby(level=0).apply(
    lambda x:
    x / x.sum()
).unstack().to_records()

dff_temp = []
for row in dff_6:
    dff_temp.append(list(row))

dff_6 = pd.DataFrame(dff_temp, columns=[
    'YEAR', 'Payer B %', 'Payer CA %',
    'Payer CO %', 'Payer F %',
    'Payer H %', 'Payer O %',
    'Payer S %', 'Payer UL %',
    'Payer UN %', 'Payer W %'
])

# 6.1 Top 10 most expensive medical services by claim specialty
df_2018 = df[df['YEAR'] == '2018'].groupby('CLAIM_SPECIALTY').agg('sum').sort_values(by='PAID_AMOUNT',
                                                                                     ascending=False).head(10)
df_2019 = df[df['YEAR'] == '2019'].groupby('CLAIM_SPECIALTY').agg('sum').sort_values(by='PAID_AMOUNT',
                                                                                     ascending=False).head(10)
df_2020 = df[df['YEAR'] == '2020'].groupby('CLAIM_SPECIALTY').agg('sum').sort_values(by='PAID_AMOUNT',
                                                                                     ascending=False).head(10)

df_2018['rn_2018'] = df_2018.rank(method='first')
df_2019['rn_2019'] = df_2019.rank(method='first')
df_2020['rn_2020'] = df_2020.rank(method='first')

df_2018.set_index('rn_2018')
df_2019.set_index('rn_2019')
df_2020.set_index('rn_2020')

df_2018 = df_2018.rename(columns={'PAID_AMOUNT': '2018'})
df_2019 = df_2019.rename(columns={'PAID_AMOUNT': '2019'})
df_2020 = df_2020.rename(columns={'PAID_AMOUNT': '2020'})
df_2018 = df_2018.rename(columns={'CLAIM_SPECIALTY': 'CLAIM_SPECIALTY_2018'})
df_2019 = df_2019.rename(columns={'CLAIM_SPECIALTY': 'CLAIM_SPECIALTY_2019'})
df_2020 = df_2020.rename(columns={'CLAIM_SPECIALTY': 'CLAIM_SPECIALTY_2020'})

dff_7 = pd.concat([df_2018, df_2019, df_2020], axis=1, ignore_index=False).to_records()

dff_temp = []
for row in dff_7:
    dff_temp.append(list(row))

dff_7 = pd.DataFrame(dff_temp, columns=[
    'CLAIM_SPECIALTY', '2018', 'rn_2018',
    '2019', 'rn_2019',
    '2020', 'rn_2020'
])

# 6.2 Top 10 most expensive medical services by claim specialty - % distribution
df_2018_ = df[df['YEAR'] == '2018'].groupby('CLAIM_SPECIALTY').agg('sum').sort_values(by='PAID_AMOUNT',
                                                                                      ascending=False).head(10)
df_2018_['YEAR'] = '2018'
df_2018_ = df_2018_.groupby(['YEAR', 'CLAIM_SPECIALTY']).agg(
    {"PAID_AMOUNT": "sum"}
).groupby(level=0).apply(
    lambda x:
    x / x.sum()
).unstack()

df_2019_ = df[df['YEAR'] == '2019'].groupby('CLAIM_SPECIALTY').agg('sum').sort_values(by='PAID_AMOUNT',
                                                                                      ascending=False).head(10)
df_2019_['YEAR'] = '2019'
df_2019_ = df_2019_.groupby(['YEAR', 'CLAIM_SPECIALTY']).agg(
    {"PAID_AMOUNT": "sum"}
).groupby(level=0).apply(
    lambda x:
    x / x.sum()
).unstack()

df_2020_ = df[df['YEAR'] == '2020'].groupby('CLAIM_SPECIALTY').agg('sum').sort_values(by='PAID_AMOUNT',
                                                                                      ascending=False).head(10)
df_2020_['YEAR'] = '2020'
df_2020_ = df_2020_.groupby(['YEAR', 'CLAIM_SPECIALTY']).agg(
    {"PAID_AMOUNT": "sum"}
).groupby(level=0).apply(
    lambda x:
    x / x.sum()
).unstack()

dff_8 = pd.concat([df_2018_, df_2019_, df_2020_], axis=0).to_records()
dff_temp = []
for row in dff_8:
    dff_temp.append(list(row))

dff_8 = pd.DataFrame(dff_temp, columns=[
    'YEAR', 'AMBULANCE %', 'CARDIOLOGY %',
    'HEMATOLOGY/ONCOLOGY %', 'HOSPITAL %',
    'Hospital %', 'INP %', 'INTERNAL MEDICINE %',
    'MEDICAL DOCTOR %', 'OUT %',
    'RADIOLOGY %', 'SNF %'
])


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def Header():
    return html.Div([
        get_header(),
        html.Br([]),
    ])


def get_header():
    header = html.Div([

        html.Div([
            html.H1(
                'Sergey Kim. Novapulsar Test Task')
        ], className="twelve columns padded"),

        html.Div([
            html.P(
                'Date: 12 April 2021')
        ], className="twelve columns padded"),

        html.Div([
            html.P(
                'Contact:')
        ], className="twelve columns padded"),

        html.Div([
            html.P(
                'Full name - Sergey Kim')
        ], className="twelve columns padded"),

        html.Div([
            html.P(
                'Tel.: +7 (705) 229-37-37')
        ], className="twelve columns padded"),

        html.Div([
            html.P(
                'E-mail: srgykim@gmail.com')
        ], className="twelve columns padded")
    ], className="row gs-header gs-text-header")
    return header


money = FormatTemplate.money(0)
percentage = FormatTemplate.percentage(2)

app.layout = html.Div([

    html.Div([
        Header(),

        html.Div([

            html.Div([
                html.H2('Report Summary',
                        className="gs-header gs-text-header padded"),

                html.P("\
                            This report describes expenses for medical services from Jan 2018 till July 2020. \
                            Medical services are provided by several departments. They are AncillaryFFS, ASCServices, \
                            ERServices, InpatientServices, OutpatientServices, PCPEncounter, PCPFFS, SNFServices, \
                            SpecialistFFS, SpecialistsFFS"),

            ], className="six columns"),

            html.Div([
                html.H2(["Year Total: all service categories, claim specialties and payers"],
                        className="gs-header gs-table-header padded"),
                dash_table.DataTable(
                    id='table-year-total',
                    columns=[
                        dict(id='2018', name='2018', type='numeric', format=money),
                        dict(id='2019', name='2019', type='numeric', format=money),
                        dict(id='2020', name='2020', type='numeric', format=money)
                    ],
                    data=dff.to_dict('records'),
                    style_data={'border': '1px solid blue'},
                    style_header={'border': '1px solid pink', 'text-align': 'center'}
                ),
            ], className="six columns"),

            html.Div([
                html.H2(["Monthly Total: all service categories, claim specialties and payers"],
                        className="gs-header gs-table-header padded"),
                dash_table.DataTable(
                    id='table-monthly-total',
                    columns=[
                        dict(id='MONTH', name='MONTH'),
                        dict(id='2018', name='2018', type='numeric', format=money),
                        dict(id='2019', name='2019', type='numeric', format=money),
                        dict(id='2020', name='2020', type='numeric', format=money)
                    ],
                    data=dff_1.to_dict('records'),
                    style_data={'border': '1px solid blue'},
                    style_header={'border': '1px solid pink', 'text-align': 'center'}
                ),
            ], className="six columns"),

            html.Br(),

            html.H2(["Expenses Comparison: chosen service category and payer"],
                        className="gs-header gs-table-header padded"),

            dcc.Dropdown(id='service-category-dropdown',
                         options=[{'label': x, 'value': x} for x in
                                  df.sort_values('SERVICE_CATEGORY')['SERVICE_CATEGORY'].unique()],
                         value='InpatientServices',
                         multi=False,
                         disabled=False,
                         clearable=True,
                         searchable=True,
                         placeholder='Choose Service Category',
                         className='form-dropdown',
                         style={'width': "90%"},
                         persistence='string',
                         persistence_type='memory'),

            html.Br(),

            dcc.Dropdown(id='payer-dropdown',
                         options=[{'label': x, 'value': x} for x in
                                  df.sort_values('PAYER')['PAYER'].unique()],
                         value='Payer F',
                         multi=False,
                         disabled=False,
                         clearable=True,
                         searchable=True,
                         placeholder='Choose Payer',
                         className='form-dropdown',
                         style={'width': "90%"},
                         persistence='string',
                         persistence_type='memory'),
            html.Div([
                dcc.Graph(
                    id='expenses-comparison-graph'
                ),
            ], className="six columns"),

            html.Div([
                html.H2(["Expenses Comparison: all service categories, claim specialties and payers"],
                        className="gs-header gs-table-header padded"),
                dcc.Graph(
                    id='expenses-comparison-graph-year-total',
                    figure={
                        'data': [
                            {'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                             'y': [val for sublist in line_2018.values.tolist() for val in sublist], 'type': 'line',
                             'name': '2018'},
                            {'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                             'y': [val for sublist in line_2019.values.tolist() for val in sublist], 'type': 'line',
                             'name': '2019'},
                            {'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                             'y': [val for sublist in line_2020.values.tolist() for val in sublist], 'type': 'line',
                             'name': '2020'}
                        ],
                        'layout': {
                            'title': 'Monthly Expenses Comparison Jan 18 - Jul 20'
                        }
                    }
                ),
            ], className="six columns"),

            html.Div([
                html.H2(["Monthly Expenses % Distribution from Year Total"],
                        className="gs-header gs-table-header padded"),
                dash_table.DataTable(
                    id='table-monthly-distr',
                    columns=[
                        dict(id='YEAR', name='YEAR'),
                        dict(id='Jan %', name='Jan %', type='numeric', format=percentage),
                        dict(id='Feb %', name='Feb %', type='numeric', format=percentage),
                        dict(id='Mar %', name='Mar %', type='numeric', format=percentage),
                        dict(id='Apr %', name='Apr %', type='numeric', format=percentage),
                        dict(id='May %', name='May %', type='numeric', format=percentage),
                        dict(id='Jun %', name='Jun %', type='numeric', format=percentage),
                        dict(id='Jul %', name='Jul %', type='numeric', format=percentage),
                        dict(id='Aug %', name='Aug %', type='numeric', format=percentage),
                        dict(id='Sep %', name='Sep %', type='numeric', format=percentage),
                        dict(id='Oct %', name='Oct %', type='numeric', format=percentage),
                        dict(id='Nov %', name='Nov %', type='numeric', format=percentage),
                        dict(id='Dec %', name='Dec %', type='numeric', format=percentage)
                    ],
                    data=dff_2.to_dict('records'),
                    style_data={'border': '1px solid blue'},
                    style_header={'border': '1px solid pink', 'text-align': 'center'}
                ),
            ], className="six columns"),

            html.Div([
                html.H2(["Annual Expenses by Service Category"],
                        className="gs-header gs-table-header padded"),
                dash_table.DataTable(
                    id='table-annual-by-service-category',
                    columns=[
                        dict(id='YEAR', name='YEAR'),
                        dict(id='ASCServices', name='ASCServices', type='numeric', format=money),
                        dict(id='AncillaryFFS', name='AncillaryFFS', type='numeric', format=money),
                        dict(id='ERServices', name='ERServices', type='numeric', format=money),
                        dict(id='InpatientServices', name='InpatientServices', type='numeric', format=money),
                        dict(id='OutpatientServices', name='OutpatientServices', type='numeric', format=money),
                        dict(id='PCPEncounter', name='PCPEncounter', type='numeric', format=money),
                        dict(id='PCPFFS', name='PCPFFS', type='numeric', format=money),
                        dict(id='SNFServices', name='SNFServices', type='numeric', format=money),
                        dict(id='SpecialistFFS', name='SpecialistFFS', type='numeric', format=money),
                        dict(id='SpecialistsFFS', name='SpecialistsFFS', type='numeric', format=money)
                    ],
                    data=dff_3.to_dict('records'),
                    style_data={'border': '1px solid blue'},
                    style_header={'border': '1px solid pink', 'text-align': 'center'}
                ),
            ], className="six columns"),

            html.Div([
                html.H2(["Annual Expenses % Distribution from Year Total"],
                        className="gs-header gs-table-header padded"),
                dash_table.DataTable(
                    id='table-annual-by-service-category-distr',
                    columns=[
                        dict(id='YEAR', name='YEAR'),
                        dict(id='ASCServices %', name='ASCServices %', type='numeric', format=percentage),
                        dict(id='AncillaryFFS %', name='AncillaryFFS %', type='numeric', format=percentage),
                        dict(id='ERServices %', name='ERServices %', type='numeric', format=percentage),
                        dict(id='InpatientServices %', name='InpatientServices %', type='numeric', format=percentage),
                        dict(id='OutpatientServices %', name='OutpatientServices %', type='numeric', format=percentage),
                        dict(id='PCPEncounter %', name='PCPEncounter %', type='numeric', format=percentage),
                        dict(id='PCPFFS %', name='PCPFFS %', type='numeric', format=percentage),
                        dict(id='SNFServices %', name='SNFServices %', type='numeric', format=percentage),
                        dict(id='SpecialistFFS %', name='SpecialistFFS %', type='numeric', format=percentage),
                        dict(id='SpecialistsFFS %', name='SpecialistsFFS %', type='numeric', format=percentage)
                    ],
                    data=dff_4.to_dict('records'),
                    style_data={'border': '1px solid blue'},
                    style_header={'border': '1px solid pink', 'text-align': 'center'}
                ),
            ], className="six columns"),

            html.Div([
                html.H2(["Annual Expenses by Payer"],
                        className="gs-header gs-table-header padded"),
                dash_table.DataTable(
                    id='table-annual-by-payer',
                    columns=[
                        dict(id='YEAR', name='YEAR'),
                        dict(id='Payer B', name='Payer B', type='numeric', format=money),
                        dict(id='Payer CA', name='Payer CA', type='numeric', format=money),
                        dict(id='Payer CO', name='Payer CO', type='numeric', format=money),
                        dict(id='Payer F', name='Payer F', type='numeric', format=money),
                        dict(id='Payer H', name='Payer H', type='numeric', format=money),
                        dict(id='Payer O', name='Payer O', type='numeric', format=money),
                        dict(id='Payer S', name='Payer S', type='numeric', format=money),
                        dict(id='Payer UL', name='Payer UL', type='numeric', format=money),
                        dict(id='Payer UN', name='Payer UN', type='numeric', format=money),
                        dict(id='Payer W', name='Payer W', type='numeric', format=money)
                    ],
                    data=dff_5.to_dict('records'),
                    style_data={'border': '1px solid blue'},
                    style_header={'border': '1px solid pink', 'text-align': 'center'}
                ),
            ], className="six columns"),

            html.Div([
                html.H2(["Annual Expenses by Payer - % Distribution from Year Total"],
                        className="gs-header gs-table-header padded"),
                dash_table.DataTable(
                    id='table-annual-by-payer-distr',
                    columns=[
                        dict(id='YEAR', name='YEAR'),
                        dict(id='Payer B %', name='Payer B %', type='numeric', format=percentage),
                        dict(id='Payer CA %', name='Payer CA %', type='numeric', format=percentage),
                        dict(id='Payer CO %', name='Payer CO %', type='numeric', format=percentage),
                        dict(id='Payer F %', name='Payer F %', type='numeric', format=percentage),
                        dict(id='Payer H %', name='Payer H %', type='numeric', format=percentage),
                        dict(id='Payer O %', name='Payer O %', type='numeric', format=percentage),
                        dict(id='Payer S %', name='Payer S %', type='numeric', format=percentage),
                        dict(id='Payer UL %', name='Payer UL %', type='numeric', format=percentage),
                        dict(id='Payer UN %', name='Payer UN %', type='numeric', format=percentage),
                        dict(id='Payer W %', name='Payer W %', type='numeric', format=percentage)
                    ],
                    data=dff_6.to_dict('records'),
                    style_data={'border': '1px solid blue'},
                    style_header={'border': '1px solid pink', 'text-align': 'center'}
                ),
            ], className="six columns"),

            html.Div([
                html.H2(["Top 10 Most Expensive Medical Services by Claim Specialty"],
                        className="gs-header gs-table-header padded"),
                dash_table.DataTable(
                    id='table-top-10-by-claim-specialty',
                    columns=[
                        dict(id='CLAIM_SPECIALTY', name='CLAIM_SPECIALTY'),
                        dict(id='2018', name='2018', type='numeric', format=money),
                        dict(id='rn_2018', name='Top 2018'),
                        dict(id='2019', name='2019', type='numeric', format=money),
                        dict(id='rn_2019', name='Top 2019'),
                        dict(id='2020', name='2020', type='numeric', format=money),
                        dict(id='rn_2020', name='Top 2020'),
                    ],
                    data=dff_7.to_dict('records'),
                    style_data={'border': '1px solid blue'},
                    style_header={'border': '1px solid pink', 'text-align': 'center'}
                ),
            ], className="six columns"),

            html.Div([
                html.H2(["Top 10 Most Expensive Medical Services by Claim Specialty % Distribution"],
                        className="gs-header gs-table-header padded"),
                dash_table.DataTable(
                    id='table-top-10-by-claim-specialty-distr',
                    columns=[
                        dict(id='YEAR', name='YEAR'),
                        dict(id='AMBULANCE %', name='AMBULANCE %', type='numeric', format=percentage),
                        dict(id='CARDIOLOGY %', name='CARDIOLOGY %', type='numeric', format=percentage),
                        dict(id='HEMATOLOGY/ONCOLOGY %', name='HEMATOLOGY/ONCOLOGY %', type='numeric',
                             format=percentage),
                        dict(id='HOSPITAL %', name='HOSPITAL %', type='numeric', format=percentage),
                        dict(id='Hospital %', name='Hospital %', type='numeric', format=percentage),
                        dict(id='INP %', name='INP %', type='numeric', format=percentage),
                        dict(id='INTERNAL MEDICINE %', name='INTERNAL MEDICINE %', type='numeric', format=percentage),
                        dict(id='MEDICAL DOCTOR %', name='MEDICAL DOCTOR %', type='numeric', format=percentage),
                        dict(id='OUT %', name='OUT %', type='numeric', format=percentage),
                        dict(id='RADIOLOGY %', name='RADIOLOGY %', type='numeric', format=percentage),
                        dict(id='SNF %', name='SNF %', type='numeric', format=percentage)
                    ],
                    data=dff_8.to_dict('records'),
                    style_data={'border': '1px solid blue'},
                    style_header={'border': '1px solid pink', 'text-align': 'center'}
                ),
            ], className="six columns")
        ], className="row "),
    ], className="subpage")

], className="page")


# ------------------------------------------------------------------
@app.callback(
    [Output('expenses-comparison-graph', 'figure')],
    [Input('service-category-dropdown', 'value'),
     Input('payer-dropdown', 'value')]
)
def update_data(service_category_dropdown, payer_dropdown):
    line_2018_update_ = line_2018_update[line_2018_update['SERVICE_CATEGORY'] == service_category_dropdown]
    line_2019_update_ = line_2019_update[line_2019_update['SERVICE_CATEGORY'] == service_category_dropdown]
    line_2020_update_ = line_2020_update[line_2020_update['SERVICE_CATEGORY'] == service_category_dropdown]

    line_2018_update_ = line_2018_update_[line_2018_update_['PAYER'] == payer_dropdown]
    line_2019_update_ = line_2019_update_[line_2019_update_['PAYER'] == payer_dropdown]
    line_2020_update_ = line_2020_update_[line_2020_update_['PAYER'] == payer_dropdown]

    line_2018_ = pd.DataFrame(line_2018_update_.groupby('MONTH').agg('sum').to_records(), columns=['MONTH', 'PAID_AMOUNT'])
    line_2019_ = pd.DataFrame(line_2019_update_.groupby('MONTH').agg('sum').to_records(), columns=['MONTH', 'PAID_AMOUNT'])
    line_2020_ = pd.DataFrame(line_2020_update_.groupby('MONTH').agg('sum').to_records(), columns=['MONTH', 'PAID_AMOUNT'])

    line_chart = go.Figure()

    line_chart.add_trace(go.Scatter(x=line_2018_['MONTH'], y=line_2018_['PAID_AMOUNT'],
                                    mode='lines+markers',
                                    name='2018'))

    line_chart.add_trace(go.Scatter(x=line_2019_['MONTH'], y=line_2019_['PAID_AMOUNT'],
                                    mode='lines+markers',
                                    name='2019'))

    line_chart.add_trace(go.Scatter(x=line_2020_['MONTH'], y=line_2019_['PAID_AMOUNT'],
                                    mode='lines+markers',
                                    name='2020'))

    line_chart.update_layout(uirevision='foo')

    return [line_chart]


# ------------------------------------------------------------------


if __name__ == '__main__':
    app.run_server(debug=True)
