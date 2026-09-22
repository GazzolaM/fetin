import sys
import os
import json
import urllib.request
import time
import re
import speech_recognition as sr
from ctypes import *

# 1. Proteção para não travar com acentos via SSH
try:
    sys.stdin.reconfigure(encoding='utf-8', errors='ignore')
except Exception:
    pass

# 2. Silenciador Seguro do ALSA
try:
    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    def py_error_handler(filename, line, function, err, fmt):
        pass
    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    asound = cdll.LoadLibrary('libasound.so.2')
    asound.snd_lib_error_set_handler(c_error_handler)
except Exception:
    pass

# --- FUNÇÕES DE ÁUDIO, VOZ E IA ---
def falar(texto, nome_arquivo="fala_ia.mp3", salvar_cache=False):
    try:
        voz = "pt-BR-AntonioNeural" 
        
        # Memória RAM para ser ultra-rápido
        caminho_arquivo = nome_arquivo if salvar_cache else f"/dev/shm/{nome_arquivo}"
        
        # Se for do roteiro e já existir, toca com o mpg123
        if salvar_cache and os.path.exists(caminho_arquivo):
            os.system(f"mpg123 -q -a hw:2,0 {caminho_arquivo}")
            return
        
        # Pede para a Microsoft gerar a voz
        comando_gerar = f'edge-tts --text "{texto}" --voice {voz} --write-media {caminho_arquivo}'
        os.system(comando_gerar)
        
        # Toca usando o mpg123
        if os.path.exists(caminho_arquivo):
            os.system(f"mpg123 -q -a hw:2,0 {caminho_arquivo}")
        else:
            print("❌ [Erro: O áudio não foi gerado]")
        
    except Exception as erro:
        print(f"Erro no áudio: {erro}")
    finally:
        if not salvar_cache and os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)



def ouvir_microfone():
    reconhecedor = sr.Recognizer()
    
    with sr.Microphone() as fonte:
        print("\n🎤 [Ajustando ruído ambiente...]")
        reconhecedor.adjust_for_ambient_noise(fonte, duration=1)
        
        print("🎤 [Ouvindo... Pode falar!]")
        try:
            # Escuta por até 5 segundos
            audio = reconhecedor.listen(fonte, timeout=5, phrase_time_limit=15)
            
            print("⏳ [Traduzindo voz para texto...]")
            texto = reconhecedor.recognize_google(audio, language='pt-BR')
            print(f"👤 Visitante disse: {texto}")
            return texto
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("❌ [Não entendi o que foi dito. Pode repetir?]")
            return ""
        except sr.RequestError as e:
            print(f"❌ [Erro de conexão com o Google: {e}]")
            return ""

def perguntar_ao_gemini(regras, conhecimento, pergunta):
    api_key = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    
    instrucao = f"""
    INSTRUÇÕES DE COMPORTAMENTO: {regras}
    BASE DE DADOS DO PROJETO: {conhecimento}
    PERGUNTA DO VISITANTE: {pergunta}
    """
    
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
                    return "Erro no servidor do Google."
                
                texto_bruto = resultado['candidates'][0]['content']['parts'][0]['text']
                return re.sub(r'[*#_`"]', '', texto_bruto)
        except Exception:
            if tentativa < tentativas - 1:
                time.sleep(2)
                continue
    return "Desculpe, os servidores estão ocupados no momento."

# --- FUNÇÕES DO ROTEIRO ---

def ler_arquivo(nome):
    with open(nome, 'r', encoding='utf-8') as f:
        return f.read().strip()

