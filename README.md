# boac

bCourses offers analytic choices.

## Installation

### Install Python 3

### Create your virtual environment

### Install Yarn

`brew install yarn`

### Install back-end

`pip install -r requirements.txt`

### Install front-end dependencies

`yarn install`

### Create Postgres user and databases

```
createuser boac --no-createdb --no-superuser --no-createrole --pwprompt
createdb boac --owner=boac
createdb boac_test --owner=boac
# TODO psql boac < scripts/db/schema.sql
```

### Create local configurations

If you plan to use any resources outside localhost, put your configurations in a separately encrypted area:

```
mkdir /Volumes/XYZ/boac_config
export BOAC_LOCAL_CONFIGS=/Volumes/XYZ/boac_config
```

## Usage
