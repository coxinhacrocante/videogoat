import dataclasses
import coletor_web
import editor
import enviar_email
import gerador_link
import sheets
import os
import time
from moviepy.editor import *
from moviepy.video import *
from moviepy.audio import *

def coluna(lista, alvo):
    numero_coluna = lista[0].index(alvo)
    return numero_coluna

def linha_em_coluna(lista, alvo_coluna, alvo_linha):
    numero_coluna = lista[0].index(alvo_coluna)
    for a in range(0, len(lista)):
        if lista[a][numero_coluna] == alvo_linha:
            return a

while True:
    
    #controle de tempo para idenficar atividde do servidor
    data = time.localtime()
    data_str = str(data.tm_year)+str(data.tm_mon)+str(data.tm_hour)
    data_min = int(data.tm_min)
    try:
        with open('DADOS.txt', 'w') as da:
            da.write(data_str)
            da.write('\n')
            da.write(str(data_min))
    except Exception as e:
        print(f"problema no centro acessar os dados de tempo {e}")

    ocorreu_edit = False
    try:
        SH = sheets.Sheets()
        templates = SH.receber("Templates!A1:AH")
        range_videos = "Videos!A1:CG"
        videos = SH.receber(range_videos)

        #Coletar informações de usuário
        usuarios = SH.receber("Usuários!A1:S")
        

        #conferir qual vídeo deve ser editada
        linhas_para_editar = list()
        for linha in range(1,len(videos)):
            print(len(videos[linha]))
            if videos[linha][coluna(videos, 'Processamento/Status')] == '' and videos[linha][coluna(videos, 'Template/Nome')] != '':
                linhas_para_editar.append(linha)
            elif videos[linha][coluna(videos, 'Template/Nome')] == '':
                break

        #gerar capas e atualizar status
        for c in linhas_para_editar:
            info = videos[c]
            nuvem = gerador_link.Drive()
            try:
                intro = eval(str.capitalize(str.lower(info[coluna(videos, 'Introdução?')])))
            except: 
                print("informação de introdução está incorreta, será dada como falso")
                intro = False
            comodos = int(info[coluna(videos, 'Qtd. Comodos')])
            array_videos = eval(info[coluna(videos, 'Array_Links_Sheets')])
            if intro == True:
                coletor_web.download_video('', info[coluna(videos, 'Comodos/Intro Link')], 'precapa')
            else:
                coletor_web.download_video('', array_videos[0], 'precapa')
            clip = VideoFileClip('precapa.mp4')
            clip.save_frame('capa.png', t=(0,0,0.01))
            clip.close()
            nome = "provisorio"  
            link_capa = nuvem.gerar_link(nuvem.postar(nome, 'capa.png', 'image/png'))
            videos[c][coluna(videos, 'Processamento/Capa Link')] = str(link_capa['webViewLink']) 
            videos[c][coluna(videos, 'Processamento/Etapa')] = "Na Fila"
            SH.modificar(range_videos, videos)

        #editar
        for c in linhas_para_editar:
            problemas = list()
            info = videos[c]
            comodos = int(info[coluna(videos, 'Qtd. Comodos')])


            try:
                intro = eval(str.capitalize(str.lower(info[coluna(videos, 'Introdução?')])))
            except:
                print('Intro considerada como falsa definitivamente')
                problemas.append('Erro interno na introdução, ela será desconsiderada, desculpe')
                intro = False
            print(intro)


            try:
                vinheta = eval(str.capitalize(str.lower(info[coluna(videos, 'Vinheta')])))
            except:
                print('Informações de vinheta incorretas, ela será dada como falsa')
                problemas.append('Erro interno na vinheta, ela será desconsiderada, desculpe')
                vinheta = False


            try:
                array_videos = eval(info[coluna(videos, 'Array_Links_Sheets')])
                array_tipos = eval(info[coluna(videos, 'Array_Extensoes_Sheets')])
                array_nomes = eval(info[coluna(videos, 'Array_Comodo_Sheets')])
            except:
                print('problema: Inforações de vídeo incorretas, não será possível editar')
                problemas.append('Erro interno de banco de dados, não será possível editar esse vídeo')
                continue

            #Atualizar estatus 
            videos[c][coluna(videos, 'Processamento/Etapa')] = "Criando"
            SH.modificar(range_videos, videos)

            #Download videos dos cômodos
            if intro == True:
                coletor_web.download_video('', info[coluna(videos, 'Comodos/Intro Link')], 'intro')
            elif intro == '':
                intro = False

            if vinheta == True:
                link_para_vinheta = info[coluna(videos, 'Link Vinheta')]
                if '.png' == link_para_vinheta[-4:] or '.jpg' == link_para_vinheta[-4:] :
                    coletor_web.download_image('', link_para_vinheta, 'vinheta')
                    clip_vinheta = ImageClip('vinheta.png', duration=2)
                    clip_vinheta.write_videofile('vinheta.mp4')
                    clip_vinheta.close()
                elif '.mp4'==link_para_vinheta[-4:] or '.MOV'==link_para_vinheta[-4:] or '.mv4'==link_para_vinheta[-4:] :
                    coletor_web.download_video('', link_para_vinheta, 'vinheta')
                else: problemas.append('Link para vinheta não identificado')
            elif vinheta == '':
                vinheta = False

            for a in range(1, comodos):
                if array_tipos[a] == '.mp4' or '.MP4' or '.mov' or '.MOV': 
                    coletor_web.download_video('', array_videos[a], 'cv'+str(a))
                    teste_duracao = VideoFileClip('cv'+str(a)+'.mp4')
                elif array_tipos[a] == '.png' or '.PNG' or '.jpeg' or '.JPEG':
                    coletor_web.download_image('', array_videos[a], 'cv'+str(a))
                    iclip = ImageClip('cv'+str(a)+'.png', duration = 10)
                    iclip.write_videofile('cv'+str(a)+'.mp4')
                    iclip.close()
                
            #selecionando a linha de template, apartir da escolha do usuário
            escolha_template = info[coluna(videos, 'Template/Nome')]
            try:
                template = templates[linha_em_coluna(templates, 'Template', escolha_template)]
            except:
                print("ERRO: TEMPLATE ESCOLHIDO NÃO ENCONTRADO")
                continue
            info_templates = templates[0]

            #download da música
            formato_musica = info[coluna(videos, 'Extensão Midia-Template')]
            if formato_musica == '.mp4' or formato_musica == '.MOV' or formato_musica == '.ogv' or formato_musica == '.m4v':
                coletor_web.download_video('', template[coluna(templates, 'Musica/link')], 'msc_video')
                clip_musica = VideoFileClip('msc_video.mp4')
                clip_musica = clip_musica.audio
                clip_musica.write_audiofile('msc.mp3')
                clip_musica.close()
                
            elif formato_musica == '.mp3' or formato_musica == '.WAV':
                coletor_web.download_musica('', template[coluna(templates, 'Musica/link')], 'msc')
            else:
                print('ERRO NO FORMATO DE ARQUIVO DE MÚSICA')

            #orientação do vídeo:
            orientar = info[coluna(videos, 'Orientação de Mídia')]
            #transição
            transitar = videos[c][coluna(videos, 'Transição')]

            #edição em si
            problemas = editor.executar_template(template, info_templates, int(comodos), intro, transitar, videos, info, vinheta, array_nomes, usuarios)
            ocorreu_edit = True

            #gerar link
            nome = info[coluna(videos, 'Título')]
            nuvem = gerador_link.Drive()
            link = nuvem.gerar_link(nuvem.postar(nome, 'final.mp4', 'video/mp4'))
            link = str(link['webViewLink'])  

            #escrever link
            videos[c][coluna(videos, 'Processamento/Status')] = 'Feito'
            videos[c][coluna(videos, 'Processamento/Link do Video Pronto')] = link
            videos[c][coluna(videos, 'Processamento/Etapa')] = 'Pronto'
            videos[c][coluna(videos, 'Processamento/Problema')] = str(problemas)
            SH.modificar(range_videos, videos)
        
        #emails para o povo
        for c in range(len(videos)):
            if videos[c][coluna(videos, 'notificado')] == False or videos[c][coluna(videos, 'notificado')] == '' and videos[c][coluna(videos, 'Usuario')] != '':
                alvo = videos[c][coluna(videos, 'Usuario')]
                tema = 'Seu Video Goat está pronto!'
                conteudo = 'Sua edição de vídeo com o Título de "{}" está pronta no App Vídeo Goat, vá conferir!'.format(videos[c][coluna(videos, 'Título')])
                enviar_email.enviar(alvo, tema, conteudo)
                videos[c][coluna(videos, 'notificado')] = True
                SH.modificar(range_videos, videos)

    except Exception as e:
        print('OCORREU ALGUM ERRO')
        print('LOG DO ERRO: {}'.format(e.with_traceback()))
        time.sleep(180) 
    print('TEMPO DE ESPERA')
    if ocorreu_edit == False: time.sleep(100)
    time.sleep(100)


