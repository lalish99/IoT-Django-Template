
DHT11 = 'DHT11'
DHT22 = 'DHT22'
MCP9701A = 'MCP9701A'
LDR = 'LDR'
BME280 = 'BME280'
BMP180 = 'BMP180'
SM150 = 'SM150'
CMS = 'CMS'
SENSOR_TYPE_CHOICES = [
    (DHT11,'Multisensor DHT11'),
    (DHT22,'Multisensor DHT22'),
    (MCP9701A,'Temperature sensor MCP9701A'),
    (LDR,'Photoresistor'),
    (BME280,'Pressure temperature humidity sensor BME280'),
    (BMP180,'Pressure temperature altitude sensor BMP180'),
    (SM150,'Moisture sensor'),
    (CMS,'Cable moisture sensor'),
]

A_TEMPERATURE = 'A_TEMPERATURE'
R_HUMIDITY = 'R_HUMIDITY'
B_HUMIDITY = 'A_HUMIDITY'
B_PRESSURE = 'B_PRESSURE'
B_ALTITUDE = 'B_ALTITUDE'
S_MOISTURE = 'S_MOISTURE'
LDR_LIGHT = 'LDR_LIGHT'

MEASUREMENT_TYPE_CHOICES = [
        (A_TEMPERATURE, 'Ambiental Temperature'),
        (R_HUMIDITY, 'Relative Humidity'),
        (B_PRESSURE, 'Barometric Presurre'),
        (B_ALTITUDE, 'Barometric Altitude'),
        (B_HUMIDITY, 'Barometric Humidity'),
        (S_MOISTURE, 'Soil Moisture'),
        (LDR_LIGHT, 'LDR Light Index'),
]