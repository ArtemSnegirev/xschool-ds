"""
This library provides class WorkloadScoring to calculate workload scoring based on BigQuery.

Supported features:

- safely storing and reading GCP credentials at .env (Google Cloud Platform)
- grouping records by categorical features e.g. group by column1, column2 etc.
- managing historical period for calculations e.g. last 28 days
- workload scoring calculation based on confidence interval
- approaches to calculate scoring based on machine learning [in progress]

Notes
-----

[!] Make sure you have credentials to work with GCP.

[!] Library uses google-auth to work with credentials and pandas-gbq.

[!] Library uses dotenv to safely store security-sensitive data.

Using
-------
- create account object by passing credentials to create WorkloadScoring instance
- read BigQuery table by ``read_table`` method passing the necessary columns to split records
- calculate assignee workload score by ``workload_scoring`` method passing the time intervals and columns for grouping
- write BigQuery table by ``write_table`` method passing the columns to save as your schema supposes

Example
-------
[!] make sure you setup your own credentials in .env in the root of repo.

Setup requirements:

    $ pip install -r requirements.txt

Run examples from ``examples.py``

    $ python examples.py

"""

from google.oauth2.service_account import Credentials

import pandas_gbq

import numpy as np
import pandas as pd
import math as mt
import datetime as dt

import itertools as it


class WorkloadScoring:
    """Class to calculate workload scoring based on BigQuery.
    """

    def __init__(self, credentials):
        """

        Parameters
        ----------
        credentials: dict of str: str, required
            required fields: https://google-auth.readthedocs.io/en/latest/user-guide.html

        Attributes
        ----------
        raw_df : dataframe
            BigQuery table data representation as pandas.DataFrame
        out_df : dataframe
            result of score calculation for saving in BigQuery table
        project_id: dataframe
            GCP project_id where placed BigQuery dataset and tables

        """

        self.raw_df = None
        self.out_df = None

        self.project_id = credentials['project_id']

        self.credentials = Credentials.from_service_account_info(credentials)

    def workload_scoring(self, columns_list, num_of_all_days=28, num_of_interval_days=7, end_date='2017-04-01'):
        """Class methods are similar to regular functions.

        Parameters
        ----------
        columns_list: list of str, required
            columns for grouping records e.g. group by column1, column2 etc.
        num_of_all_days: int, optional, default=28
            period in days that used to calculate score
        num_of_interval_days: int, optional, default=7
            window that used to slide against period
        end_date: str, optional, default='2017-04-01'
            date of the last interval in schema 'y-m-d'

        """

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

        cartesian_product = list(it.product(*col_unique_vals))

        for values in cartesian_product:
            df_slice = self.__get_dataframe_slice(columns_list, values)

            end_date = dt.datetime.strptime(str(end_date), '%Y-%m-%d')
            end_date = end_date.date()

            fst_cur_date = end_date - dt.timedelta(days=num_of_all_days)

            delta = dt.timedelta(days=num_of_interval_days)

            snd_cur_date = fst_cur_date + delta

            num_of_intervals = int(num_of_all_days / num_of_interval_days)
            num_tasks_per_week = []

            for i in range(0, num_of_intervals):
                df_interval = df_slice[
                    (df_slice.updated >= str(fst_cur_date)) & (df_slice.updated <= str(snd_cur_date))]

                fst_cur_date = fst_cur_date + delta
                snd_cur_date = snd_cur_date + delta

                if i != (num_of_intervals - 1):
                    num_of_tasks = len(np.unique(df_interval['id']))
                    num_tasks_per_week.append(num_of_tasks)  # history number of tasks
                else:
                    num_tasks_per_current_week = len(np.unique(df_interval['id']))  # currently number of tasks

            avg_num_of_task_per_week = round(np.mean(num_tasks_per_week), 2)

            # TODO: rewrite score calculation logic as interface->class->object

            x_values = []
            for num in num_tasks_per_week:
                x = round((num - avg_num_of_task_per_week) ** 2, 2)
                x_values.append(x)

            x_sum = round(sum(x_values), 2)
            dispersion = round(x_sum / (num_of_intervals - 1), 2)
            std = round(mt.sqrt(dispersion), 2)
            ste = round(std / mt.sqrt(num_of_intervals), 2)

            left_border = int(avg_num_of_task_per_week - ste)
            right_border = int(avg_num_of_task_per_week + ste)

            score_value = self.__calc_workload_score(left_border, right_border, num_tasks_per_current_week)

            data['score_value'].append(score_value)
            data['count_last_period'].append(num_tasks_per_current_week)
            data['count_sem_calc_period'].append(ste)
            data['count_mean_calc_period'].append(avg_num_of_task_per_week)

            for i, column in enumerate(columns_list):
                data[column].append(values[i])

        self.out_df = pd.DataFrame(data=data)

    def read_table(self, dataset_id, table_id, columns=None):
        """Loading table data from BigQuery for workload scoring model

        Parameters
        ----------
        dataset_id: str, required
            BigQuery dataset_id of dataset that contains tables
        table_id: str, required
            BigQuery table_id which use to query data
        columns: list of str, optional, default=None
            columns for grouping records e.g. group by column1, column2 etc.

        """
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

    def write_table(self, dataset_id, table_id, dev_name='default.developer', columns=None):
        """Writing scoring data to BigQuery table

        Parameters
        ----------
        dataset_id: str, required
            BigQuery dataset_id of dataset that contains tables
        table_id: str, required
            BigQuery table_id which use to query data
        dev_name: str, optional, default='default.developer'
            name.surname of developer who perform calculations
        columns: list of str, optional, default=None
            columns to use in resulting table

        """

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
