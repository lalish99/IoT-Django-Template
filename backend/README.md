## Configuring for deployment:

Before deploying your application you must configure your database,
the way in which this project is via environmental variables, thus
you must modify the following variables in your environment for Django
to be able to locate your database:

* **"RDS_DB_NAME"** : Your database name
* **"RDS_USERNAME"** : Your database username
* **"RDS_PASSWORD"** : Your database password
* **"RDS_HOSTNAME"** : Your host name
* **"RDS_PORT"** : The port  of your database

----
## Important notes:
By default this project is configured to use **MySQL**. If you want to change
it you most modify the **"ENGINE"** variable inside the **DATABASES** section of
the `backend.settings.py` file
