from ast import Pass
from moviepy.editor import *
from moviepy.audio import *
from moviepy.video import *
from moviepy.tools import *
import os
import math
import cv2
import coletor_web
import time
from tqdm import tqdm


def crops(clipes_lista, enquadramento):
    print('enquadramento recebido: {}'.format(enquadramento))
    if enquadramento == '': 
        print('Enquadramento Nulo')
        return clipes_lista

    #encontrado a intersessão
    for c in range(len(clipes_lista)):
        clip = clipes_lista[c]
        if c == 0:
            w_min, h_min = clip.size
        elif c >= 1:
            w, h = clip.size
            if w_min > w:
                w_min = w
            if h_min > h:
                h_min = h

    #calculando as medidas do corte
    if enquadramento == '📱 9:16':
        print('Enquadramento vertical')
        lado = (h_min * 9)//16
        altura = h_min
    elif enquadramento == '📟 16:9':
        print('Enquadramento horizontal')
        altura = (w_min * 16)//9
        lado = w_min
    elif enquadramento == '🔲 1:1':
        print('Enquadramento quadrado')
        if h_min == w_min:
            altura = h_min 
            lado = w_min
        elif h_min > w_min:
            altura = w_min
            lado = w_min
        elif h_min < w_min:
            altura = h_min
            lado = h_min
    else:
        print('ERRO: ENQUADRAMENTO ERRADO, veio assim: {}'.format(enquadramento))
        return clipes_lista

    #cortando caso seja necessário
    for c in range(len(clipes_lista)):
        clip = clipes_lista[c]
        w, h = clip.size
        x1 = w//2-lado//2
        y1 = h//2-altura//2
        x2 = w//2+lado//2
        y2 = h//2+altura//2
        clipes_lista[c] = clip.crop(x1=x1 , y1=y1 , x2=x2 , y2=y2)
    
    return clipes_lista, (int(x2-x1), int(y2-y1))











def coluna(lista, alvo):
    try:
        numero_coluna = lista.index(alvo)
        return numero_coluna
    except:
        numero_coluna = lista[0].index(alvo)
        return numero_coluna

def linha_em_coluna(lista, alvo_coluna, alvo_linha):
    numero_coluna = lista[0].index(alvo_coluna)
    for a in range(1, len(lista)):
        if lista[a][numero_coluna] == alvo_linha:
            return a



def tamanho_texto(texto, tamanho_fonte):
    linhas = texto.split('\n')
    comprimento_max = 0
    for c in range(0, len(linhas)):
        comprimento = len(linhas[c])
        if comprimento > comprimento_max:
            comprimento_max = comprimento
    texto_tamanho_x = int(comprimento_max * ((tamanho_fonte + tamanho_fonte/5)/2))
    texto_tamanho_y = int(len(linhas) * (tamanho_fonte + tamanho_fonte/4))
    formato_texto = (texto_tamanho_x, texto_tamanho_y)
    return formato_texto







