# IoT-Django-Template
IoT Django backend basic starter project template
----

# **IMPORTANT**!!
You must reset the `SECRET_KEY` inside the `settings.py` file else your project might have security issues.

To do so I suggest generating a random string or going to a [random key generator online](https://randomkeygen.com/) 
and mixing some of the randomly generated strings. Ideally your `SECRET_KEY` must be [50](https://stackoverflow.com/questions/42726719/how-can-i-properly-change-the-assigned-secret-key-in-a-django-web-application) 

For more information read the [documentation](https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-SECRET_KEY)

#### Additionally you could use:
[django-generate-secret-key](https://pypi.org/project/django-generate-secret-key/)

*It is already inside `requirements.txt`.*
**First you'll need to uncomment the line `'django_generate_secret_key',` inside `INSTALLED_APPS` in `settings.py`.**
Then you only need to use: 
```
$ ./manage.py generate_secret_key
```
This will write a randomly generated `SECRET_KEY` to a new file called `secretkey.txt`, for more options and information check their [github](https://github.com/MickaelBergem/django-generate-secret-key).

Just remember to create your virtualenv first, check the *Prerequisites* section
----
----

### Features
* Custom User Model
* Custom Acces Tokens for secure authentication and delegation of read/write tasks (see `users.api.README` for more information)
* Ready to use IoT basic data recolection and management from multiple data sources (see `IoT.api.README` for more information)
* Ready to use and customizable plot views (see `IoT.README` for more information)
* Lean deployement on AWS Bean Stalk
* Static files and Database configured for local development and remote deployment

### Prerequisites
* Install [virtualenv](https://pypi.org/project/virtualenv/)
* Create a new virtual environment: 
```
$ virtualenv MyVirtualEnv -p python3
```
This will create a new virtualenv with the name *MyVirtualEnv* (feel free to change it), using python 3
* Start your new virtualenv: 
```
$ . MyVirtualEnv/bin/activate
```
* Install requirements on your environment: 
```
$ pip install -r requirements.txt
```

### How To Use
After completing the prerequisites section you can now start using the project, simply do the following:
* Migrate in order to setup the custom user model, the authentication tokens, and the IoT models: 
```
$ ./manage.py migrate
```
* Create a super user by typing:
```
$ ./manage.py createsuperuser
```
and following the steps
* Test the installation by running the server: 
```
$ ./manage.py runserver
```

After that you can access the `Admin` console via `localhost:8000/admin/` and start configurating your projects and their sensors.

### **IMPORTANT!**
Don't forget to migrate your database everytime you pull updates:
```
$ git pull
$ ./manage.py migrate
```
With this you ensure the project works correctly
