from settings import CREDENTIALS
from lib import WorkloadScoring

if __name__ == '__main__':
    ws = WorkloadScoring(CREDENTIALS)

    # dataset and table from which we read
    dataset_id = 'xsolla_summer_school'
    read_table_id = 'customer_support'

    # the name for filtering records
    # in the result tables
    developer_name = 'artem.snegirev'

    # table for saving results of example 1
    write_table_id = 'score_result_status'

    # config of columns for slice
    # and available values of column
    table_columns = {
        'assignee_id': [],  # all values are allowed
        'status': ['closed', 'solved']
    }

    # load dataframe with specify dataset and table
    ws.load_data(dataset_id, read_table_id, table_columns)

    # calculate workload score in terms of columns and period
    ws.workload_scoring(
        columns_list=list(table_columns.keys()),
        num_of_interval_days=7,
        num_of_all_days=63,
        end_date='2017-04-01'
    )

    # save result to bigquery
    ws.insert_data(dataset_id, write_table_id, developer_name)

    # -----------------------------------#

    # table for saving results of example 2
    write_table_id = 'score_result_total'

    table_columns = {
        'assignee_id': [],
    }

    ws.workload_scoring(
        columns_list=list(table_columns.keys()),
        num_of_interval_days=7,
        num_of_all_days=63,
        end_date='2017-04-01'
    )

    ws.insert_data(
        dataset_id,
        write_table_id,
        developer_name,

        # only this columns'll written to bigquery
        columns=['assignee_id', 'score_value']
    )

    # -----------------------------------#

    # table for saving results of example 3
    write_table_id = 'score_result_status_channel'

    table_columns = {
        'channel': [],
        'assignee_id': [],
        'status': ['closed', 'solved'],
    }

    ws.load_data(dataset_id, read_table_id, table_columns)

    ws.workload_scoring(
        columns_list=list(table_columns.keys()),
        num_of_interval_days=7,
        num_of_all_days=35,
        end_date='2017-04-01'
    )

    ws.insert_data(dataset_id, write_table_id, developer_name)
