# Models:
#### General aspects:
All models can have multiple acces tokens, allowing managment of read and write actions.

* ### Project:
    * Belongs to a user
    * Manages Zones
    * Has a name
    * Has a description
    * Has a snippet title and image in order to facilitate frontend development
* ### Zones:
    * Belongs to a Project
    * Manages:
        * Ambiental sensors
        * Nodes
    * Has a name
    * Has a description
* ### Nodes:
    * Belongs to a Zone
    * Manages node sensors
    * Has a name
    * Has a description
* ### Sensors:
    * Belongs to a Zone
    * *Might belong to a Node*
    * *Might be ambiental*
    * Has a type
        * This types can be modified inside the `model_choices.py` file
* ### Measurements:
    * Belong to a sensor
    * Has a type:
        * This types can be modified inside the `model_choices.py` file
    * Has a value
    * Has a `created_at` timestamp
        * It's set automatically when a new record is created
        * **If the time does not match your current timezone please change the `TIME_ZONE` parameter inside `backend.settings.py`**

### Models relationship:
![Model Relationship](https://mindmup-export.s3.amazonaws.com/map.png/out/ad5450808e8511ea8b9065e7a71d3811.map.png?AWSAccessKeyId=ASIASNCK5ADRYXXVF6KF&Expires=1588745137&Signature=i65i1ZYCoRxZ2FHpCJnFlxcXqTQ%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEEwaCXVzLWVhc3QtMSJHMEUCIQCmbSR3BxsfPC9Z8DQC9Ftd2JjhiXTkePP1YnYpGdhWEAIgWnhKRLj1DIKr0WNjOjNN66iVyR%2FAYgp6JetldIe7G28q2AEIhf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgwxNjU1MTMzMzA5MTUiDONYmvhxMjWO5E%2BRrCqsARa%2Fr1wKVsqIxUVe30BkYbWAWH16YCRDYvkjL0WXabrVLT9PRTUZebSuD4uzkhv2DSW4OXw0ZFidrqRAIVK9BSgSfhw5OoHKtz1ron4ZQ6VxVilLuzcTea6PDTlnGdUJDFrQT771POrBkAOKEvEf521Lsc%2Bp%2FAqEWy6kaK8MVKZMM5nwq%2Fb6KZ2ZIHxSXj%2BcR1uxEH8bKrk93N8AgWr7qWQT8vwUgJ%2FMds5p1eQw6MfD9QU64AF9HqgS7O5qtMfqTzDkWW1ftl0NgYFszGTBhdw7DlTwhAHOoKwgc0dDMUSM4DfWv7duvjWFyZT5Fx1z7GPequp%2FUNn7dY9gPshhtuu0OsmGxMdjyT1u3U6YziyhBAwErR5amm1RCVo%2F%2BwVNhd5HghsHiuc2m9RR0ELfbL4aWE%2FZuMz9dk5VnJWaoJIyb%2F0vYnC0wA5dhz8BKrBIAwGcadiTg3MrGscWjk7Q9oD73YEeZELmxuW6ZKMa3vRUiR4ueIpRiMsFRejhOh76ATxYAMLKgyT%2By%2BD%2B2SmRbufEhM9XDQ%3D%3D)
* A user can have **N** tokens which might belong to **N** Projects, Zones or Nodes.
* Each Project can have **N** Zones
* Each Zone can have **N** Nodes & **N** Ambiental Sensors
* Each Node can have **N** Sensors
* Each Sensor might have **N** Measurements with different types

# Plot views:
**IMPORTANT!** *As of current version there's no validation on who can see the plots*

### General aspects:
*All of the plot views return an image created from a `matplotlib.pyplot plot`, and all of the views require a project id*

### Views information
Inside the `views.py` file you will find 3 view classes, this classes accomplish different functions:
* `sensor_graph`:
    * Plots all measurements from a sensor
    * If some measurement types have different amount of measurements they'll be presented in different plots inside the same image

* `graph`:
    * Plots all measurments of a type from a sensor
    * Single type plot, thus no mismatching dimentions

* `graph_mixed`
    * Plots all measurments of a type from all sensors in a zone
    * If some sensor measurements have different amount of measurements they'll be presented in different plots inside the same image