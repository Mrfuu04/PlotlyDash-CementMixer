from datetime import (
    timedelta,
)

import pandas as pd
import plotly.express as px
from pandas import (
    DataFrame,
)


class MainPageUICreator:
    """Используется для создания компонентов на главной странице.
    Данные в dataframe должны приходить уже в готовом виде."""

    def __init__(self, dataframe: DataFrame):
        self.dataframe = dataframe
        self.color_discrete_map = self.get_color_discrete_map()

    def get_color_discrete_map(self):
        """Возвращает карту цветов с типом {'state': 'color'}."""

        if self.dataframe is not None:
            color_discrete_map = {
                reason: color for reason, color in zip(self.dataframe['reason'], self.dataframe['color'])
            }

        return color_discrete_map

    def get_reasons_pie(self):
        """Возвращает в виде круговой диаграммы причины состояний."""

        hover_template = (
            'Причина - <b>%{label}</b><br>'
            'В часах - <b>%{value}</b><br>'
            '<extra></extra>'
        )

        reasons_pie = px.pie(
            self.dataframe,
            values='duration_hour',
            names='reason',
            height=450,
            color_discrete_map=self.color_discrete_map,
            color='reason',
        )

        reasons_pie.update_traces(hovertemplate=hover_template, hoverlabel_bgcolor='white')

        return reasons_pie

    def get_states_duration_diagram(self):
        """Возвращает диаграмму ганта длительностей состояний."""

        dataframe = self.dataframe

        # Форматируем данные для красивого отображения в hovertemplate
        dataframe['formatted_start'] = dataframe['state_begin'].dt.strftime('%H:%M:%S (%d.%m)')
        dataframe['formatted_dur_min'] = dataframe['duration_min'].round(2).astype(str) + ' мин.'
        dataframe['formatted_shift_day'] = pd.to_datetime(dataframe['shift_day']).dt.strftime('%d.%m.%y')

        hover_template = (
            'Состояние - <b>%{customdata[0]}</b><br>'
            'Причина - <b>%{customdata[1]}</b><br>'
            'Начало - <b>%{customdata[2]}</b><br>'
            'Длительность - <b>%{customdata[3]}</b><br>'
            '<br>'
            'Сменный день - <b>%{customdata[4]}</b><br>'
            'Смена - <b>%{customdata[5]}</b><br>'
            'Оператор - <b>%{customdata[6]}</b><br>'
            '<extra></extra>'
        )

        custom_data = [
            'state', 'reason', 'formatted_start',
            'formatted_dur_min', 'formatted_shift_day',
            'shift_name', 'operator',
        ]

        states_duration_diagram = px.timeline(
            dataframe, x_start="state_begin", x_end="state_end",
            y="endpoint_name", color='reason', color_discrete_map=self.color_discrete_map,
            custom_data=custom_data,
        )

        min_tickval = dataframe['state_begin'].min() - timedelta(hours=1)
        max_tickval = dataframe['state_end'].max() + timedelta(hours=1)

        states_duration_diagram.update_layout(
            title={
                'text': 'График состояний',
                'x': 0.5,
            },
            showlegend=False,
            xaxis=dict(
                tickmode='array',
                tickformat='%H',
                type='date',
                tickvals=pd.date_range(start=min_tickval, end=max_tickval, freq='H'),
                ticks='inside',
                side='top',
            ),
            yaxis=dict(title=''),
            overwrite=True,
        )

        states_duration_diagram.update_traces(hovertemplate=hover_template, hoverlabel_bgcolor='white')

        return states_duration_diagram

    def get_first_client_name(self):
        """Возвращает первое имя из датафрейма, если оно есть, иначе None."""

        client_names = self.dataframe.get('client_name')
        first_client_name = client_names[0] if client_names is not None else None

        return first_client_name

    def get_shift_day(self):
        """Возвращает минимальное значение сменного дня."""

        shift_days = self.dataframe.get('shift_day')
        shift_day = shift_days.min() if shift_days is not None else None

        return shift_day

    def get_endpoint_name(self):
        """Возвращает первое значение точки учета из датафрейма,
        если оно есть, иначе None."""

        endpoint_names = self.dataframe.get('endpoint_name')
        endpoint_name = endpoint_names[0] if endpoint_names is not None else None

        return endpoint_name

    def get_state_begin(self):
        """Возвращает минимальное значение начала периода."""

        state_begins = self.dataframe.get('state_begin')
        if state_begins is not None:
            state_begin = state_begins.min().strftime('%H:%M:%S (%d.%m)')
        else:
            state_begin = None

        return state_begin

    def get_state_end(self):
        """Возвращает максимальное значение начала периода."""

        state_ends = self.dataframe.get('state_end')
        if state_ends is not None:
            state_end = state_ends.max().strftime('%H:%M:%S (%d.%m)')
        else:
            state_end = None

        return state_end
