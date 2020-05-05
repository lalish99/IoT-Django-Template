# General aspects
By default, **in this project**, `django_extensions` is included in the `requirements.txt`, thus you can allways call
```
$ ./manage.py show_urls
```
To see the complete routing of the prject.

But it's important to note the api root is `IoT/api/` and that the api views live inside the `IoT/api/g/` url namespace

# Measuring
In order to register a `Measurement` to a `Sensor` you first need to create a `Acces Token` and add it to a `Zone`, all of which 
can be done inside the admin console (type `admin/` on your browser).

After you have your `Acces Token` configured you can send single or multiple `Measurements` using the 
url: `IoT/api/g/measure/`

*For more information on `Access Tokens` check the `users.api.README` file*

### HTTP Rquest configuration:
* You must add the **"CA-TOKEN"** Header using your `Acces Token`
* You must send the information in **JSON** format
* The `Measurements` must be contained within the `sensors` argument of the body
* Each `Measurement` must contain:
    * The sensor id in the `ìd_sensor` parameter
    * The value inside the `value` parameter 
        * **IT CAN BE DECIMAL BUT MUST NOT EXCEED 2 DECIMAL POINTS**
        * If you need to change this, modify the `IoT.models.py`file
    * A valid measurement type inside the `measurement_type` parameter

#### JSON example:
```
{
    "sensors":[
        {
            "id_sensor":#,
            "value":##.##,
            "measurement_type":""
        }
    ]
}
```
#### HTTPie Test
By default, **in this project**, httpie is installed, with this you can test the different aspects of the api using the terminal 
just type: 
```
$ http REQUEST_TYPE http://ip_address:PORT/url/namespace/ "HEADER: VALUE" PARAMETER:='JSON'
```

For example, you could send a test `Measurement` using:
```
$ http POST http://localhost:8000/IoT/api/g/measure/ "CA-TOKEN: <your-token>" sensors:='[{"value":14,"id_sensor":1,"measurement_type":"A_HUMIDITY"}]'
```