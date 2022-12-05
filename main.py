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

# Crear funcion para mandar el mensaje

async def send_message_main(i, url_send):
    try:
        ports_to_send_df = await send_message('http://localhost:3000/api/botprocess')
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
        my_uuid = uuid.uuid4()
        my_uuid = str(my_uuid)
        try:
            send_text = requests.get(
                f'http://localhost:{port}{url_send}/{i[1]}/{i[0]}')
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
            # await asyncio.sleep(15)
            try:
                ports_to_send_df = await send_message('http://localhost:3000/api/botprocess')
                port = random.choice(ports_to_send_df['port'])
                send_text = requests.get(
                    f'http://localhost:{port}{url_send}/{i[1]}/{i[0]}')
            except Exception as e:
                print(e)
        print(
            f'Mensaje terminando esperando para el siguiente {random_sync_sleep} segundos')
        # await asyncio.sleep(random_sync_sleep)
        print('Mensaje enviado')
    except Exception as e:
        print(e)
        pass


async def send_message(url):
    bool_value = True
    while (bool_value):
        try:
            ports_to_send = json.loads(requests.get(url).content)
            if len(ports_to_send) == 0:
                # volver a intenar
                print('No hay puertos para enviar esperando 10 segundos')
                await asyncio.sleep(10)
            else:
                try:
                    ports_to_send = json.loads(requests.get(url).content)
                    print(ports_to_send)
                    ports_to_send_df = pd.DataFrame.from_records(ports_to_send)
                    print(ports_to_send_df)
                    ports_to_send_df = ports_to_send_df[ports_to_send_df['status'] == 'ready']
                    if len(ports_to_send_df) > 0:
                        return ports_to_send_df
                    await asyncio.sleep(10)
                    print('Ports to send: ', ports_to_send_df)
                except Exception as e:
                    print(
                        'Error al convertir a dataframe los puertos no estan en ready')
                    print(e)
                    await asyncio.sleep(10)

        except Exception as e:
            print('Error al obtener los puertos esperando 10 segundos')
            await asyncio.sleep(10)
            print(e)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = file.file.read()
    with open(file.filename, 'wb') as f:
        f.write(contents)
    os.rename(file.filename, 'assets/data.csv')
    files = pd.read_csv('assets/data.csv')
    for i in files.values:
        try:
            ports_to_send_df = await send_message('http://localhost:3000/api/botprocess')
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
            my_uuid = uuid.uuid4()
            my_uuid = str(my_uuid)
            text = f'Hola {i[0]}, La Receta para un atraco al pueblo desde el Congreso de Morelos\nPrimer paso:\nRabindranath Salazar, aspirante a gobernador eterno, junto con su operador Miguel Lucia Espejo, le venden el apoyo y el apoyo de los tres diputados que “tienen” en el congreso a la oposición, Agustín Alonso y Francisco Sánchez.\n\nSegundo paso:\nTania Valentina se suma a la negociación y el nuevo grupo RSS24 obtiene un moche de $20 millones, $5 millones por diputado. \n\nTercer paso:\nPara recuperar el dinero de los expresidentes municipales y para poder financiar la lega campaña de rabindranath, el grupo RSS24 acuerda repartirse el paquete presupuestal a modo y repartirse las ganancias entre ellos.\n\nCuarto paso:\nPara destantear al enemigo y a los presidentes municipales aumentan del uno al dos por ciento los ingresos de los municipios, cuando anteriormente habían  propuesto 1%. De paso crean nuevas cláusulas y un “Fondo Municipal para obra pública” por $492 millones adicionales.\n\nQuinto paso:\nDe los $492 millones del nuevo fondo, $450 millones los etiquetan y asignan para solo 3 municipios del PAN y de Agustín Alonso y de Francisco Perez, con la condición de que dicho presupuesto se ejercido directamente por los municipios en cuestión, a cambio, le prometen a cada diputado entre $5Millones y $10Millones dependiendo de que tan trucha se puso el diputado local en turno.\n\nSexto y último paso:\nSi toda la tranza les sale, con el recurso de obra etiquetado, Agustín Alonso, Francisco Perez y el RSS24 planean embolsarse el 35% de ese dinero utilizando y asignando los contratos a empresas que son propiedad propia o de amigos y familiares muy cercanos a los distintos diputados como son las constructoras de los diputados Paola Cruz, Eliasib Polanco, Agustín Alonso, Francisco Perez, Alberto Sánchez, entre otros. Total esos municipios los controlan ellos y la maña.\n\n{my_uuid[0:7]}'
            post_json = {"message": text, "phoneNumber": i[1]}
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
                    ports_to_send_df = await send_message('http://localhost:3000/api/botprocess')
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
            pass

@app.post("/ckeckuser")
async def upload(file: UploadFile = File(...)):
    contents = file.file.read()
    with open(file.filename, 'wb') as f:
        f.write(contents)
    os.rename(file.filename, 'assets/data.csv')
    files = pd.read_csv('assets/data.csv')
    for i in files.values:
        await send_message_main(i, '/api/whatsapp/checkuser')

@app.get("/")
def main():
    return {"ok": True,  "msg": "El servidor esta corriendo correctamente"}
