from ia import perguntar
from util import limpar_texto
from voz import falar_thread, parar_audio

while True:
    texto = input("Você: ")

    if texto.lower() == "sair":
        break

    resposta = perguntar(texto)

    resposta = limpar_texto(resposta)

    print("IA:", resposta)

    falar_thread(resposta)