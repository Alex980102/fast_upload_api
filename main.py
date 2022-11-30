import random
from fastapi import FastAPI, File, Form, UploadFile
import pandas as pd
import requests
import uuid
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from PIL import Image
from fastapi.openapi.utils import get_openapi
import os
import json

origins = ['*']
headers = {'User-Agent': 'Custom'}
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ports_enviados = [3001]
# TODO: crear variable para guardar numero no mandados en base de datos


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        with open(file.filename, 'wb') as f:
            f.write(contents)
        os.rename(file.filename, 'assets/data.csv')
        files = pd.read_csv('assets/data.csv')
        for i in files.values:
            ports_to_send = json.loads(requests.get(
                'http://localhost:3000/api/botprocess').content)
            try:
                ports_to_send_df = pd.DataFrame.from_records(ports_to_send)
                ports_to_send_df = ports_to_send_df[ports_to_send_df['status'] == 'ready']
            except Exception as e:
                print(e)
                print('Abriendo Exception de ports_to_send_df')
                bool_value = True
                while (bool_value):
                    await asyncio.sleep(15)
                    print('despues de 15 segundos')
                    ports_to_send = json.loads(requests.get(
                        'http://localhost:3000/api/botprocess').content)
                    if (len(ports_to_send) > 0):
                        ports_to_send_df = pd.DataFrame.from_records(ports_to_send)
                        ports_to_send_df = ports_to_send_df[ports_to_send_df['status'] == 'ready']
                        if(len(ports_to_send_df['port']) > 0):    
                            bool_value = False
                ports_to_send = json.loads(requests.get(
                    'http://localhost:3000/api/botprocess').content)
                ports_to_send_df = pd.DataFrame.from_records(ports_to_send)
                ports_to_send_df = ports_to_send_df[ports_to_send_df['status'] == 'ready']
            print(len(ports_to_send_df['port']))
            if (len(ports_to_send_df['port']) == 0):
                bool_value = True
                while (bool_value):
                    await asyncio.sleep(15)
                    print('despues de 15 segundos')
                    ports_to_send = json.loads(requests.get(
                        'http://localhost:3000/api/botprocess').content)
                    ports_to_send_df = pd.DataFrame.from_records(ports_to_send)
                    ports_to_send_df = ports_to_send_df[ports_to_send_df['status'] == 'ready']
                    if (len(ports_to_send_df['port']) > 0):
                        bool_value = False
                ports_to_send = json.loads(requests.get(
                    'http://localhost:3000/api/botprocess').content)
                ports_to_send_df = pd.DataFrame.from_records(ports_to_send)
                ports_to_send_df = ports_to_send_df[ports_to_send_df['status'] == 'ready']
            port = random.choice(ports_to_send_df['port'])
            if (len(ports_enviados) < 2):
                ports_enviados.append(port)
            else:
                if (port == ports_enviados[-1]):
                    port = random.choice(ports_to_send_df['port'])
            ports_enviados.append(port)
            params_random_response = requests.get(
                'http://localhost:3000/api/sendparams').content
            minValue = json.loads(params_random_response)[0]['minValue']
            maxValue = json.loads(params_random_response)[0]['maxValue']
            random_sync_sleep = random.randint(minValue, maxValue)
            text = f'Hola {i[0]}{i[1]},\ntexto para convencer y volver a pagar el monto de {i[3]} pesos en la siguiente liga:\n{i[4]}'
            post_json = {"message": text, "phoneNumber": i[2]}
            try:
                send_text = requests.post(
                    f'http://localhost:{port}/api/whatsapp/sendtxt', post_json)
                if (send_text.status_code != 201):
                    print(send_text)
                    print(
                        f'Problema Grave con el envio status code: {send_text.status_code}')
                else:
                    print(send_text)
            except Exception as e:
                print(e)
                print(
                    'problema no se pudo mandar se va amandar el mensaje de otro puerto')
                await asyncio.sleep(15)
                try:
                    ports_to_send = json.loads(requests.get(
                        'http://localhost:3000/api/botprocess').content)
                    ports_to_send_df = pd.DataFrame.from_records(
                        ports_to_send)
                    ports_to_send_df = ports_to_send_df[ports_to_send_df['status'] == 'ready']
                    port = random.choice(ports_to_send_df['port'])
                    send_text = requests.post(
                        f'http://localhost:{port}/api/whatsapp/sendtxt', post_json)
                except Exception as e:
                    print(e)
            print(
                f'Mensaje terminando esperando para el siguiente {random_sync_sleep} segundos')
            await asyncio.sleep(random_sync_sleep)
            print('Mensaje enviado')
    except Exception as e:
        print(e)

        return {"ok": False, "msg": "Error fatal checar logs"}


@app.get("/")
def main():
    return {"ok": True,  "msg": "El servidor esta corriendo correctamente"}
