import time

# Importa os módulos que você já criou!
import falar_bt
import pensar

print("--- INICIANDO O GUIA HISTÓRICO ---")

# 1. Prepara a caixa de som
falar_bt.inicializar_audio()

# Dá um tempinho para o Bluetooth acordar
time.sleep(0.5) 

# 2. Simula a entrada do usuário (Já que não temos o microfone ainda)
pergunta_simulada = "Resuma em uma frase: quem foi o inventor do telefone e em que ano?"
print(f"\n[Usuário perguntou]: {pergunta_simulada}")

# 3. Manda para o Opencode (O Motor)
print("\n[Maestro]: Enviando para o Opencode...")
resposta_da_ia = pensar.consultar_guia(pergunta_simulada)

# 4. Manda a resposta para a caixa de som (A Voz)
print(f"\n[Maestro]: Recebido! A resposta é: {resposta_da_ia}")
print("[Maestro]: Falando...")
falar_bt.falar(resposta_da_ia)

print("\n--- FIM DO TESTE ---")
