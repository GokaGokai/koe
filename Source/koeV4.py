import os
import time
from pygame import mixer
import pyttsx3
import win32clipboard
import keyboard
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

# by GokaGokai/ JohnTitorTitor/ Kanon

os.system("title 声")
mixer.init()
engine = pyttsx3.init()
paused = True
started = False
listening = False
enIndex = 0
frIndex = 0
jpIndex = 0
enRate = 100
frRate = 100
jpRate = 100

def languageSetup(text):
    lang = detect(text)
    # print(lang)
    voices = engine.getProperty('voices')
    # for voice in voices:
    #     print(voice.id)
    if lang == "ja" or lang == "zh-cn" or lang == "ko":
        engine.setProperty('voice', voices[jpIndex].id)
        engine.setProperty('rate', jpRate)
                
    elif lang == "fr":
        engine.setProperty('voice', voices[frIndex].id)
        engine.setProperty('rate', frRate)
                
    else:
        engine.setProperty('voice', voices[enIndex].id)
        engine.setProperty('rate', enRate)
                

def start(text):
    languageSetup(text)
    outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp.wav')
    engine.save_to_file(text, outfile)
    engine.runAndWait()
    
    mixer.music.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp.wav'))
    mixer.music.play()

    global started
    global paused
    started = True
    paused = False

def action():
        if listening:
            time.sleep(0.05)
            win32clipboard.OpenClipboard()
            if not win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                win32clipboard.CloseClipboard()
                return
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            stop()
            try:
                detect(data)
                start(data)
            except LangDetectException:
                # return a default language code or None if language cannot be detected
                return None
            

keyboard.add_hotkey("ctrl+c", lambda: action())
keyboard.add_hotkey("ctrl+shift+x", lambda: toggleListen())
keyboard.add_hotkey("ctrl+alt", lambda: togglePause())

def stop():
    mixer.music.stop()
    mixer.music.unload()

def toggleListen():
    global listening

    if listening:
        listening= False
        print(f"--Ignoring                                                                          ", end="\r")
    elif not listening:
        listening = True
        print(f"--Listening                                                                           ", end="\r")

def togglePause():
    global paused
    global started

    if paused and started:
        mixer.music.unpause()
        # print("in paused")
        paused= False
        # print(paused)
    elif not paused and started:
        mixer.music.pause()
        # print("in not")
        paused = True
        # print(paused)

def languageIndexSelect():
    print("------")
    voices = engine.getProperty('voices')
    i = 0
    for voice in voices:
        print(str(i) + " - " + voice.id)
        i += 1
    global enIndex
    global frIndex
    global jpIndex

    print("\nIf you don't see the language, just type 0 for now")
    enIndex = int(input("What to choose for EN? [0-" + str(i-1) + "] "))
    frIndex = int(input("What to choose for FR? [0-" + str(i-1) + "] "))
    jpIndex = int(input("What to choose for JP? [0-" + str(i-1) + "] "))
    print("\nGotcha!\n")


def rateSelect():
    global enRate
    global frRate
    global jpRate
    print("------")
    print("\nFor reference, the normal Speed is 100")
    enRate = int(input("Speed Rate for EN? [1-500] "))
    frRate = int(input("Speed Rate for FR? [1-500] "))
    jpRate = int(input("Speed Rate for JP? [1-500] "))
    print("\nGotcha!\n")


print("")
print("------------------------------------------------")
print("    koe")
print("    v4")
print("  by GokaGokai/ JohnTitorTitor/ Kanon")
print("------------------------------------------------")
print("\nAfter selecting voices and speed rates, leave it in the background\n")
languageIndexSelect()
rateSelect()
print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
print("------------------------------------------------")
print("    koe")
print("    v4")
print("  by GokaGokai/ JohnTitorTitor/ Kanon")
print("------------------------------------------------")
print("\nLeave it in the background\n")
print("Speak:        ctrl+c")
print("toggleListen: ctrl+shift+x")
print("TogglePause:  ctrl+alt")
print("\n-Status-")
toggleListen()
input("")

# keyboard.add_hotkey("ctrl+c", lambda: action())
# keyboard.add_hotkey("ctrl+shift+x", lambda: toggleListen())
# keyboard.add_hotkey("ctrl+alt", lambda: togglePause())