import keyboard
import sys
import os
import json
import urllib.request
import time
import re
import unicodedata
import speech_recognition as sr
from ctypes import *

# 1. Proteção para não travar com acentos via SSH
try:
    sys.stdin.reconfigure(encoding='utf-8', errors='ignore')
except Exception:
    pass

# 2. Silenciador Seguro do ALSA (Deixa o terminal limpo e o microfone livre)
try:
    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    def py_error_handler(filename, line, function, err, fmt):
        pass
    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    asound = cdll.LoadLibrary('libasound.so.2')
    asound.snd_lib_error_set_handler(c_error_handler)
except Exception:
    pass

# 3. Áudio via PipeWire/Pulse para o alto-falante Bluetooth
os.environ.setdefault("XDG_RUNTIME_DIR", "/run/user/1000")

# Garante edge-tts do venv e binarios do sistema no PATH mesmo via cron/watcher
os.environ["PATH"] = os.pathsep.join(
    [os.path.dirname(sys.executable)]
    + [p for p in os.environ.get("PATH", "").split(os.pathsep) if p]
    + ["/usr/bin", "/bin"]
)

def tocar_audio(caminho_arquivo):
    codigo = os.system(f"mpg123 -q -o pulse {caminho_arquivo}")
    if codigo != 0:
        os.system(f"mpg123 -q -a hw:2,0 {caminho_arquivo}")

# --- FUNÇÕES DE ÁUDIO, VOZ E IA ---

def falar(texto, nome_arquivo="fala_ia.mp3", salvar_cache=False):
    try:
        voz = "pt-BR-AntonioNeural" 
        
        # Memória RAM (/dev/shm) para a IA falar rápido e SD para o Cache
        caminho_arquivo = nome_arquivo if salvar_cache else f"/dev/shm/{nome_arquivo}"
        
        # Se for do roteiro e já existir, toca com o mpg123
        if salvar_cache and os.path.exists(caminho_arquivo):
            tocar_audio(caminho_arquivo)
            return
        
        # Pede para a Microsoft gerar a voz (Edge-TTS)
        comando_gerar = f'edge-tts --text "{texto}" --voice {voz} --write-media {caminho_arquivo}'
        os.system(comando_gerar)
        
        # Toca usando o mpg123
        if os.path.exists(caminho_arquivo):
            tocar_audio(caminho_arquivo)
        else:
            print("❌ [Erro: O áudio não foi gerado]")
        
    except Exception as erro:
        print(f"Erro no áudio: {erro}")
    finally:
        if not salvar_cache and os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)

def ouvir_microfone(tempo_espera=4):
    reconhecedor = sr.Recognizer()
    reconhecedor.pause_threshold = 2.0  # 2s de silencio encerram a fala
    
    with sr.Microphone() as fonte:
        print("\n🎤 [Ajustando ruído ambiente...]")
        reconhecedor.adjust_for_ambient_noise(fonte, duration=1)
        
        print("🎤 [Ouvindo... Pode falar!]")
        try:
            # Espera a fala comecar e limita a frase a 15 segundos
            audio = reconhecedor.listen(fonte, timeout=tempo_espera, phrase_time_limit=15)
            
            print("⏳ [Traduzindo voz para texto...]")
            texto = reconhecedor.recognize_google(audio, language='pt-BR')
            print(f"👤 Visitante disse: {texto}")
            return texto
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("❌ [Não entendi o que foi dito. Pode repetir?]")
            falar("Não entendi, pode repetir?", "cache_nao_entendi.mp3", salvar_cache=True)
            return ""
        except sr.RequestError as e:
            print(f"❌ [Erro de conexão com o Google: {e}]")
            return ""

def carregar_chave_deepseek():
    chave = os.environ.get("DEEPSEEK_API_KEY", "")
    if chave:
        return chave
    caminho_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(caminho_env):
        with open(caminho_env, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                if linha.strip().startswith("DEEPSEEK_API_KEY="):
                    return linha.split("=", 1)[1].strip().strip('"').strip("'")
    return ""

def perguntar_ao_deepseek(regras, conhecimento, pergunta):
    api_key = carregar_chave_deepseek()
    url = "https://api.deepseek.com/chat/completions"
    
    contexto_sistema = f"""
    INSTRUÇÕES DE COMPORTAMENTO: {regras}
    REGRA DE OURO INQUEBRÁVEL: Seja extremamente breve e vá direto ao ponto! Responda SEMPRE usando apenas 1 frase curta (máximo de 15 a 20 palavras). Nunca dê explicações longas ou detalhes desnecessários.
    BASE DE DADOS DO PROJETO: {conhecimento}
    """
    
    dados_dict = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": contexto_sistema},
            {"role": "user", "content": pergunta}
        ],
        "temperature": 0.7
    }
    dados = json.dumps(dados_dict).encode("utf-8")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    req = urllib.request.Request(url, data=dados, headers=headers)
    
    tentativas = 3
    for tentativa in range(tentativas):
        try:
            with urllib.request.urlopen(req) as resposta:
                resultado = json.loads(resposta.read().decode("utf-8"))
                texto_bruto = resultado['choices'][0]['message']['content']
                return re.sub(r'[*#_`"]', '', texto_bruto)
        except Exception as erro:
            print(f"❌ [Erro na conexão com DeepSeek: {erro}]")
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
        "regras.txt": "Você é um robô educado da FETIN. Use linguagem falada de forma amigável. Se a resposta não estiver na BASE DE DADOS, diga que não tem essa informação e não invente nada.",
        "conhecimento.txt": "O nosso projeto é um robô assistente. Ele usa uma Raspberry Pi, programação em Python e a Inteligência Artificial. Nosso grupo trabalhou nesse protótipo.",
        "apresentacao.txt": "Olá! Sejam muito bem-vindos ao nosso estande na FETIN. É um prazer receber vocês.",
        "tema1.txt": "Vamos começar falando do nosso projeto. Nós desenvolvemos um assistente inteligente usando Python e a placa Raspberry Pi.",
        "tema2.txt": "Agora a segunda parte: nós conectamos esse sistema à inteligência artificial para ele conseguir conversar de forma natural e inteligente.",
        "encerramento.txt": "E com isso encerramos a nossa apresentação. Muito obrigado pela atenção de todos e aproveitem a feira!"
    }
    for nome_arquivo, conteudo in arquivos.items():
        if not os.path.exists(nome_arquivo):
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)

