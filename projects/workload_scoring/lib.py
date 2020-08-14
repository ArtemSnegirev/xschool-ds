from google.oauth2.service_account import Credentials

import pandas_gbq

import numpy as np
import pandas as pd
import math as mt
import datetime as dt

import itertools as it


class WorkloadScoring:
    """

    """

    def __init__(self, credentials):

        self.raw_df = None
        self.out_df = None

        self.project_id = credentials['project_id']

        self.credentials = Credentials.from_service_account_info(credentials)

    def workload_scoring(self, columns_list, num_of_all_days=28, num_of_interval_days=7, end_date='2017-04-01'):
        if self.raw_df is None:
            return 'load data'

        data = {
            'score_value': [],
            'count_last_period': [],
            'count_sem_calc_period': [],
            'count_mean_calc_period': []
        }

        col_unique_vals = []
        for column in columns_list:
            data[column] = []

            col_unique_vals.append(self.raw_df[column].unique())

        #
        cartesian_product = list(it.product(*col_unique_vals))

        for values in cartesian_product:
            # берем срез записей в зависимости от набора значений по категориям
            df_slice = self.__get_dataframe_slice(columns_list, values)

            # берем конечную дату
            end_date = dt.datetime.strptime(str(end_date), '%Y-%m-%d')
            end_date = end_date.date()

            # берем первую дату
            fst_cur_date = end_date - dt.timedelta(days=num_of_all_days)

            # берем интервал/смещение
            delta = dt.timedelta(days=num_of_interval_days)

            # находим конец первого периода
            snd_cur_date = fst_cur_date + delta

            num_of_intervals = int(num_of_all_days / num_of_interval_days)
            num_tasks_per_week = []

            for i in range(0, num_of_intervals):
                # берем записи i интервала
                df_interval = df_slice[
                    (df_slice.updated >= str(fst_cur_date)) & (df_slice.updated <= str(snd_cur_date))]

                # делаем смещения
                fst_cur_date = fst_cur_date + delta
                snd_cur_date = snd_cur_date + delta

                if i != (num_of_intervals - 1):
                    num_of_tasks = len(np.unique(df_interval['id']))
                    num_tasks_per_week.append(num_of_tasks)  # history number of tasks
                else:
                    num_tasks_per_current_week = len(np.unique(df_interval['id']))  # currently number of tasks

            avg_num_of_task_per_week = round(np.mean(num_tasks_per_week), 2)

            # squared deviations
            x_values = []
            for num in num_tasks_per_week:
                x = round((num - avg_num_of_task_per_week) ** 2, 2)
                x_values.append(x)

            # data sampling statistics
            x_sum = round(sum(x_values), 2)  # sum of squared deviations
            dispersion = round(x_sum / (num_of_intervals - 1), 2)  # dispersion
            std = round(mt.sqrt(dispersion), 2)  # standart deviation for sample
            ste = round(std / mt.sqrt(num_of_intervals), 2)  # standart error for sample

            # confidence interval
            left_border = int(avg_num_of_task_per_week - ste)
            right_border = int(avg_num_of_task_per_week + ste)

            # workload scoring for status
            score_value = self.__calc_workload_score(left_border, right_border, num_tasks_per_current_week)

            data['score_value'].append(score_value)
            data['count_last_period'].append(num_tasks_per_current_week)
            data['count_sem_calc_period'].append(ste)
            data['count_mean_calc_period'].append(avg_num_of_task_per_week)

            for i, column in enumerate(columns_list):
                data[column].append(values[i])

        self.out_df = pd.DataFrame(data=data)

    def load_data(self, dataset_id, table_id, columns=None):
        where_statement = []
        from_statement = f"from `{dataset_id}.{table_id}`"
        select_statement = "select id, date(cast(created_at as datetime)) as created, " \
                           "date(cast(updated_at as datetime)) as updated"

        if columns is not None:
            select_statement = select_statement + ", " + ", ".join(columns.keys())

            for c, v in columns.items():
                if len(v) > 0:
                    val_enum = ", ".join([f"'{x}'" for x in v])
                    where_statement.append(f'{c} in ({val_enum})')

        where_statement = "where " + ", ".join(where_statement) if len(where_statement) > 0 else ""

        bigquery_sql = " ".join([
            select_statement,
            from_statement,
            where_statement,
            "ORDER BY updated"
        ])

        self.raw_df = pandas_gbq.read_gbq(
            bigquery_sql,
            project_id=self.project_id
        )

    def insert_data(self, dataset_id, table_id, dev_name='default.developer', columns=None):
        if self.out_df is None:
            return 'calc workload scoring'

        destination_table = f"{dataset_id}.{table_id}"

        insert_df = pd.DataFrame()

        if columns is None:
            columns = self.out_df.columns

        column2type = dict(pandas_gbq.read_gbq(
            f"select {', '.join(columns)} from `{destination_table}` limit 0",
            project_id=self.project_id
        ).dtypes)

        for col in columns:
            insert_df[col] = self.out_df[col].astype(column2type[col])

        insert_df['developer'] = dev_name
        insert_df['developer'] = insert_df['developer'].astype('str')

        pandas_gbq.to_gbq(
            insert_df,
            project_id=self.project_id,
            destination_table=destination_table,
            if_exists='append'
        )

    def __get_dataframe_slice(self, columns, values):
        mask = True

        for i, col in enumerate(columns):
            mask = mask & (self.raw_df[col] == values[i])

        return self.raw_df[mask]

    @staticmethod
    def __calc_workload_score(left_board, right_board, current_num_of_tasks):
        if (left_board == 0) & (current_num_of_tasks == 0) & (right_board == 0):
            score = 0
        elif (current_num_of_tasks >= 0) & (current_num_of_tasks < left_board):
            score = 0
        elif (current_num_of_tasks >= left_board) & (current_num_of_tasks <= right_board):
            score = 1
        else:
            score = 2

        return score