def criar_arquivos_se_nao_existirem():
    arquivos = {
        "regras.txt": "Você é um robô educado da FETIN. Responda em até 2 frases curtas. Use linguagem falada. Se a resposta não estiver na BASE DE DADOS, diga que não tem essa informação.",
        "conhecimento.txt": "O nosso projeto é um robô assistente. Ele usa uma Raspberry Pi, programação em Python e Inteligência Artificial. Trabalhamos 3 meses no protótipo.",
        "apresentacao.txt": "Olá! Sejam muito bem-vindos ao nosso estande na FETIN. É um prazer receber vocês.",
        "tema1.txt": "Vamos começar falando do projeto. Desenvolvemos um assistente inteligente usando Python e a placa Raspberry Pi.",
        "tema2.txt": "Agora a segunda parte: conectamos esse sistema à inteligência artificial do Google para ele conversar de forma inteligente.",
        "encerramento.txt": "E com isso encerramos a nossa apresentação. Muito obrigado pela atenção de todos e aproveitem a feira!"
    }
    for nome_arquivo, conteudo in arquivos.items():
        if not os.path.exists(nome_arquivo):
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)

def sessao_de_duvidas(fase_nome, regras, conhecimento, fala_transicao="Perfeito, vamos continuar então.", arquivo_transicao="cache_continuar.wav"):
    print(f"\n--- Sessão de Dúvidas: {fase_nome} ---")
    falar("Alguém tem alguma dúvida sobre essa parte?", "cache_pergunta_duvida.wav", salvar_cache=True)
    
    while True:
        pergunta = ouvir_microfone()
        
        if not pergunta:
            continue
            
        texto_limpo = pergunta.strip().lower()
        palavras_avanco = ['nao', 'não', 'não.', 'nao.', 'não tenho', 'nenhuma', 'pode seguir', 'continuar', 'sem duvidas', 'sem dúvidas', 'não tenho dúvidas', 'seguir']
        
        if texto_limpo in palavras_avanco:
            print(">>> Avançando para a próxima etapa...\n")
            if fala_transicao:
                falar(fala_transicao, arquivo_transicao, salvar_cache=True)
            break
            
        print("Pensando...")
        resposta_ia = perguntar_ao_gemini(regras, conhecimento, pergunta)
        print(f"Robô: {resposta_ia}")
        falar(resposta_ia)
        
        # --- NOVO: Pergunta novamente após responder ---
        falar("Mais alguma dúvida?", "cache_mais_duvidas.wav", salvar_cache=True)

# --- EXECUÇÃO PRINCIPAL ---

if __name__ == "__main__":
    print("Preparando o Robô Guia...")
    criar_arquivos_se_nao_existirem()
    
    regras_ia = ler_arquivo("regras.txt")
    conhecimento_ia = ler_arquivo("conhecimento.txt")
    
    print("\n==================================")
    print("🎭 INICIANDO APRESENTAÇÃO FETIN")
    print("==================================\n")
    
    # 1. BOAS VINDAS
    txt_intro = ler_arquivo("apresentacao.txt")
    print("Robô:", txt_intro)
    falar(txt_intro, "cache_intro.wav", salvar_cache=True)
    
    # 2. TEMA 1
    txt_tema1 = ler_arquivo("tema1.txt")
    print("\nRobô:", txt_tema1)
    falar(txt_tema1, "cache_tema1.wav", salvar_cache=True)
    
    # 3. PAUSA PARA DÚVIDAS (TEMA 1)
    sessao_de_duvidas("Tema 1", regras_ia, conhecimento_ia)
    
    # 4. TEMA 2
    txt_tema2 = ler_arquivo("tema2.txt")
    print("\nRobô:", txt_tema2)
    falar(txt_tema2, "cache_tema2.wav", salvar_cache=True)
    
    # 5. PAUSA PARA DÚVIDAS (TEMA 2) - SEM TRANSIÇÃO
    sessao_de_duvidas("Tema 2", regras_ia, conhecimento_ia, fala_transicao="", arquivo_transicao="")
    
    # 6. ENCERRAMENTO
    txt_fim = ler_arquivo("encerramento.txt")
    print("\nRobô:", txt_fim)
    falar(txt_fim, "cache_fim.wav", salvar_cache=True)
    
    print("\n--- Apresentação Concluída! ---")
