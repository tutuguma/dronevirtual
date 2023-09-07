#Configurar puerto y host para conexion de counterfit
from counterfit_connection import CounterFitConnection
CounterFitConnection.init('127.0.0.1', 5000)

#Librerias para tiempo,configuración del sensor gps, decodificar gps,conectar el dispositivo
#a la nube
import time
import counterfit_shims_serial
import pynmea2
import json
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

#Configuracion del sensor, y de las conexiones del dispositivo a la nube
serial = counterfit_shims_serial.Serial('/dev/ttyAMA0')
connection_string = "AZURE CONNECTION_STRING"

#Conexion del dispositivo a la nube
device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)
print('Connecting')
device_client.connect()
print('Connected')

#Leer del puerto serie e imprimir los valores en la consola de forma decodificada
def print_gps_data(line):
 msg = pynmea2.parse(line)
 if msg.sentence_type == 'GGA':
    lat = pynmea2.dm_to_sd(msg.lat)
    lon = pynmea2.dm_to_sd(msg.lon)

    if msg.lat_dir == 'S':
        lat = lat * -1

    if msg.lon_dir == 'W':
        lon = lon * -1

    message_json = { "gps" : { "lat":lat, "lon":lon } }
    print("Sending telemetry", message_json)
    message = Message(json.dumps(message_json))
    device_client.send_message(message)  


while True:
    line = serial.readline().decode('utf-8')
    while len(line) > 0:
        print_gps_data(line)
        line = serial.readline().decode('utf-8')

    time.sleep(60)