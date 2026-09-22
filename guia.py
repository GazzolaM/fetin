import os
import sys # Importante para ler o que você digita no terminal
from gtts import gTTS

def reproduzir_audio(texto):
    try:
        print("Gerando áudio do texto...")
        tts = gTTS(text=texto, lang='pt', tld='com.br')
        tts.save("leitura.mp3")
        
        print("Falando...")
        os.system("mpg123 -q leitura.mp3")
        
    except Exception as erro:
        print(f"Erro ao tentar falar: {erro}")
    finally:
        if os.path.exists("leitura.mp3"):
            os.remove("leitura.mp3")

def ler_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            texto = arquivo.read()
            print("\nTexto lido do arquivo:")
            print(f"--- comece a ouvir ---\n{texto}\n--- fim do texto ---\n")
            
            reproduzir_audio(texto)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado na pasta.")

if __name__ == "__main__":
    # Verifica se você digitou o nome de um arquivo
    if len(sys.argv) > 1:
        arquivo_escolhido = sys.argv[1]
        ler_arquivo(arquivo_escolhido)
    else:
        print("Uso correto: python guia.py <nome_do_arquivo.txt>")
