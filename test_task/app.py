from datetime import (
    datetime,
)

import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import (
    Input,
    Output,
    State,
    dcc,
    html,
)
from dash.exceptions import (
    PreventUpdate,
)
from dash_extensions.enrich import (
    DashProxy,
    MultiplexerTransform,
    ServersideOutputTransform,
)
from database import (
    DataCollector,
)

from test_task.ui_components import (
    MainPageUICreator,
)

CARD_STYLE = {
    'withBorder': True,
    'shadow': "sm",
    'radius': "md",
    'style': {'height': '500px'}
}

flex_input_style = {'display': 'flex', 'align-items': 'center'}
dropdown_style = {'width': '200px', 'searchable': False}


class EncostDash(DashProxy):
    def __init__(self, **kwargs):
        self.app_container = None
        super().__init__(transforms=[ServersideOutputTransform(),
                                     MultiplexerTransform()], **kwargs)


app = EncostDash(name=__name__)


def get_main_layout():
    """Основной шаблон для фильтрации.

    Returns:
        Div: html-разметка для фильтрации.
    """

    return html.Div([
        dmc.Paper([
            dmc.Grid([
                dmc.Col([
                    dmc.Card([
                        html.H1(
                            [
                                f'Клиент: ',
                                dmc.Select(
                                    data=dataframe['client_name'].unique(),
                                    id="client_name_select",
                                )
                            ],
                            style=flex_input_style,
                        ),
                        dmc.Text(
                            children=[
                                dmc.Text(
                                    [
                                        f'Точка учета: ',
                                        dmc.Select(
                                            id='endpoint_name_select',
                                        )
                                    ],
                                    style=flex_input_style,
                                ),
                                dmc.Text(
                                    [
                                        f'Сменный день:',
                                        dcc.Dropdown(
                                            id='shift_day_select',
                                            style=dropdown_style,
                                        ),
                                    ],
                                    style=flex_input_style,
                                ),
                                dmc.Text(
                                    [
                                        f'Начало периода: ',
                                        dcc.Dropdown(
                                            id='state_begin_select',
                                            style=dropdown_style,
                                        )
                                    ],
                                    style=flex_input_style,
                                ),
                                dmc.Text(
                                    [
                                        f'Конец периода: ',
                                        dcc.Dropdown(
                                            id='state_end_select',
                                            style=dropdown_style,
                                        )
                                    ],
                                    style=flex_input_style,
                                ),
                            ],
                            weight=600,
                        ),
                        dmc.Button(
                            'Собрать',
                            id='confirm_form',
                        ),
                        html.Div(id='output'),
                    ],
                        **CARD_STYLE
                    ),
                ], span=6),
            ], gutter="xl", )
        ])
    ], id='body')


def get_layout(ui_creator):
    """Шаблон с отрисовкой главной страницы.

    Args:
        ui_creator (MainPageUICreator): Класс создателя ui-компонентов.
    Returns:
        Div: html-разметка для главной страницы.
    """

    global states_duration_diagram

    reasons_pie = ui_creator.get_reasons_pie()
    states_duration_diagram = ui_creator.get_states_duration_diagram()

    return html.Div([
        dmc.Paper([
            dmc.Grid([
                dmc.Col([
                    dmc.Card([
                        html.H1(f'Клиент: {ui_creator.get_first_client_name()}'),
                        dmc.Text(
                            children=[
                                dmc.Text(f'Сменный день: {ui_creator.get_shift_day()}'),
                                dmc.Text(f'Точка учета: {ui_creator.get_endpoint_name()}'),
                                dmc.Text(f'Начало периода: {ui_creator.get_state_begin()}'),
                                dmc.Text(f'Конец периода: {ui_creator.get_state_end()}'),
                            ],
                            weight=600,
                        ),
                        dmc.MultiSelect(
                            id="states_filter",
                            data=dataframe['state'].unique(),
                            clearable=True,
                            style={"width": 400, "marginBottom": 10},
                        ),
                        dmc.Button(
                            'Фильтровать',
                            id='filter_button',
                        ),
                        dmc.Button(
                            'К настройкам',
                            id='settings_button',
                        ),
                        html.Div(id='output'),
                    ],
                        **CARD_STYLE
                    ),
                ], span=6),
                dmc.Col([
                    dmc.Card([
                        dcc.Graph(
                            id='reason_pie',
                            figure=reasons_pie,
                        )],
                        **CARD_STYLE)
                ], span=6),
                dmc.Col([
                    dmc.Card([
                        dcc.Graph(
                            id='states_duration_diagram',
                            figure=states_duration_diagram,
                        )],
                        **CARD_STYLE)
                ], span=12),
            ], gutter="xl", )
        ])
    ], id='body',
    )


