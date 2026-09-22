import os
import time
from gtts import gTTS
import pygame

def inicializar_audio():
    pygame.mixer.init()

def falar(texto):
    print(f"Gerando áudio para: '{texto}'")
    tts = gTTS(text=texto, lang='pt')
    
    arquivo_temp = "resposta_temporaria.mp3"
    tts.save(arquivo_temp)
    print("Áudio salvo. Iniciando reprodução...")
    
    pygame.mixer.music.load(arquivo_temp)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
        
    print("Reprodução concluída.")
    os.remove(arquivo_temp)

if __name__ == "__main__":
    inicializar_audio()
    time.sleep(0.5) 
    falar("TESTE de audio comcluido com sucesso aaaaaaaaaaaAAAAAAAAAAAAAAAAAA.")
