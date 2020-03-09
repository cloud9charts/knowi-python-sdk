
# Python3 - Knowi API SDK (knowipy)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://www.opensource.org/licenses/MIT)

This repository houses the official Python SDK for use with Knowi. 

Knowi is an augmented analytics platform that instantly transforms any data into insights and data driven actions.


#### About

* The Knowi API SDK is the simplest way to automate your Knowi instance
* The SDK streamlines the API programming experience, allowing you to significantly reduce your written code
* This SDK was written for Python3, and is not compatible with Python2
* This library requires Python 3.6 and above.
* Execute scripts via `python3`

#### Features

* Dashboard Management
    * List, create, edit, clone, share, and delete dashboards
    * View widgets in a dashboard, export dashboards to PDF
    * Generate simple/secure dashboard share url
    * List, share, delete dashboard filter-sets
* Widget Management
    * List, create, edit, clone, share, and delete widgets
    * Generate simple/secure widget share url
* Datasource Management
    * List, clone, share, and delete datasources
* Query Management
    * List, clone, share, run, and delete queries
* Categories Management
    * List, copy, share, run, and delete categories
    * Add and remove assets to/from categories
* User Management
    * List, create, edit, and delete users
    * Transfer user assets to another user 
* Groups Management
    * List, create, edit, and delete groups 
* Natural Language Query Management
    * Get NLP query suggestions on a dataset
    * Execute NLP queries against a dataset
* Dataset Management
    * Retrieve data from a dataset or query
* Single Sign On (SSO)
    * Create and manage SSO users
    * Update SSO user attributes including user content filters  

#### Installation
We recommend using [PyPI](https://pypi.python.org/pypi) to install the Knowi SDK for Python
```bash
$ pip3 install knowipy --upgrade
```
> **Note:** You may need to use `python3` before your commands to ensure you use the correct Python path. e.g. `python3 --version`

```bash
python --version

-- or --

python3 --version
```




#### Usage
* See [examples.py](examples) for full usage and examples
* Retrieve your Client id/secret from your [Knowi](https://www.knowi.com) account
    - Navigate to Settings -> Account Settings https://recordit.co/HAudn0LJ2E 

```python
from knowipy import Knowi
import os

# instantiate the client
knowi = Knowi(clientId=os.environ['KNOWI_CLIENT_ID'], clientSecret=os.environ['KNOWI_CLIENT_SECRET'])


# get list of dashboards
dashboard_list = knowi.dashboard_list()

# to refresh an existing query
query_refresh = knowi.query_refresh(queryId=1231)


```


#### Development

----

Getting Started

Assuming that you have Python3 and ``virtualenv`` installed, set up your
environment and install the required dependencies like this instead of
the `pip3 install knowipy` defined above:

```shell script
 $ git clone https://github.com/ezeagwulae/knowi-python-sdk.git
    $ cd knowipy
    $ virtualenv venv
    ...
    $ . venv/bin/activate
    $ pip install -r requirements.txt
    $ pip install -e .
``` 

