import re

def limpar_texto(texto):
    # Remove markdown em negrito e itálico
    texto = re.sub(r"\*\*(.*?)\*\*", r"\1", texto)
    texto = re.sub(r"\*(.*?)\*", r"\1", texto)

    # Remove crases
    texto = texto.replace("`", "")

    # Remove cabeçalhos
    texto = texto.replace("#", "")

    # Remove links markdown
    texto = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", texto)

    # Remove espaços extras
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()