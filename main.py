import speech_recognition as sr

def main():
    r = sr.Recognizer()
    audioFile = sr.AudioFile("test.wav")
    with audioFile as source:
        audio = r.record(audioFile)
        sentence = r.recognize_google(audio)
        print(sentence)

if __name__ == "__main__":
    main()
