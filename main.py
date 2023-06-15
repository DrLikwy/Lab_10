# Третьяк Елизавета

import json
import requests
import pyttsx3, pyaudio, vosk

tts = pyttsx3.init('sapi5')
rate = tts.getProperty('rate') # Задаём скорость произношения
tts.setProperty('rate', rate-30)

volume = tts.getProperty('volume') #Устанавливаем громкость голоса
tts.setProperty('volume', volume+1.0)

voices = tts.getProperty('voices')
tts.setProperty('voices', 'en')

for voice in voices:
    print(voice)
    if voice.name == 'Microsoft Zira Desktop - English (United States)':
        tts.setProperty('voice', voice.id) # Выбрали, с кем хотим общаться

model = vosk.Model('model_small_en')
record = vosk.KaldiRecognizer(model, 16000)
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=16000,
                 input=True,
                 frames_per_buffer=8000)
stream.start_stream()

def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if record.AcceptWaveform(data) and len(data) > 0:
            answer = json.loads(record.Result())
            if answer['text']:
                yield answer['text']

def speak(say):
    tts.say(say)
    print(say)
    tts.runAndWait()

speak('Hello, let us laugh together! Only ask and I will find the best joke for you')

present_joke = []

for text in listen():
    if text in ['close','goodbye']: # Если хотим выключить ассистента
        quit()
    elif text in ['joke','tell me joke','make me laugh','next joke', 'another one']: # Новая шутка
        res = requests.get("https://v2.jokeapi.dev/joke/Any")
        last_joke = present_joke
        present_joke = res.json()
        if present_joke['type'] == 'twopart':
            speak(present_joke['setup'])
            speak(present_joke['delivery'])
        elif present_joke['type'] == 'single':
            speak(present_joke['joke'])

    elif text in ['what type is it','type']: # Узнать тип шутки: диалог или высказывание
        if present_joke == []:
            speak('oh, I have not joked yet')
        elif present_joke['type'] == 'twopart':
            speak("It is a dialog")
        elif present_joke['type'] == 'single':
            speak('It was said by one person')

    elif text in ['save it', 'good joke']: # Записать шутку в файл
        if present_joke == []:
            speak('oh, I have not joked yet')
        elif present_joke['type'] == 'twopart':
            with open('My JokeNote.txt', 'r+') as file:
                file.write(present_joke['setup'])
                file.write(present_joke['delivery'] + '\n')
                file.close()
                speak('I have written it down to your JokeNote')
        elif present_joke['type'] == 'single':
            with open('My JokeNote.txt', 'r+') as file:
                file.write(present_joke['joke'] + '\n')
                file.close()
                speak ('I have written it down to your JokeNote')

    elif text in ['what category','category']: # Узнать категорию шутки
        if present_joke == []:
            speak('oh, I have not joked yet')
        else:
            speak(present_joke['category'])

    elif text in ['thank you']: # Поблагодарить ассистента за хорошие шутки
            speak("I really love to listen to your laugh, you're welcome")

    else:
        speak("Sorry, I have not recognized the command. Repeat please   " )