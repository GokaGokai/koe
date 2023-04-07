# Author: GokaGokai (@GokaGokai on GitHub)
# Date: March 20, 2023
# Description: Text-to-speech listener (Windows) v5.1
import os
import time
from pygame import mixer
import pyttsx3
import win32clipboard
import keyboard
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from translate import Translator
os.system("title 声")
langs = ["","en", "fr", "ja"]   # "" is autodetect
ver = "v5.1"


# ------------------
# Internal functions
# ------------------   
mixer.init()
engine = pyttsx3.init()
detectedLang = ""

def speak(text):
    global started
    global paused
    started = True
    paused = False

    voiceSetup()

    if "MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS" in text:
        print(text)

    try:
        outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp.wav')
        engine.save_to_file(text, outfile)
        engine.runAndWait()
        mixer.music.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp.wav'))
        mixer.music.play()
    except Exception as e:
        print("Error", e)

def voiceSetup():
    voices = engine.getProperty('voices')

    if langs[selectedLang] == "":
        if detectedLang == "ja" or detectedLang == "zh-cn" or detectedLang == "ko":
            engine.setProperty('voice', voices[jpIndex].id)
            engine.setProperty('rate', jpRate)
        elif detectedLang == "fr":
            engine.setProperty('voice', voices[frIndex].id)
            engine.setProperty('rate', frRate)
        else:
            engine.setProperty('voice', voices[enIndex].id)
            engine.setProperty('rate', enRate)
            
    elif langs[selectedLang] == "en":
        engine.setProperty('voice', voices[enIndex].id)
        engine.setProperty('rate', enRate)
    elif langs[selectedLang] == "fr":
        engine.setProperty('voice', voices[frIndex].id)
        engine.setProperty('rate', frRate)
    elif langs[selectedLang] == "ja":
        engine.setProperty('voice', voices[jpIndex].id)
        engine.setProperty('rate', jpRate)
    
def translate(text):
    try:
        if detectedLang == "ja" or detectedLang == "zh-cn" or detectedLang == "ko":
            translator = Translator(langs[selectedLang], from_lang="ja")
        elif detectedLang == "fr":
            translator = Translator(langs[selectedLang], from_lang="fr")
        elif detectedLang == "en":
            translator = Translator(langs[selectedLang], from_lang="en")
        else:
            translator = Translator(langs[selectedLang])

        translation = translator.translate(text)

        return translation
    except Exception as e:
        print("Error translating text:", e)
        return text
    
def stop():
    mixer.music.stop()
    mixer.music.unload()


# ------
# Keys
# ------
DELAY = 0.05
selectedLang = 0
started = False
listening = False
paused = True

def action():
        if listening:
            # Wait for a brief moment to avoid racing conditions with clipboard updates
            time.sleep(DELAY)
            win32clipboard.OpenClipboard()
            if not win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                win32clipboard.CloseClipboard()
                return
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            stop()

            try:
                global detectedLang
                detectedLang = detect(data)
                
                if langs[selectedLang] != "" and not (langs[selectedLang] in detectedLang):
                    translatedData = translate(data)
                    speak(translate(translatedData))
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(translatedData, win32clipboard.CF_UNICODETEXT)
                    win32clipboard.CloseClipboard()
                else:
                    speak(data)

            except LangDetectException:
                # return a default language code or None if language cannot be detected
                return None

def selectForceLang():
    global selectedLang
    selectedLang += 1
    if selectedLang == len(langs):
        selectedLang = 0

    if langs[selectedLang] == "":
        additional = ""
    else:
        additional = "and Speaking in "

    print(f"Listening " + additional + langs[selectedLang] + "                                                                           ", end="\r")

def toggleListen():
    global listening
    if langs[selectedLang] == "":
        additional = ""
    else:
        additional = "and Speaking in "

    if listening:
        listening= False
        print(f"Ignoring                                                                           ", end="\r")
    elif not listening:
        listening = True
        print(f"Listening " + additional + langs[selectedLang] + "                                                                           ", end="\r")

def togglePause():
    global paused
    global started

    if paused and started:
        mixer.music.unpause()
        paused= False
    elif not paused and started:
        mixer.music.pause()
        paused = True

keyboard.add_hotkey("ctrl+c", lambda: action())
keyboard.add_hotkey("ctrl+shift+alt+x", lambda: selectForceLang())
keyboard.add_hotkey("ctrl+shift+x", lambda: toggleListen())
keyboard.add_hotkey("ctrl+alt", lambda: togglePause())


# ------
# Prints
# ------
enIndex = 0
frIndex = 0
jpIndex = 0
enRate = 100
frRate = 100
jpRate = 100

def printSelectVoices():
    global enIndex
    global frIndex
    global jpIndex
    voices = engine.getProperty('voices')
    i = 0

    print("------")
    for voice in voices:
        print(str(i) + " - " + voice.id)
        i += 1

    print("\nIf you don't see the language, just type 0 for now")
    enIndex = int(input("What to choose for EN? [0-" + str(i-1) + "] "))
    frIndex = int(input("What to choose for FR? [0-" + str(i-1) + "] "))
    jpIndex = int(input("What to choose for JP? [0-" + str(i-1) + "] "))
    print("\nGotcha!\n")

def printSelectRate():
    global enRate
    global frRate
    global jpRate

    print("------")
    print("\nFor reference, the normal Speed is 100")
    enRate = int(input("Speed Rate for EN? [1-500] "))
    frRate = int(input("Speed Rate for FR? [1-500] "))
    jpRate = int(input("Speed Rate for JP? [1-500] "))
    print("\nGotcha!\n")

def printMenu():
    print("")
    print("------------------------------------------------")
    print("    koe")
    print("    " + ver)
    print("  by GokaGokai/ JohnTitorTitor/ Kanon")
    print("------------------------------------------------")
    print("\nAfter selecting voices and speed rates, leave it in the background\n")

    printSelectVoices()
    printSelectRate()
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

    print("------------------------------------------------")
    print("    koe")
    print("    " + ver)
    print("  by GokaGokai/ JohnTitorTitor/ Kanon")
    print("------------------------------------------------")
    print("\nLeave it in the background\n")
    print("Speak:               ctrl+c")
    print("SelectForceLang:     ctrl+shift+alt+x")
    print("ToggleListen:        ctrl+shift+x")
    print("TogglePause:         ctrl+alt")
    print("")
    print("---Status---")

printMenu()
toggleListen()
keyboard.wait()
