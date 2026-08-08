import json
import os


PASTA_MEMORIA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "memoria"
)

ARQUIVO_MEMORIA = os.path.join(
    PASTA_MEMORIA,
    "memoria.json"
)

ARQUIVO_HISTORICO = os.path.join(
    PASTA_MEMORIA,
    "historico.json"
)


def garantir_arquivos():

    os.makedirs(PASTA_MEMORIA, exist_ok=True)

    if not os.path.exists(ARQUIVO_MEMORIA):
        with open(
            ARQUIVO_MEMORIA,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                {},
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    if not os.path.exists(ARQUIVO_HISTORICO):
        with open(
            ARQUIVO_HISTORICO,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                [],
                arquivo,
                ensure_ascii=False,
                indent=4
            )


# =========================
# MEMÓRIA
# =========================

def carregar_memoria():

    garantir_arquivos()

    with open(
        ARQUIVO_MEMORIA,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(arquivo)


def salvar_memoria(memoria):

    garantir_arquivos()

    with open(
        ARQUIVO_MEMORIA,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            memoria,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


# =========================
# HISTÓRICO
# =========================

def carregar_historico():

    garantir_arquivos()

    with open(
        ARQUIVO_HISTORICO,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(arquivo)


def salvar_conversa(usuario, ia):

    historico = carregar_historico()

    historico.append({
        "usuario": usuario,
        "ia": ia
    })

    with open(
        ARQUIVO_HISTORICO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            historico,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


# =========================
# SALVAR INFORMAÇÃO
# =========================

def salvar_informacao(chave, valor):

    memoria = carregar_memoria()

    memoria[chave] = valor

    salvar_memoria(memoria)


# =========================
# BUSCAR INFORMAÇÃO
# =========================

def buscar_informacao(chave):

    memoria = carregar_memoria()

    return memoria.get(chave)