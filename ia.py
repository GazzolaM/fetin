from openai import OpenAI
from config import API_KEY, BASE_URL, MODELO
from memoria import carregar_historico, salvar_conversa

import os


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)


# =========================
# CONHECIMENTO
# =========================

ARQUIVO_CONHECIMENTO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "conhecimento.txt"
)


with open(
    ARQUIVO_CONHECIMENTO,
    "r",
    encoding="utf-8"
) as arquivo:

    conhecimento = arquivo.read()


# =========================
# HISTÓRICO
# =========================

historico_salvo = carregar_historico()


historico = [
    {
        "role": "system",
        "content": (
            "Você é um assistente virtual que responde sempre "
            "em português do Brasil. "

            "Quando o assunto for programação, "
            "explique primeiro em português. "

            "Evite responder em inglês desnecessariamente.\n\n"

            "Você possui um conhecimento fornecido pelo usuário. "
            "Quando a pergunta estiver relacionada a esse conhecimento, "
            "use-o como fonte principal e não invente informações.\n\n"

            "Se a pergunta não estiver relacionada ao conhecimento "
            "fornecido, você pode responder normalmente usando "
            "seus conhecimentos gerais.\n\n"

            "CONHECIMENTO FORNECIDO PELO USUÁRIO:\n"
            "----------------------------------------\n"
            + conhecimento +
            "\n----------------------------------------"
        )
    }
]


# =========================
# RECUPERA HISTÓRICO
# =========================

for conversa in historico_salvo:

    historico.append({
        "role": "user",
        "content": conversa["usuario"]
    })

    historico.append({
        "role": "assistant",
        "content": conversa["ia"]
    })


# =========================
# PERGUNTAR
# =========================

def perguntar(pergunta):

    historico.append({
        "role": "user",
        "content": pergunta
    })

    resposta = client.chat.completions.create(
        model=MODELO,
        messages=historico
    )

    texto = resposta.choices[0].message.content

    historico.append({
        "role": "assistant",
        "content": texto
    })

    # Salva a conversa permanentemente
    salvar_conversa(
        pergunta,
        texto
    )

    return texto