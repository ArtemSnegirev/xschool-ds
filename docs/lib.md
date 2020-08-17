Module lib
==========
Workload scoring library

This library provides class WorkloadScoring to calculate workload scoring based on BigQuery.

Supported features:
- safely storing and reading GCP credentials at .env (Google Cloud Platform)
- splitting records by categorical features e.g. country, channels and so on
- managing historical period for calculations e.g. last 28 days
- workload scoring calculation based on confidence interval
- approaches to calculate scoring based on machine learning [in progress]

Notes
-----
    [!] Make sure you have **credentials** to work with GCP.
    [!] Library uses **google-auth** to work with credentials and **pandas-gbq**.
    [!] Library uses **dotenv** to safely store security-sensitive data.

Using
-------
    1) create account object by passing credentials to create WorkloadScoring instance
    2) read BigQuery table by **read_table** method passing the necessary columns to split records
    3) calculate assignee workload score by **workload_scoring** method passing the time intervals and columns for splitting
    4) write BigQuery table by **write_table** method passing the columns to save as your schema supposes

Example
-------
    [!] make sure you setup your own credentials in .env in the root of repo.

    See examples in **examples.py**

    $ python examples.py

Classes
-------

`WorkloadScoring(credentials)`
:   The summary line for a class docstring should fit on one line.
    
    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).
    
    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.
    
    Attributes
    ----------
    attr1 : str
        Description of `attr1`.
    attr2 : :obj:`int`, optional
        Description of `attr2`.
    
    Example of docstring on the __init__ method.
    
    The __init__ method may be documented in either the class level
    docstring, or as a docstring on the __init__ method itself.
    
    Either form is acceptable, but the two should not be mixed. Choose one
    convention to document the __init__ method and be consistent with it.
    
    Note
    ----
    Do not include the `self` parameter in the ``Parameters`` section.
    
    Parameters
    ----------
    param1 : str
        Description of `param1`.
    param2 : :obj:`list` of :obj:`str`
        Description of `param2`. Multiple
        lines are supported.
    param3 : :obj:`int`, optional
        Description of `param3`.

    ### Methods

    `read_table(self, dataset_id, table_id, columns=None)`
    :   Class methods are similar to regular functions.
        
        Note
        ----
        Do not include the `self` parameter in the ``Parameters`` section.
        
        Parameters
        ----------
        param1
            The first parameter.
        param2
            The second parameter.
        
        Returns
        -------
        bool
            True if successful, False otherwise.

    `workload_scoring(self, columns_list, num_of_all_days=28, num_of_interval_days=7, end_date='2017-04-01')`
    :   Class methods are similar to regular functions.
        
        Note
        ----
        Do not include the `self` parameter in the ``Parameters`` section.
        
        Parameters
        ----------
        param1
            The first parameter.
        param2
            The second parameter.
        
        Returns
        -------
        bool
            True if successful, False otherwise.

    `write_table(self, dataset_id, table_id, dev_name='default.developer', columns=None)`
    :   Class methods are similar to regular functions.
        
        Note
        ----
        Do not include the `self` parameter in the ``Parameters`` section.
        
        Parameters
        ----------
        param1
            The first parameter.
        param2
            The second parameter.
        
        Returns
        -------
        bool
            True if successful, False otherwise.