# Classification app

___

## Project Setup

### First Steps

You can begin by either downloading a zip file of the project through github, or using a git command to clone the project by:

```bash
git clone https://github.com/ArtemSnegirev/xsolla_school.git
```

### Virtual Environment Setup

It is preferred to create a virtual environment per project, rather then installing all dependencies of each of your projects system wide. Once you install [virtual env](https://virtualenv.pypa.io/en/stable/installation/), and move to your projects directory through your terminal, you can set up a virtual env with:

```bash
virtualenv venv -p python3.6
```

This will create a python3.6 based virtual environment (venv) for you within your projects directory.

Note: You need to have [Python 3.6](https://www.python.org/downloads/release/python-360/) installed on your local device.

### Dependency installations

To install the necessary packages:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

This will install the required packages within your venv.


---

## Project Structure

**It's forked from cool [repo](https://github.com/alisezer/flask-template/blob/master/stories.py) developed by alisezer**

### Main Modules

Every flask application has a top-level module for creating the app itself.

### Models

The models, which are ML models, are built with Sklearn. 


### API

The project creates a simple API which has one endpoint for message categorization


### Main APP (Web Page)

The project also creates a very simple SPA provides call API `message_categorizer` by UI form.

Like the API, the web page relies on a blueprint, which is initiated in the `__init__.py` module.

The HTML and Static files for CSS required for rendering and styling web pages can be found under the `templates` and `static` folder.

### Logging

Logging is handled through flask's logger.

---

## Running the Application

You can go ahead and run the application with a simple command:

```bash
# ./projects

python -m classification_app
```
