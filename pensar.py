import requests

# === SUBSTITUA ESTES VALORES PELOS DADOS DO SEU OPENCODE ===
OPENCODE_API_URL = "COLE_A_URL_DO_ENDPOINT_AQUI"
OPENCODE_API_KEY = ""

def consultar_guia(pergunta_usuario):
    """Envia o texto para o Opencode e retorna a resposta gerada."""
    print(f"Enviando pergunta para a nuvem: '{pergunta_usuario}'...")
    
    # Cabeçalhos de autenticação (geralmente exigidos por APIs)
    headers = {
        "Authorization": f"Bearer {OPENCODE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # O pacote de dados enviado (payload). 
    # O formato exato (se é 'message', 'text', 'prompt') depende da doc do Opencode.
    payload = {
        "message": pergunta_usuario 
    }
    
    try:
        # Faz o disparo da requisição POST
        resposta = requests.post(OPENCODE_API_URL, json=payload, headers=headers)
        
        # Verifica se deu certo (Código 200)
        if resposta.status_code == 200:
            dados_retornados = resposta.json()
            # Extrai apenas o texto da resposta do JSON (o caminho exato depende da API)
            texto_resposta = dados_retornados.get("reply", "Erro ao ler a resposta.")
            print(f"Resposta recebida: {texto_resposta}")
            return texto_resposta
        else:
            print(f"Erro na comunicação. Código: {resposta.status_code}")
            return "Ocorreu um erro de comunicação com o servidor central."
            
    except Exception as e:
        print(f"Erro crítico de rede: {e}")
        return "Não consegui acessar a rede. Verifique a conexão."

if __name__ == "__main__":
    # Teste 1: Pergunta dentro do contexto
    print("--- Teste 1: Contexto Histórico ---")
    resposta_1 = consultar_guia("Quem inventou o telefone?")
    
    print("\n--- Teste 2: Tentativa de quebra de contexto ---")
    # Teste 2: Pergunta fora do contexto para testar o filtro do Opencode
    resposta_2 = consultar_guia("Qual a previsão do tempo para amanhã em Santa Rita do Sapucaí?")
