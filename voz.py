import asyncio
import edge_tts
import pygame
import threading
import os

PASTA_AUDIO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "audio"
)

pygame.mixer.init()

thread_audio = None
id_audio = 0
bloqueio = threading.Lock()


async def criar_audio(texto, arquivo):

    os.makedirs(PASTA_AUDIO, exist_ok=True)

    comunicacao = edge_tts.Communicate(
        texto,
        voice="pt-BR-AntonioNeural"
    )

    await comunicacao.save(arquivo)


def falar(texto, meu_id):

    arquivo = os.path.join(
        PASTA_AUDIO,
        f"resposta_{meu_id}.mp3"
    )

    try:

        # Cria o áudio
        asyncio.run(criar_audio(texto, arquivo))

        # Verifica se esse áudio ainda é válido
        with bloqueio:
            if meu_id != id_audio:
                return

        # Carrega e toca
        pygame.mixer.music.load(arquivo)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():

            with bloqueio:
                if meu_id != id_audio:
                    pygame.mixer.music.stop()
                    break

            pygame.time.Clock().tick(10)

    except Exception as erro:

        print("Erro no áudio:", erro)

    finally:

        try:
            if os.path.exists(arquivo):
                os.remove(arquivo)
        except:
            pass


def falar_thread(texto):

    global thread_audio
    global id_audio

    with bloqueio:
        id_audio += 1
        meu_id = id_audio

    thread_audio = threading.Thread(
        target=falar,
        args=(texto, meu_id),
        daemon=True
    )

    thread_audio.start()


def parar_audio():

    global id_audio

    with bloqueio:
        id_audio += 1

    pygame.mixer.music.stop()