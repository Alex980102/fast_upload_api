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

async def changeImage(path: str):
    image = Image.open(path)
    image.putpixel((random.randint(1, image.size[0]), random.randint(1, image.size[1])), (0,0,0,255))
    image.save('/Users/alejandro/DevProjects/Projects/Zintech/Whats-App-Github/fast_upload_api/assets/img.png')
    return '/Users/alejandro/DevProjects/Projects/Zintech/Whats-App-Github/fast_upload_api/assets/img.png'

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
            img_path = await changeImage('/Users/alejandro/DevProjects/Projects/Zintech/Whats-App-Github/fast_upload_api/assets/unicef.png')
            # img_path = '/Users/alejandro/DevProjects/Projects/Zintech/Whats-App-Github/fast_upload_api/assets/video_unicef.mp4'
            text = f'Hola *{i[1]} {i[2]}*,\n\n¡Te extrañamos! Vuelve a ser parte de la familia UNICEF y salva más vidas💙.\n\nTu ayuda toca el corazón de miles de niñas y niños 👦🏽👧🏽 que hoy te necesitan.\n\nDona ${i[5]} al mes y mueve al mundo de nuevo🌎.\nApóyalos aquí: \n\n{i[9]}'
            post_json = {"message": text, "phoneNumber": i[3]}
            post_image = {"path": img_path, "phoneNumber": i[3], "caption": text}
            try:
                # send_text = requests.post(
                #     f'http://localhost:{port}/api/whatsapp/sendtxt', post_json)
           
                # send_link = requests.post(f'http://localhost:{port}/api/whatsapp/sendtxt', {"message": i[9], "phoneNumber": i[3]})
                send_image = requests.post(
                    f'http://localhost:{port}/api/whatsapp/sendmedia', post_image,)
                if (send_image.status_code != 201):
                    print(send_image)
                    print(
                        f'Problema Grave con el envio status code: {send_image.status_code}')
                else:
                    print(send_image)
            except Exception as e:
                print(e)
                print(
                    'problema no se pudo mandar se va amandar el mensaje de otro puerto')
                await asyncio.sleep(15)
                try:
                    ports_to_send_df = await send_message('http://localhost:3000/api/botprocess')
                    port = random.choice(ports_to_send_df['port'])
                    # send_text = requests.post(
                    #     f'http://localhost:{port}/api/whatsapp/sendtxt', post_json)
                    # send_link = requests.post(f'http://localhost:{port}/api/whatsapp/sendtxt', {"message": i[9], "phoneNumber": i[3]})
                    send_image = requests.post(
                    f'http://localhost:{port}/api/whatsapp/sendmedia', post_image)
                except Exception as e:
                    print(e)
            print(
                f'Mensaje terminando esperando para el siguiente {random_sync_sleep} segundos')
            await asyncio.sleep(random_sync_sleep)
            print('Mensaje enviado')
        except Exception as e:
            print(e)
            pass

# @app.post("/uploadunicef")
# async def uploadUnicef(file: UploadFile = File(...)):
#     contents = file.file.read()
#     with open(file.filename, 'wb') as f:
#         f.write(contents)
#     os.rename(file.filename, 'assets/data.csv')
#     files = pd.read_csv('assets/data.csv')
#     for i in files.values:
#         try:
#             ports_to_send_df = await send_message('http://localhost:3000/api/botprocess')
#             port = random.choice(ports_to_send_df['port'])
#             if (len(ports_enviados) < 2):
#                 ports_enviados.append(port)
#             else:
#                 if (port == ports_enviados[-1]):
#                     port = random.choice(ports_to_send_df['port'])
#             ports_enviados.append(port)
#             params_random_response = requests.get(
#                 'http://localhost:3000/api/sendparams').content
#             minValue = json.loads(params_random_response)[0]['minValue']
#             maxValue = json.loads(params_random_response)[0]['maxValue']
#             random_sync_sleep = random.randint(minValue, maxValue)
#             my_uuid = uuid.uuid4()
#             my_uuid = str(my_uuid)
#             text = f'Hola {i[1]} {i[2]},\n¡Te extrañamos! Vuelve a ser parte de la familia UNICEF y salva más vidas:corazón_azul:.\nTu ayuda toca el corazón de miles de niñas y niños :chico::tono-de-piel-4::niña::tono-de-piel-4: que hoy te necesitan.\nDona {i[5]} al mes y mueve al mundo de nuevo:tierra_asia:.\nApóyalos aquí: {i[9]}  \n\n{my_uuid[0:7]}'
#             post_json = {"message": text, "phoneNumber": i[1]}
#             try:
#                 send_text = requests.post(
#                     f'http://localhost:{port}/api/whatsapp/sendtxt', post_json)
#                 if (send_text.status_code != 201):
#                     print(send_text)
#                     print(
#                         f'Problema Grave con el envio status code: {send_text.status_code}')
#                 else:
#                     print(send_text)
#             except Exception as e:
#                 print(e)
#                 print(
#                     'problema no se pudo mandar se va amandar el mensaje de otro puerto')
#                 await asyncio.sleep(15)
#                 try:
#                     ports_to_send_df = await send_message('http://localhost:3000/api/botprocess')
#                     port = random.choice(ports_to_send_df['port'])
#                     send_text = requests.post(
#                         f'http://localhost:{port}/api/whatsapp/sendtxt', post_json)
#                 except Exception as e:
#                     print(e)
#             print(
#                 f'Mensaje terminando esperando para el siguiente {random_sync_sleep} segundos')
#             await asyncio.sleep(random_sync_sleep)
#             print('Mensaje enviado')
#         except Exception as e:
#             print(e)
#             pass

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
