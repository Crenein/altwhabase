import os
import time
import datetime
import subprocess
from dotenv import load_dotenv
from ispbaltwha import *

# Cargar variables de entorno desde .env
load_dotenv()

def send_messages(token, messages):

    for x in messages:
        try:
            message = x['message']
            phone = str(x["phone"])
            message_id = x['id']
            command = ['docker', 'run', '--rm', '-v', f'{os.getcwd()}/mudslide:/usr/src/app/cache', 'robvanderleek/mudslide', 'send', phone, message]
            commandout = subprocess.check_output(command, timeout=60, stderr=subprocess.PIPE)
            if 'success' in commandout.decode("utf-8"):
                success_send_message(token, message_id)
            else:
                error_send_message(token, message_id)
            t = delay_message(token)
            time.sleep(t)
        except subprocess.CalledProcessError as e:
            with open('log/error.txt', 'a', encoding='utf-8') as log:
                now = datetime.datetime.now()
                log.write(f"{now} Docker command failed: {e.returncode} - {e.stderr.decode('utf-8') if e.stderr else 'No stderr'}\n")
            error_send_message(token, message_id)
            return False
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
        try:
            #Obtener token
            token = get_ispb_token()

            if token:
                try:
                    if is_valid_time():
                        #print("La hora actual está dentro del rango válido.")

                        #Cantidad de mensajes por ronda
                        mxr = message_per_round(token['token_access'])
                        if mxr == False:
                            connection_error()
                            continue

                        #Traer los mensajes de la ronda
                        messages = get_messages(token['token_access'], mxr) + get_noprocess_messages(token['token_access'], mxr)
                        if messages == False:
                            connection_error()
                            continue

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
                            continue

                        urgent_messages = get_urgent_messages(token['token_access'], mxr) + get_urgent_noprocess_messages(token['token_access'], mxr)
                        if urgent_messages == False:
                            connection_error()
                            continue

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

                except Exception as e:
                    with open('log/error.txt', 'a', encoding='utf-8') as log:
                        now = datetime.datetime.now()
                        log.write(f"{now} Error en procesamiento principal: {repr(e)}\n")
                    print(f"Error en procesamiento principal: {e}")
                    time.sleep(60)

            else:
                print('El token esta vacio')
                time.sleep(60)
                
        except Exception as e:
            with open('log/error.txt', 'a', encoding='utf-8') as log:
                now = datetime.datetime.now()
                log.write(f"{now} Error crítico en bucle principal: {repr(e)}\n")
            print(f"Error crítico en bucle principal: {e}")
            time.sleep(60)
            
        time.sleep(60)