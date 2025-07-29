import time
import datetime
import requests
import random
from requests_cache import CachedSession
import os

#Validar dia y hora
def is_valid_time():
    now = datetime.datetime.now()
    if now.weekday() < 6 and 8 <= now.hour < 19:
        return True
    return False

#Base url generate
def get_base_url():
    subdomain = os.environ['ISPBRAIN_SUBDOMAIN']
    base_url = base_url = "https://"+subdomain+".ispbrain.io:4443/api/v2"
    
    return base_url

#Account ID
def get_account_id():
    account_id = os.environ['ISPBRAIN_ACCOUNT']
    
    return account_id

#Validate response
def validation_response(response):
    #Validacion de response
    if response.status_code == 401:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + ' 401 Unauthenticated' + "\n")
            return False

    if response.status_code >= 500:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + ' 500 Cloud server error' + "\n")
            return False

    if response.status_code >= 402:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + ' 400 Client error' + "\n")
            return False

    if response.status_code == 200:
        return response

#Obtener token de ISPbrain
def get_ispb_token():
    username = os.environ['ISPBRAIN_USER']
    password = os.environ['ISPBRAIN_PASSWORD']
    login = {"username": username, "password": password}
    base_url = get_base_url()
    try:
        response = requests.post(base_url+"/auth", json = login)
        response = validation_response(response)
        token = response.json()
        return token

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " get_ispb_token " + repr(e) + '\n')
        return False

#Obtener configuración de la cuenta
def get_account_config(token):

    base_url = get_base_url()
    account_id = get_account_id()
    headers = {"Authorization": token}

    try:
        session = CachedSession('ispb_cache', backend='sqlite', expire_after=600)
        response = session.get(base_url+'/altwha_accounts/'+account_id, headers = headers)
        response = validation_response(response)
        data = response.json()['config']
        return data

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " get_account_config " + repr(e) + '\n')
        return False

#Generar cantidad de mensajes por ronda
def message_per_round(token):

    config = get_account_config(token)
    block = config['block']
    mxr = random.randint(block[0], block[1])

    return mxr

#Tiempo de descanso entre rondas
def pause_send(token):

    config = get_account_config(token)
    pause = config['pause']
    pause_time = random.randint(pause[0], pause[1])

    return pause_time

#Generar tiempo de espera entre mensajes
def delay_message(token):

    config = get_account_config(token)
    delay = config['delay']
    tem = random.randint(delay[0], delay[1])

    return tem

#Obtener mensajes urgentes de la cuenta
def get_urgent_messages(token, limit):

    base_url = get_base_url()
    account_id = get_account_id()
    headers = {"Authorization": token}

    try:
        params={
            "page[size]": limit,
            "page[number]": 1,
            "filter[account_id]": account_id,
            "filter[cancelled]": 0,
            "filter[deleted]": 0,
            "filter[status]": 0,
            "filter[urgent]": 1
        }
        response = requests.get(base_url+'/altwha_messages', params = params, headers = headers)
        response = validation_response(response)
        data = response.json()['data']

        return data

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " get_urgent_messages " + repr(e) + '\n')
        return False

#Obtener mensajes urgentes de la cuenta
def get_urgent_noprocess_messages(token, limit):

    base_url = get_base_url()
    account_id = get_account_id()
    headers = {"Authorization": token}

    try:
        params={
            "page[size]": limit,
            "page[number]": 1,
            "filter[account_id]": account_id,
            "filter[cancelled]": 0,
            "filter[deleted]": 0,
            "filter[status]": 2,
            "filter[urgent]": 1
        }
        response = requests.get(base_url+'/altwha_messages', params = params, headers = headers)
        response = validation_response(response)
        data = response.json()['data']

        return data

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " get_urgent_messages " + repr(e) + '\n')
        return False

#Obtener mensajes de la cuenta
def get_messages(token, limit):

    base_url = get_base_url()
    account_id = get_account_id()
    headers = {"Authorization": token}

    try:
        urgent_messages = get_urgent_messages(token, limit)
        
        if len(urgent_messages) >= limit:
            messages = urgent_messages
        else:
            limit = limit-len(urgent_messages)

            params={
                "page[size]": limit,
                "page[number]": 1,
                "filter[account_id]": account_id,
                "filter[cancelled]": 0,
                "filter[deleted]": 0,
                "filter[status]": 0,
                "filter[urgent]": 0
            }
            response = requests.get(base_url+'/altwha_messages', params = params, headers = headers)
            response = validation_response(response)
            messages = urgent_messages + response.json()['data']

        return messages

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " get_messages " + repr(e) + '\n')
        return False


#Obtener mensajes de la cuenta
def get_noprocess_messages(token, limit):

    base_url = get_base_url()
    account_id = get_account_id()
    headers = {"Authorization": token}

    try:
        params={
            "page[size]": limit,
            "page[number]": 1,
            "filter[account_id]": account_id,
            "filter[cancelled]": 0,
            "filter[deleted]": 0,
            "filter[status]": 2,
            "filter[urgent]": 0
        }
        response = requests.get(base_url+'/altwha_messages', params = params, headers = headers)
        response = validation_response(response)
        messages = response.json()['data']

        return messages

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " get_messages " + repr(e) + '\n')
        return False

#Success send message
def success_send_message(token, message_id):
    base_url = get_base_url()
    account_id = get_account_id()
    headers = {"Authorization": token}

    now = datetime.datetime.now()
    time = now.strftime("%H:%M:%S")
    date = now.strftime("%Y-%m-%d")
    send_at = date+' '+time

    try:
        response = requests.patch(base_url+'/altwha_messages/'+str(message_id), json = {"send_at": send_at, "status": 1}, headers = headers)
        response = validation_response(response)
        return True

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " success_send_message " + repr(e) + '\n')
        return False

#Error send message
def error_send_message(token, message_id):
    base_url = get_base_url()
    account_id = get_account_id()
    headers = {"Authorization": token}

    now = datetime.datetime.now()
    time = now.strftime("%H:%M:%S")
    date = now.strftime("%Y-%m-%d")
    send_at = date+' '+time

    try:
        response = requests.patch(base_url+'/altwha_messages/'+str(message_id), json = {"send_at": send_at, "status": 2}, headers = headers)
        response = validation_response(response)
        return True

    except Exception as e:
        with open('log/error.txt', 'a', encoding='utf-8') as log:
            now = datetime.datetime.now()
            log.write(str(now) + " error_send_message " + repr(e) + '\n')
        return False