TEMPO_SEM_PERGUNTA = 10

PALAVRAS_AVANCO = {'nao', 'nenhuma', 'seguir', 'continuar', 'proximo', 'proxima'}
EXPRESSOES_AVANCO = ('nao tenho', 'sem duvida', 'pode seguir', 'pode continuar', 'sem mais', 'nao obrigado', 'nao precisa', 'nao muito obrigado', 'nao valeu', 'era so isso', 'e so isso')
EXCECOES_AVANCO = ('nao entendi', 'nao sei', 'nao entendia')

def sem_acentos(texto):
    return unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')

def eh_pedido_de_avancar(texto):
    limpo = sem_acentos(re.sub(r'[^\w\s]', ' ', texto.lower()))
    limpo = ' '.join(limpo.split())
    palavras = limpo.split()

    if not palavras or len(palavras) > 4:
        return False
    if any(excecao in limpo for excecao in EXCECOES_AVANCO):
        return False
    if len(palavras) == 1 and palavras[0] in PALAVRAS_AVANCO:
        return True
    if any(expressao in limpo for expressao in EXPRESSOES_AVANCO):
        return True
    if palavras[0] == 'nao':
        return True
    return len(palavras) <= 3 and palavras[-1] == 'nao'

def sessao_de_duvidas(fase_nome, regras, conhecimento, fala_transicao="Perfeito, vamos continuar então.", arquivo_transicao="cache_continuar.mp3"):
    print(f"\n--- Sessão de Dúvidas: {fase_nome} ---")
    falar("Alguém tem alguma dúvida sobre essa parte?", "cache_pergunta_duvida.mp3", salvar_cache=True)
    
    while True:
        inicio_espera = time.time()
        pergunta = ""
        
        while not pergunta:
            restante = TEMPO_SEM_PERGUNTA - (time.time() - inicio_espera)
            if restante <= 0:
                break
            pergunta = ouvir_microfone(tempo_espera=min(restante, 4))
        
        if not pergunta:
            print(f">>> {TEMPO_SEM_PERGUNTA}s sem pergunta. Seguindo a apresentação...\n")
            if fala_transicao:
                falar(fala_transicao, arquivo_transicao, salvar_cache=True)
            break
        
        if eh_pedido_de_avancar(pergunta):
            print(">>> Pedido de avanço detectado. Seguindo...\n")
            if fala_transicao:
                falar(fala_transicao, arquivo_transicao, salvar_cache=True)
            break
            
        print("Pensando...")
        resposta_ia = perguntar_ao_deepseek(regras, conhecimento, pergunta)
        print(f"Robô: {resposta_ia}")
        falar(resposta_ia)
        
        # Robô devolve a bola para o público
        falar("Mais alguma dúvida?", "cache_mais_duvidas.mp3", salvar_cache=True)

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
    falar(txt_intro, "cache_intro.mp3", salvar_cache=True)
    
    # 2. TEMA 1
    txt_tema1 = ler_arquivo("tema1.txt")
    print("\nRobô:", txt_tema1)
    falar(txt_tema1, "cache_tema1.mp3", salvar_cache=True)
    
    # 3. PAUSA PARA DÚVIDAS (TEMA 1)
    sessao_de_duvidas("Tema 1", regras_ia, conhecimento_ia)
    
    # 4. TEMA 2
    txt_tema2 = ler_arquivo("tema2.txt")
    print("\nRobô:", txt_tema2)
    falar(txt_tema2, "cache_tema2.mp3", salvar_cache=True)
    
    # 5. PAUSA PARA DÚVIDAS (TEMA 2) - Sem transição para ir direto pro encerramento
    sessao_de_duvidas("Tema 2", regras_ia, conhecimento_ia, fala_transicao="", arquivo_transicao="")
    
    # 6. ENCERRAMENTO
    txt_fim = ler_arquivo("encerramento.txt")
    print("\nRobô:", txt_fim)
    falar(txt_fim, "cache_fim.mp3", salvar_cache=True)
    
    print("\n--- Apresentação Concluída! ---")