@app.callback(
    Output('endpoint_name_select', 'data'),
    Input('client_name_select', 'value'),
    prevent_initial_call=True,
)
def select_client_name(client_name):
    """Коллбек при выборе имени клиента.
    Фильтрует датафрейм по client_name и обновляет endpoint_name_select."""

    if client_name is None:
        raise PreventUpdate

    filtered_dataframe = dataframe[dataframe['client_name'] == client_name]

    endpoint_names = filtered_dataframe['endpoint_name'].unique()

    return endpoint_names


@app.callback(
    Output('shift_day_select', 'options'),
    Input('endpoint_name_select', 'value'),
)
def select_endpoint_name(endpoint_name):
    """Коллбек при выборе точки учета.
    Фильтрует датафрейм по endpoint_name и обновляет shift_day_select."""

    if endpoint_name is None:
        raise PreventUpdate

    filtered_dataframe = dataframe[dataframe['endpoint_name'] == endpoint_name]

    shift_days = filtered_dataframe['shift_day'].unique()

    shift_day_options = [{'label': day.strftime('%Y-%m-%d'), 'value': day} for day in shift_days]

    return shift_day_options


@app.callback(
    Output('state_begin_select', 'options'),
    Output('state_end_select', 'options'),
    Input('shift_day_select', 'value'),
    prevent_initial_call=True,
)
def select_shift_day(shift_day):
    """Коллбек при выборе дня смены.
    Фильтрует датафрейм по shift_day и обновляет state_begin_select и state_end_select."""

    if shift_day is None:
        raise PreventUpdate

    shift_day = datetime.strptime(shift_day, '%Y-%m-%d')
    filtered_dataframe = dataframe[dataframe['shift_day'] == shift_day.date()]

    # Здесь в качестве теста
    state_min = filtered_dataframe['state_begin'].min()
    state_max = filtered_dataframe['state_end'].max()

    state_begin_options = [{
        'label': state_min.strftime('%H:%M:%S (%d.%m)'),
        'value': state_min,
    }]

    state_end_options = [{
        'label': state_max.strftime('%H:%M:%S (%d.%m)'),
        'value': state_max,
    }]

    return state_begin_options, state_end_options


@app.callback(
    Output('body', 'children'),
    Output('output', 'children'),
    Input('confirm_form', 'n_clicks'),
    State('client_name_select', 'value'),
    State('endpoint_name_select', 'value'),
    State('shift_day_select', 'value'),
    State('state_begin_select', 'value'),
    State('state_end_select', 'value'),
    prevent_initial_call=True,
)
def confirm_button(click, *args):
    """Коллбек нажатия на кнопку 'Собрать'.
    Фильтрует датафрейм по всем параметрам."""

    if click is None:
        raise PreventUpdate

    client_name, endpoint_name, shift_day, state_begin, state_end = args

    if not all((client_name, endpoint_name, shift_day, state_begin, state_end)):
        return dash.no_update, dmc.Text(
            'Заполните все поля', style={'color': 'red'}
        )

    shift_day = datetime.strptime(shift_day, '%Y-%m-%d')
    state_begin = pd.to_datetime(state_begin)
    state_end = pd.to_datetime(state_end)

    dataframe_filtered = dataframe[
        (dataframe['client_name'] == client_name) &
        (dataframe['endpoint_name'] == endpoint_name) &
        (dataframe['shift_day'] == shift_day.date()) &
        (dataframe['state_begin'] >= state_begin) &
        (dataframe['state_end'] <= state_end)
    ]

    if dataframe_filtered.empty:
        return dash.no_update, dmc.Text(
            'По заданным параметрам не найдено данных', style={'color': 'red'}
        )

    ui_creator = MainPageUICreator(dataframe_filtered)
    new_layout = get_layout(ui_creator)

    return new_layout, dash.no_update


@app.callback(
    Output('body', 'children'),
    Input('settings_button', 'n_clicks'),
    prevent_initial_call=True,
)
def settings_button(click):
    """Возвращение к окну с фильтрами."""

    if click is None:
        raise PreventUpdate

    return get_main_layout()


@app.callback(
    Output('states_duration_diagram', 'figure'),
    State('states_filter', 'value'),
    Input('filter_button', 'n_clicks'),
    prevent_initial_call=True,
)
def filter_states_duration_diagram(values, click):
    """Фильтрация диаграммы длительностей состояний."""

    if click is None:
        raise PreventUpdate

    global states_duration_diagram

    if values:
        for i in states_duration_diagram.data:
            opacity = 0.2 if i['name'] not in values else 1
            states_duration_diagram.update_traces(opacity=opacity, selector={'name': i['name']})
    else:
        states_duration_diagram.update_traces(opacity=1)

    return states_duration_diagram


if __name__ == '__main__':
    data_collector = DataCollector()
    dataframe = data_collector.get_dataframe()

    app.layout = get_main_layout()
    app.run_server()
