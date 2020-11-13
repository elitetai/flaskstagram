# Flaskstagram
This flask project is created using the template provided by NEXT ACADEMY (refer below notes) and below features have been added:

1. User can signup, log in and out
1. **Google Authenticator** has been added for login purposes
1. User can update their credentials
1. User can make privatize their profile - for fan and idol features
1. A user can follow or being followed by another user, and one would need to approve or reject the request if the profile is under `private`
1. User can upload image (sent to **Amazon S3**) and being showed on their page once upload complete
1. Another user can `donate` (or make payment) via **Braintree** 
1. (Not testable, but it is working) User will receive an email via **Mailgun**

**Others features**: CSRF enabled, PostgreSQL Database

**Additional Info:** 

This flask project has API endpoint for another React project called [Reactstagramme](https://github.com/elitetai), which shares the same database (e.g. user info, image url path).

Deployed under **[Heroku]**()

---

### Notes:
> This repository template belongs to [NEXT Academy](https://github.com/NextAcademy/curriculum-nextagram-template) and is a part of NEXT Academy's coding bootcamps


## Dependencies Installation

- Python 3.7.2 was tested
- Postgresql 10.3 was tested

1. Delete `peewee-db-evolve==3.7.0` from `requirements.txt` during the first installation.
   Because of how `peewee-db-evolve` created it's build process, we would first need to delete it.
1. Run:
   ```
   pip install -r requirements.txt
   ```
1. Now add `peewee-db-evolve==3.7.0` back into `requirements.txt`
1. Run again:
   ```
   pip install -r requirements.txt
   ```

If you're having trouble installing dependencies

- Remove `certifi==2018.11.29` from requirements.txt

If you're having trouble starting flask

- Restart your terminal as well and reactivate conda source

**Create a `.env` file at the root of the directory**

This project uses `python-dotenv`. When running commands using `flask`, environment variables from `.env` are automatically loaded.

When executing `python` scripts directly e.g. `python start.py`, environment variables are not loaded and will not work except `python migrate.py` _(read the script - `migrate.py` to know why it would load the environment variables `.env`)_

Minimum environment variables that needs to be set

```
FLASK_APP='start' # based on the name of our entry point script
FLASK_ENV='development' # use this in development, otherwise 'production' or 'test'
DATABASE_URL="postgres://localhost:5432/nextagram_dev"
SECRET_KEY= #generate your own key
```

Use `os.urandom(32)` to generate a random secret key and paste that in `.env`. It's important to keep this `SECRET_KEY` private.

Since this app uses Pooled Connections, you may also want to set:

```
DB_TIMEOUT=300 # 5 minutes
DB_POOL=5
```

_(see `database.py`)_

**Create a Database**

- this application is configured to use Postgresql

```
createdb flaskstagram_dev
```

_\*if you name your database something else, tweak the settings in `.env`_

**Ignoring Files from Git**

Before git commiting, remember to ignore key files. Here's an example of `.gitignore`

```
.vscode
*.DS_Store
*__pycache__
*.env
```

---

## Database Migrations

```
python migrate.py
```

\*_this template is configured to use Peewee's PooledConnection, however, migrations using Peewee-DB-Evolve doesn't work well. A hack was used to not use PooledConnection when running migration. Pending investigation. There are no known side effects to run this template in production._

## Starting Server

```
flask run
```

## Starting Shell

```
flask shell
```

---

## Architecture

This template separates out API and Web to separate packages. Both API and Web are configured to use Flask's Blueprints.

All new models should go into it's own file/script within the models directory.

The entry point for a Flask server to start is located at `start.py`

---

## Dependencies

This template was created against `Python 3.7`. Should work with newer versions of Python. Not tested with older versions.

`Peewee` is used as ORM along with a database migration library `peewee-db-evolve`.

This template also comes packaged with Bootstrap 4.1.3 and it's dependencies (jQuery).

A copy of requirements.txt is included in the repository.

Remove `certifi==2018.11.29` if you're having trouble installing dependencies.
