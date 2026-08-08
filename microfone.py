import speech_recognition as sr

reconhecedor = sr.Recognizer()

with sr.Microphone() as fonte:
    print("Fale alguma coisa...")
    audio = reconhecedor.listen(fonte)

try:
    texto = reconhecedor.recognize_google(audio, language="pt-BR")
    print("Você disse:", texto)

except sr.UnknownValueError:
    print("Não consegui entender.")

except sr.RequestError as erro:
    print("Erro no serviço de reconhecimento:", erro)