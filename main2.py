import speech_recognition as sr
import threading
import time
import pygame

from ia import perguntar
from util import limpar_texto
from voz import falar_thread, parar_audio


reconhecedor = sr.Recognizer()

parar_programa = threading.Event()
falando = threading.Event()


def monitorar_audio():
    """
    Monitora quando o áudio termina.
    """

    while not parar_programa.is_set():

        if falando.is_set():

            if not pygame.mixer.music.get_busy():
                falando.clear()

        time.sleep(0.1)


def ouvir_microfone():

    while not parar_programa.is_set():

        try:

            with sr.Microphone() as fonte:

                print("\n🎤 Ouvindo...")

                audio = reconhecedor.listen(
                    fonte,
                    timeout=None,
                    phrase_time_limit=5
                )

            texto = reconhecedor.recognize_google(
                audio,
                language="pt-BR"
            )

            texto = texto.lower().strip()

            print("Você:", texto)

            # =========================
            # SAIR
            # =========================

            if texto == "sair":

                parar_programa.set()
                parar_audio()

                break

            # =========================
            # INTERROMPER
            # =========================

            if "interromper" in texto:

                parar_audio()
                falando.clear()

                print("🔇 Áudio interrompido.")

                continue

            # =========================
            # SE A IA ESTÁ FALANDO
            # =========================

            if falando.is_set():

                print("🔊 A IA ainda está falando.")

                continue

            # =========================
            # PERGUNTA PARA A IA
            # =========================

            resposta = perguntar(texto)

            resposta = limpar_texto(resposta)

            print("IA:", resposta)

            # =========================
            # COMEÇA A FALAR
            # =========================

            falando.set()

            falar_thread(resposta)

        except sr.UnknownValueError:

            print("Não consegui entender.")

        except sr.RequestError as erro:

            print("Erro no reconhecimento de voz:", erro)

        except Exception as erro:

            print("Erro:", erro)


# =========================
# THREAD DO MONITOR
# =========================

thread_monitor = threading.Thread(
    target=monitorar_audio,
    daemon=True
)

thread_monitor.start()


# =========================
# THREAD DO MICROFONE
# =========================

thread_microfone = threading.Thread(
    target=ouvir_microfone,
    daemon=True
)

thread_microfone.start()


try:

    while not parar_programa.is_set():

        time.sleep(0.2)

except KeyboardInterrupt:

    parar_programa.set()
    parar_audio()