import pandas as pd
import sys
import mmh3
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import os

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
server = app.server
server.secret_key = os.environ.get('SECRET_KEY', 'my-secret-key')
w = 10
h = 4
# ---------------------------------------------------------------
sketch_dataframe = pd.DataFrame([[i + 1] + [0] * w for i in range(h)])
sketch_dataframe = sketch_dataframe.rename({0: 'Hash Functions'}, axis=1)
# ---------------------------------------------------------------

actual_dataframe = pd.DataFrame(columns=['Element', 'Count'])

# ---------------------------------------------------------------
app.layout = html.Div([
    html.Div([dbc.Row([
        html.Br(),
        dbc.Col(html.Div("Count Min Sketch",id="title",
                         style={'text-align': 'center', 'font-size': '150%', "font-weight":'bold'}), )]),
        html.Br(),
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    id='cms',
                    data=sketch_dataframe.to_dict('records'),
                    columns=[
                        {"name": str(i), "id": str(i), "type": 'numeric', 'deletable': False, "selectable": False} for i
                        in
                        sketch_dataframe.columns
                    ],
                    editable=False,
                    style_data_conditional=[],
                    style_cell_conditional=[{
                        'if': {'column_id': 'Hash Functions'},
                        'width': '10%',
                        'backgroundColor': 'grey',
                        'color': 'white',
                        'font-weight':'bold'
                    }]
                    ,
                    row_deletable=False,
                    style_cell={'width': '7.5%', 'textAlign': 'center'}
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
                    style={'width': '100%%', 'text-align': 'left', 'border-radius': 4, 'font-family': 'Verdana'},

                ),
                width={'size': 3, 'offset': 1, 'text-align': 'center'}
            ),
            dbc.Col(
                html.Button(id='add-button', type='submit', n_clicks=0, n_clicks_timestamp=-1,
                            children="Increment Count",
                            style={'background-colour': 'white', "width": '100%',
                                   'border-radius': 4, 'font-family': 'Verdana'}),
                width={'size': 3}
            ),
        ]),
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
                    style={'width': '100%%', 'text-align': 'left', 'horizontalAlign': 'left', 'border-radius': 4,
                           'font-family': 'Verdana'},

                ),
                width={'size': 3, 'offset': 1, 'text-align': 'center'}
            ),
            dbc.Col(
                html.Button(id='get-button', type='submit', n_clicks=0, children="Get Count",
                            style={"width": '100%',
                                   'horizontalAlign': 'left',
                                   'border-radius': 4, 'font-family': 'Verdana'}),
                width={'size': 3}
            ),
            dbc.Col(
                html.Pre(id='Count-text', children="Count =",
                         style={"width": '100%', 'border-radius': 4, 'font-size': '100%', 'font-family': 'Verdana',
                                'text-align': 'right'}),
                width={'size': 2, 'offset': 0}
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
                    style={'width': '100%', 'text-align': 'left', 'border-radius': 4, 'horizontalAlign': 'left',
                           'font-family': 'Verdana'},

                ),
                width={'size': 1, 'offset': 0, 'text-align': 'left', "width": '100%', 'horizontalAlign': 'left'}
            ),
        ]),
        html.Br(),
    ], style={"border":"2px brown solid",'margin':'50px'}),
    html.Div([
        html.Br(),
        dbc.Row([
            html.Br(),
            dbc.Col(html.Div("Actual Counts",id="title-2",
                             style={'text-align': 'center', 'font-size': '150%',  "font-weight":'bold'}),
                    ), ]),
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    id='actual_count',
                    data=actual_dataframe.to_dict('records'),
                    columns=[
                        {"name": str(i), "id": str(i), "type": 'text', 'deletable': False, "selectable": False} for i in
                        actual_dataframe.columns
                    ],
                    editable=False,
                    row_deletable=False,
                    style_cell={'width': '50%', 'textAlign': 'center'}
                ), width={'size': 4, 'offset': 4})

        ], className='row-table-2'),
        html.Br()
    ],style={"border":"2px brown solid",'margin':'50px'}
    )
])


@app.callback(
    [Output(component_id='cms', component_property='data'),
     Output(component_id='actual_count', component_property='data'),
     Output(component_id='cms', component_property='style_data_conditional'),
     Output(component_id='input', component_property='n_submit'),
     Output(component_id='add-button', component_property='n_clicks'),
     Output(component_id='input', component_property='value')],
    [Input(component_id='cms', component_property='data'),
     Input(component_id='actual_count', component_property='data'),
     Input(component_id='add-button', component_property='n_clicks'),
     Input(component_id='input', component_property='n_submit')],
    [State(component_id='input', component_property='value')]
)
def update_output(df_cms, df_actual, num_submit, num_click, input_value):
    style_data_conditional = []
    if (num_submit and input_value) or num_click:
        # update records
        for i in range(h):
            index = mmh3.hash(input_value, i) % w
            df_cms[i][str(index + 1)] = df_cms[i][str(index + 1)] + 1
            style_data_conditional.append({
                'if': {
                    'row_index': i,
                    'column_id': '{}'.format(index + 1)
                },
                'color': 'tomato',
                'backgroundColor': '#DDDDDD',
                'fontWeight': 'bold'
            }, )

        df_actual = pd.DataFrame(df_actual, columns=['Element', 'Count'])
        if input_value in df_actual['Element'].values:
            df_actual.loc[df_actual['Element'] == input_value, 'Count'] += 1
        else:
            df_actual = df_actual.append({'Element': input_value, 'Count': 1}, ignore_index=True)
        print(df_actual)
        df_actual = df_actual.sort_values(by=['Count'], ascending=False)
        df_actual = df_actual.to_dict('records')

        return df_cms, df_actual, style_data_conditional, 0, 0, ''
    return df_cms, df_actual, style_data_conditional, num_submit, num_click, input_value


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
