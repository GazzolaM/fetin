import sys
import os
import json
import urllib.request
import time
import re
from gtts import gTTS

def falar_com_gemini(pergunta):
    api_key = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    
    pergunta_formatada = pergunta + " (Responda de forma natural, falada e em no máximo duas frases curtas. Sem formatação especial ou emojis)."
    dados = json.dumps({"contents": [{"parts": [{"text": pergunta_formatada}]}]}).encode("utf-8")
    req = urllib.request.Request(url, data=dados, headers={'Content-Type': 'application/json'})
    
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            with urllib.request.urlopen(req) as resposta:
                resultado = json.loads(resposta.read().decode("utf-8"))
                if 'error' in resultado:
                    codigo_erro = resultado['error'].get('code', 0)
                    if codigo_erro == 503 and tentativa < tentativas - 1:
                        time.sleep(2)
                        continue
                    return f"Desculpe, o servidor retornou o erro {codigo_erro}."
                
                texto_bruto = resultado['candidates'][0]['content']['parts'][0]['text']
                # Remove caracteres especiais que travam o terminal/audio
                texto_limpo = re.sub(r'[*#_`"]', '', texto_bruto)
                return texto_limpo
        except urllib.error.HTTPError as e:
            if e.code == 503 and tentativa < tentativas - 1:
                time.sleep(2)
                continue
            return f"Erro de conexão (HTTP {e.code})."
        except Exception as erro:
            return f"Erro inesperado: {erro}"
            
    return "Servidores ocupados no momento."

def reproduzir_audio(texto):
    try:
        print("Gerando áudio...")
        tts = gTTS(text=texto, lang='pt', tld='com.br')
        tts.save("resposta.mp3")
        
        print("Reproduzindo...")
        # Executa e garante que o processo fecha
        os.system("mpg123 -q -a hw:2,0 resposta.mp3")
        
    except Exception as erro:
        print(f"Erro ao tentar falar: {erro}")
    finally:
        # Garante que o arquivo é apagado mesmo se houver erro
        if os.path.exists("resposta.mp3"):
            os.remove("resposta.mp3")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pergunta_usuario = sys.argv[1]
        print("Pensando...")
        
        resposta_ia = falar_com_gemini(pergunta_usuario)
        print(f"\nGemini: {resposta_ia}\n")
        
        reproduzir_audio(resposta_ia)
        print("Pronto!")
    else:
        print("Por favor, digite uma pergunta entre aspas após o nome do script.")
