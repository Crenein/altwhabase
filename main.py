import os
import time
import datetime
import subprocess
from ispbaltwha import *

def send_messages(token, messages):

    for x in messages:
        try:
            message = x['message']
            phone = str(x["phone"])
            message_id = x['id']
            command = "docker exec altwha mudslide send "+phone+" "+"'"+message+"'"
            commandout = subprocess.check_output(command, shell = True, timeout=60)
            if 'success' in commandout.decode("utf-8"):
                success_send_message(token, message_id)
            else:
                error_send_message(token, message_id)
            t = delay_message(token)
            time.sleep(t)
        except Exception as e:
            with open('log/error.txt', 'a', encoding='utf-8') as log:
                now = datetime.datetime.now()
                log.write(str(now) + " send_message " + repr(e) + '\n')
            error_send_message(token, message_id)
            return False

def connection_error():
    print('Error de conexión a API ISPbrain')
    time.sleep(300)

if __name__ == "__main__":
    
    while True:
        #Obtener token
        token = get_ispb_token()

        if token:
            if is_valid_time():
                #print("La hora actual está dentro del rango válido.")

                #Cantidad de mensajes por ronda
                mxr = message_per_round(token['token_access'])
                if mxr == False:
                    connection_error()

                #Traer los mensajes de la ronda
                messages = get_messages(token['token_access'], mxr) + get_noprocess_messages(token['token_access'], mxr)
                if messages == False:
                    connection_error()

                #Enviar mensajes
                if len(messages) > 0:
                    output = send_messages(token['token_access'], messages)

                    #Pausa
                    pause_time = pause_send(token['token_access'])
                    if pause_time:
                        #print('Pausa de: '+str(pause_time)+' segundos')
                        time.sleep(pause_time)
                    else:
                        connection_error()

            else:
                #print("La hora actual está fuera del rango válido pero se enviarán mensajes urgentes")

                #Cantidad de mensajes por ronda
                mxr = message_per_round(token['token_access'])
                if mxr == False:
                    connection_error()

                urgent_messages = get_urgent_messages(token['token_access'], mxr) + get_urgent_noprocess_messages(token['token_access'], mxr)
                if urgent_messages == False:
                    connection_error()

                if len(urgent_messages) > 0:
                    #Enviar mensajes
                    output = send_messages(token['token_access'], urgent_messages)
                    #Pausa
                    pause_time = pause_send(token['token_access'])
                    if pause_time:
                        #print('Pausa de: '+str(pause_time)+' segundos')
                        time.sleep(pause_time)
                    else:
                        connection_error()

        else:
            print('El token esta vacio')
        time.sleep(60)