def executar_template(template_escolhido, info_templates, comodos, intro, transitar, videoss, info_video, vinheta, array_nomes, usuarios):
    problemas = list()
    for c in range(len(template_escolhido)):
        try:
            if template_escolhido[c].replace(',','.').replace(':','.').isdecimal() == True:
                template_escolhido[c] = template_escolhido[c].replace(',','.').replace(':','.')
                template_escolhido[c] = float(template_escolhido[c])
        except:
            Pass

    #LINDANDO COM AS VELOCIDADES
    velocidade = eval(template_escolhido[coluna(info_templates, "Velocidades")])
    if len(velocidade) == 1:
        repetir = velocidade[0]
        velocidade = list()
        for c in range(comodos):
            velocidade.append(repetir)

    #CARREGANDO CLIPES E ÁUDIO
    msc = AudioFileClip('msc.mp3')
    if intro == True:
        cap = cv2.VideoCapture('intro.mp4')
        if cap.isOpened():
            w = int(cap.get(4))
            h = int(cap.get(3))
            forma = (w, h)
        clip_intro = VideoFileClip('intro.mp4', target_resolution = forma, resize_algorithm = 'bilinear')
    if vinheta == True:
        cap = cv2.VideoCapture('vinheta.mp4')
        if cap.isOpened():
            w = int(cap.get(4))
            h = int(cap.get(3))
            forma = (w, h)
        clip_vinheta = VideoFileClip('vinheta.mp4', target_resolution=forma)
 
    clipes = list()
    for c in range(1, comodos):
        cap = cv2.VideoCapture('cv'+str(c)+'.mp4')
        if cap.isOpened():
            w = int(cap.get(4))
            h = int(cap.get(3))
        else: print('ERRO AO ABRIR CAPTURA COM CV2')
        forma = (w, h)

        vid = VideoFileClip('cv'+str(c)+'.mp4', target_resolution = forma, resize_algorithm = 'bilinear')
        vid = vfx.speedx(vid, velocidade[c-1])
        
        momento_do_corte = eval(info_video[coluna(videoss, 'Array_Tempos_Sheets')])
        momento_do_corte = float(momento_do_corte[c-1].replace(',','.'))

        #retornando erro em caso de clipe pequeno demais
        if vid.duration < momento_do_corte:
            problemas.append(f'VÍDEO COM DURAÇÃO INSUFICIENTE, último frame foi estendido no vídeo {c} dos cômodos')

        vid = vid.subclip(0, momento_do_corte)
        clipes.append(vid)
        print("Vídeo {} tamanho: {}".format('cv'+str(c), str(forma)))

    clipes, forma = crops(clipes, info_video[coluna(videoss, 'Orientação de Mídia')])
    w = forma[0]
    h = forma[1]
    
 #ADICIONANDO O TÍTULO DO VÍDEO
    se_legenda = bool(info_video[coluna(videoss, 'Legenda')])
    print(f'Status da legenda: {se_legenda}')
    if se_legenda == True:
        for c in range(0, len(clipes)):
            content = str(array_nomes[c])
            print(f'Legenda {c}: "{content}"')
            
            tamanho_fonte = 35
            size_clip_text = tamanho_texto(content, tamanho_fonte)

            clip = TextClip(content, fontsize = tamanho_fonte, color ="white", method='caption', size=size_clip_text, align='center', bg_color='black', )
            clip = clip.set_duration(clipes[c].duration).set_fps(60).set_position((0, forma[1] - forma[1]//4))
            clipes[c] = CompositeVideoClip([clipes[c], clip], size=forma)


#CONCATENANDO VÍDEOS E AÚDIO E APLICANDO TRANSIÇÕES
    transitar = 'slide'
    cv1 = clipes[0]
    for c in range(1, len(clipes)):
        if transitar == 'slide':
            cv1 = concatenate_videoclips([cv1.slide_in(1, 'left'), clipes[c].slide_out(1,'right')], method='compose', padding = -1)
        if transitar == 'in/out':
            cv1 = concatenate_videoclips([cv1, clipes[c].crossfadein(1)], method='compose', padding = -1)
        if transitar == 'queda':
            None
        if transitar == '':
            cv1 = concatenate_videoclips([cv1, clipes[c]], method='compose')

    final_video = cv1.set_audio(msc)
    if intro == True:
        final_video = concatenate_videoclips([clip_intro, final_video], method = "compose")
    if vinheta == True:
        clip_vinheta = clip_vinheta.fx(vfx.resize, width=forma[0])
        final_video = concatenate_videoclips([clip_vinheta, final_video], method = 'compose')
         

#IMPEDINDO QUE O VÍDEO PASSE DA DURAÇÃO IDEAL
    duration = final_video.duration
    final_video = final_video.subclip(0,duration)


#ADICIONANDO MARCA D'AGUA VIDEOGOAT
    fps = final_video.fps

    if bool(info_video[coluna(videoss, 'Marca Dágua')]) == True:
        mark_video = ImageClip('marcaVideoGoat.png', duration = duration).set_fps(fps)
        if h > w:
            mark_video = mark_video.fx(vfx.resize, width=w//3)
            mark_video = mark_video.set_position((w//20, h//20))
        elif h <= w:
            mark_video = mark_video.fx(vfx.resize, width=w//5)
            mark_video = mark_video.set_position((w//20, h//20))
        final_video = CompositeVideoClip([final_video, mark_video], size=forma)


#ADICIONANDO TELA DE CONTATO
    if bool(info_video[coluna(videoss, 'TelaContato')]) == True:
        email_user = info_video[coluna(videoss, "Usuario")]
        logo_coluna = coluna(usuarios, 'Logo')
        link_logo = usuarios[linha_em_coluna(usuarios, "Email", email_user)][logo_coluna]
        coletor_web.download_image('', link_logo, 'logo')

     #DEFININDO TEXTO PARA A TELA DE CONTATO
        user = usuarios[linha_em_coluna(usuarios, "Email", email_user)][coluna(usuarios, 'Nome')]
        numero = usuarios[linha_em_coluna(usuarios, "Email", email_user)][coluna(usuarios, 'Telefone')]
        try:
            numero = '('+numero[0:2]+')'+numero[2:7]+'-'+numero[7:]
        except:
            None
        conta = usuarios[linha_em_coluna(usuarios, "Email", email_user)][coluna(usuarios, 'Conta')]
        text = f"{conta}\n\n{numero}\n{email_user}"

    #CALCULANDO O TAMANHO DO TEXTO PARA CONSEGUIR CENTRALIZAR ELE
        tamanho_fonte = 40
        formato_texto = tamanho_texto(text, tamanho_fonte)
        texto_tamanho_x = formato_texto[0]
        texto_tamanho_y = formato_texto[1]

    #CALCULANDO A POSIÇÃO CENTRALIZADA
        centro_x = (w - texto_tamanho_x)//2
        centro_y = (h - texto_tamanho_y)//2
        centralizado = (centro_x, centro_y)

    #CRIANDO CLIPE DE TEXTO
        tela = TextClip(text, fontsize=tamanho_fonte, color="white", method='caption', size=formato_texto, align='center', bg_color='black')
        tela = tela.set_duration(duration).set_fps(fps).set_position(centralizado)

    #IMAGEM DA CONTA DO USUÁRIO
        #if 
        img_conta = ImageClip('logo.png', duration=duration)
        if h >= w:
            img_conta = img_conta.fx(vfx.resize, width = w//4)
        elif h < w:
            img_conta = img_conta.fx(vfx.resize, width = h//4)
        img_conta = img_conta.set_fps(fps).set_position((w//2-img_conta.w//2, h//10))
    
    #IMAGEM "FEITO POR VIDEOGOAT"
        if bool(info_video[coluna(videoss, 'Marca Dágua')]) == True:
            img_goat = ImageClip('LOGOVIDEOGOAT.png', duration=duration)
            img_goat = img_goat.set_fps(fps)
            if tela.h >= tela.w:
                img_goat = img_goat.fx(vfx.resize, width = (w//3)*2)
                img_goat = img_goat.set_position((w//2-(w//3), h-h//4))
            elif tela.h < tela.w: #horizontal
                img_goat = img_goat.fx(vfx.resize, width = w//2)
                img_goat = img_goat.set_position((w//2 - (w//2)//2, h-h//4))
            tela = CompositeVideoClip([tela, img_goat], size=forma)

    #JUNTANDO AS PARTES DA TELA DE CONTATO
        tela = CompositeVideoClip([tela, img_conta], size=forma)

#JUNTANDO A PRIMEIRA E A SEGUNDA PARTE DO VíDEO
        final_video = concatenate_videoclips([final_video, tela], method='compose')
    
#Escrevendo Vídeo Final
    final_video.write_videofile('final.mp4', preset = 'ultrafast', fps = 60, threads=2)
    final_video.close()




    return problemas

