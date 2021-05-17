import pandas as pd
import sys
import mmh3
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.COSMO])
server = app.server
server.secret_key = os.environ.get(‘SECRET_KEY’, ‘my-secret-key’)


w = 10
h = 3
# ---------------------------------------------------------------
dff = pd.DataFrame(pd.DataFrame([[i + 1] + [0] * w for i in range(h)]))

dff = dff.rename({0: 'Hash Functions'}, axis=1)
# ---------------------------------------------------------------
app.layout = (html.Div([dbc.Row([
    html.Br(),
    dbc.Col(html.Pre(id="title", children="Count Min Sketch",
                     style={'text-align': 'center', 'font-size': '40px', 'font-family': 'Verdana'}), )]),
    html.Br(),
    # dbc.Col(html.Div(id="text",children="Add values to see how the sketch updates the count"),width={'offset':1}),
    dbc.Row([
        dbc.Col(
            dash_table.DataTable(
                id='cms',
                data=dff.to_dict('records'),
                columns=[
                    {"name": str(i), "id": str(i), "type": 'numeric', 'deletable': False, "selectable": False} for i in
                    dff.columns
                ],
                editable=False,
                style_data_conditional=[],
                style_cell_conditional=[{
                    'if': {'column_id': 'Hash Functions'},
                    'width': '10%',
                    'backgroundColor': 'grey',
                    'color': 'white'
                }]
                ,
                row_deletable=False,
                style_cell={'width':'7.5%','textAlign': 'center'}
            ), width={'size': 10, 'offset': 1})

    ], className='row-table'),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dcc.Input(
                id='input',
                type='text',
                placeholder="Insert number/word",
                readOnly=False,
                disabled=False,
                debounce=True,
                n_submit=0,
                autoFocus=True,
                value='',
                style={'width': '100%%', 'text-align': 'left', 'border-radius': 4},

            ),
            width={'size': 2, 'offset': 1, 'text-align': 'center'}
        ),
        dbc.Col(
            html.Button(id='add-button', type='submit', n_clicks=0, n_clicks_timestamp=-1, children="Increment Count",
                        style={'background-colour': 'white', "width": '80%',
                               'border-radius': 4}),
            width={'size': 2}
        )
    ]
    ),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dcc.Input(
                id='input-get-count',
                type='text',
                placeholder="Insert number/word",
                readOnly=False,
                disabled=False,
                debounce=True,
                n_submit=0,
                autoFocus=False,
                value='',
                style={'width': '100%%', 'text-align': 'left', 'border-radius': 4},

            ),
            width={'size': 2, 'offset': 1, 'text-align': 'center'}
        ),
        dbc.Col(
            html.Button(id='get-button', type='submit', n_clicks=0, children="Get Count",
                        style={"width": '80%',
                               'border-radius': 4}),
            width={'size': 2}
        )

    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            html.Pre(id='Count-text', children="Count =",
                     style={"width": '100%', 'border-radius': 4, 'font-size': '20px', 'font-family': 'Verdana'}),
            width={'size': 1, 'offset': 1}
        ),
        dbc.Col(
            dcc.Input(
                id='output',
                type='text',
                placeholder="Count",
                readOnly=True,
                disabled=False,
                debounce=False,
                n_submit=0,
                autoFocus=False,
                value='0',
                style={'width': '30%%', 'text-align': 'left', 'border-radius': 4},

            ),
            width={'size': 1, 'offset': 0, 'text-align': 'center', "width": '30%'}
        ),
    ])
]))


@app.callback(
    [Output(component_id='cms', component_property='data'),
     Output(component_id='cms', component_property='style_data_conditional'),
     Output(component_id='input', component_property='n_submit'),
     Output(component_id='add-button', component_property='n_clicks'),
     Output(component_id='input', component_property='value')],
    [Input(component_id='cms', component_property='data'),
     Input(component_id='add-button', component_property='n_clicks'),
     Input(component_id='input', component_property='n_submit')],
    [State(component_id='input', component_property='value')]
)
def update_output(df, num_submit, num_click, input_value):
    style_data_conditional = []
    if (num_submit and input_value) or num_click:
        for i in range(h):
            index = mmh3.hash(input_value, i) % w
            df[i][str(index + 1)] = df[i][str(index + 1)] + 1
            style_data_conditional.append({
            'if': {
                'row_index': i,
                'column_id': '{}'.format(index+1)
            },
            'color': 'tomato',
            'backgroundColor':'#DDDDDD',
            'fontWeight': 'bold'
        },)
        return df, style_data_conditional, 0, 0, ''
    return df, style_data_conditional, num_submit, num_click, input_value


@app.callback(
    [Output(component_id='output', component_property='value'),
     Output(component_id='input-get-count', component_property='n_submit'),
     Output(component_id='get-button', component_property='n_clicks')],
    [Input(component_id='cms', component_property='data'),
     Input(component_id='input-get-count', component_property='n_submit'),
     Input(component_id='get-button', component_property='n_clicks'),
     Input(component_id='output', component_property='value')],
    [State(component_id='input-get-count', component_property='value')]
)
def update_output(df, input_submit, button_submit, count_value, input_value):
    minimum = sys.maxsize
    if ((input_submit and input_value) or button_submit) and input_value != '':
        for i in range(h):
            index = mmh3.hash(input_value, i) % w
            if df[i][str(index + 1)] < minimum:
                minimum = df[i][str(index + 1)]
        count_value = minimum
        num_submit = 0
        input_submit = 0
    return [count_value, button_submit, input_submit]


# ------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
