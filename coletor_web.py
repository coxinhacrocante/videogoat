import requests
import io
from PIL import Image
from moviepy.audio import *
from moviepy.video import *
from moviepy.editor import *

def download_image(download_path, url, file_name):
    try:
        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        file_path = download_path + file_name + '.png'
        with open(file_path, "wb") as f:
            image.save(f, "png")
        print('sucesso no download da imagem: '+file_name)
    except Exception as e:
        print('CRITICAL FALIURE - ' + str(e))

def download_video(saida, url, titulo):
    chunk_size = 256
    entrada = requests.get(url, stream=True)
    with open(titulo + '.mp4', 'wb') as arquivo:
        for chunk in entrada.iter_content(chunk_size=chunk_size):
            arquivo.write(chunk)
        arquivo.close()

def download_musica(saida, url, titulo):
    CHUNK = 256
    entrada = requests.get(url, stream=True)
    with open(titulo + '.mp3', 'wb') as arquivo:
        for chunk in entrada.iter_content(chunk_size=CHUNK):
            arquivo.write(chunk)

def transformar_video_em_audio(arquivo, titulo=None):
    clip = VideoFileClip(arquivo)
    if titulo == None:
        clip.writeAudioFile(str(arquivo[:-4])+'.mp3')
    else:
        clip.writeAudioFile(str(titulo)+".mp3")