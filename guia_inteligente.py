import sys
import os
import json
import urllib.request
import time
import re
from gtts import gTTS

def falar(texto):
    try:
        tts = gTTS(text=texto, lang='pt', tld='com.br')
        tts.save("fala.mp3")
        os.system("mpg123 -q fala.mp3")
    except Exception as erro:
        print(f"Erro no áudio: {erro}")
    finally:
        if os.path.exists("fala.mp3"):
            os.remove("fala.mp3")

def ler_arquivo(nome_arquivo):
    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
        return arquivo.read()

def perguntar_ao_gemini(contexto, pergunta):
    api_key = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    
    # AQUI ESTÁ O SEGREDO: Instruções rígidas para a IA
    instrucao = (
        "Você é um robô guia na feira tecnológica FETIN. "
        "Vou te passar um CONTEXTO de informações e depois uma PERGUNTA. "
        "REGRA 1: Responda a pergunta SOMENTE baseando-se no CONTEXTO. "
        "REGRA 2: Se a resposta não estiver no CONTEXTO, diga EXATAMENTE: "
        "'Desculpe, não tenho essa informação no momento.' e não invente nada. "
        "REGRA 3: Responda de forma falada, natural, em até duas frases curtas.\n\n"
        f"CONTEXTO:\n{contexto}\n\n"
        f"PERGUNTA: {pergunta}"
    )
    
    dados = json.dumps({"contents": [{"parts": [{"text": instrucao}]}]}).encode("utf-8")
    req = urllib.request.Request(url, data=dados, headers={'Content-Type': 'application/json'})
    
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            with urllib.request.urlopen(req) as resposta:
                resultado = json.loads(resposta.read().decode("utf-8"))
                if 'error' in resultado:
                    if resultado['error'].get('code') == 503 and tentativa < tentativas - 1:
                        time.sleep(2)
                        continue
                    return "Erro no servidor."
                texto_bruto = resultado['candidates'][0]['content']['parts'][0]['text']
                return re.sub(r'[*#_`"]', '', texto_bruto)
        except Exception:
            if tentativa < tentativas - 1:
                time.sleep(2)
                continue
    return "Servidores ocupados no momento."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        nome_arquivo = sys.argv[1]
        try:
            # 1. Lê o texto e guarda na memória (Contexto)
            contexto_atual = ler_arquivo(nome_arquivo)
            
            # 2. Faz a apresentação inicial em voz alta
            print("\n--- Apresentando o estande ---")
            print(contexto_atual)
            falar(contexto_atual)
            
            # 3. Entra em modo de perguntas contínuas (Loop)
            print("\n--- Modo de Dúvidas ativado! (Digite 'sair' para encerrar) ---")
            while True:
                pergunta_usuario = input("\nSua pergunta: ")
                
                if pergunta_usuario.lower() in ['sair', 'exit', 'fim']:
                    print("Encerrando o modo guia...")
                    break
                    
                print("Pensando...")
                resposta_ia = perguntar_ao_gemini(contexto_atual, pergunta_usuario)
                print(f"Guia: {resposta_ia}")
                falar(resposta_ia)
                
        except FileNotFoundError:
            print(f"Erro: O arquivo '{nome_arquivo}' não existe.")
    else:
        print("Uso correto: python guia_inteligente.py <arquivo.txt>")
