#!/bin/bash

PERGUNTA=$1

# Pega a resposta do Gemini e salva na variável (sem imprimir ainda)
RESPOSTA=$(curl -s -H 'Content-Type: application/json' \
     -d '{
           "contents": [{
             "parts": [{"text": "'"$PERGUNTA"'"}]
           }]
         }' \
     -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key=${GEMINI_API_KEY}" | jq -r '.candidates[0].content.parts[0].text')

# Imprime a resposta na tela para você ler
echo "$RESPOSTA"

# Manda a Raspberry Pi falar a resposta (em português do Brasil)
espeak-ng -v pt-br "$RESPOSTA"
