A simple Django-based quiz application where users can register and login to attempt questions based on their choice of subjects.


## Running the Project Locally

1. Clone/Download the repository.

2. Open the folder:
```bash
cd testYourKnowledge
```


3. Create and activate the virtual environment and install the dependencies:

```bash
pip install pipenv
pipenv shell
pipenv install
```

4. Create the database:

```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

5. Create superuser to access the admin panel (You can also use the credentials given below):

```bash
python manage.py createsuperuser
```

6. Run the server:

```bash
python manage.py runserver
```

## Credentials to access the admin panel
```bash
username - kaushal
password - kaushal
```
