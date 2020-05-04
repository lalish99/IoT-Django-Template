# Django 3.0 template for AWS Bean Stalk
----

### Features
* Custom User Model
* Lean deployement on AWS Bean Stalk
* Static files and Database configured for local development and remote deployment

### Prerequisites
* Install [virtualenv](https://pypi.org/project/virtualenv/)
* Create a new virtual environment: `$ virtualenv MyVirtualEnv -p python3`
This will create a new virtualenv with the name *MyVirtualEnv* (feel free to change it), using python 3
* Start your new virtualenv: `$ . MyVirtualEnv/bin/activate`
* Install requirements on your environment: `$ pip install -r requirements.txt`

### How to use:
After completing the prerequisites section you can now start using the project, simply do the following:
* Migrate in order to setup the custom user model: `$ ./manage.py migrate`
* Test the installation by running the server: `$ ./manage.py runserver`
