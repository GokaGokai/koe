# Author: GokaGokai (@GokaGokai on GitHub)
# Date: 4/7/2023
# Description: Text-to-speech listener (Windows) v6.1
import json
import os
import time
from pygame import mixer
import pyttsx3
import win32clipboard
import keyboard
import queue
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from translate import Translator
os.system('start cmd /c mode con: cols=56 lines=18 && mode con: cols=56 lines=18 && title 声')
langs = ["","en", "fr", "ja"]   # "" is autodetect
ver = "v6.1"


# ------------------
# Internal functions
# ------------------   
mixer.init()
engine = pyttsx3.init()
detectedLang = ""
task_queue = queue.Queue()

def speak(text):
    global started
    global paused
    started = True
    paused = False

    voiceSetup()
    
    # Warning for SelectForceLang on limits per day
    if "MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS" in text:
        print(text)

    try:
        outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp.wav')
        engine.save_to_file(text, outfile)
        engine.runAndWait()

        mixer.music.load(outfile)
        mixer.music.play()
    except Exception as e:
        # print("Error", e)
        return

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
        # print("Error translating text:", e)
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

            try:
                win32clipboard.OpenClipboard()
                if not win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                    win32clipboard.CloseClipboard()
                    return
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
            except Exception as e:
                # print("Error accessing clipboard:", e)
                return
            
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

    stop()
    if langs[selectedLang] == "":
        speak("Auto")
    elif langs[selectedLang] == "en":
        speak("English")
    elif langs[selectedLang] == "fr":
        speak("Francais")
    elif langs[selectedLang] == "ja":
        speak("にほんご")

    print(f"{'Listening ' + additional + langs[selectedLang]:<{os.get_terminal_size().columns}}", end="\r")

def toggleListen():
    global listening
    if langs[selectedLang] == "":
        additional = ""
    else:
        additional = "and Speaking in "

    stop()
    if listening:
        listening= False
        speak("Ignoring")
        print(f"{'Ignoring':<{os.get_terminal_size().columns}}", end="\r")
    elif not listening:
        listening = True
        speak("Listening")
        print(f"{'Listening ' + additional + langs[selectedLang]:<{os.get_terminal_size().columns}}", end="\r")

def interrupt():
    global paused
    global started

    if paused and started:
        mixer.music.unpause()
        paused= False
    elif not paused and started:
        mixer.music.pause()
        paused = True

keyboard.add_hotkey("ctrl+c", lambda: task_queue.put("action"))
keyboard.add_hotkey("ctrl+alt", lambda: task_queue.put("interrupt"))
keyboard.add_hotkey("ctrl+shift+x", lambda: task_queue.put("toggleListen"))
keyboard.add_hotkey("ctrl+shift+alt+x", lambda: task_queue.put("selectForceLang"))
keyboard.add_hotkey("ctrl+alt+p", lambda: task_queue.put("selectVoicesSpeeds"))


# ------------------------
# Saves and load config
# ------------------------
config_file = "config.json"

def get_config_path():
    app_name = "Koe"
    local_app_data = os.environ.get("LOCALAPPDATA")
    config_folder = os.path.join(local_app_data, app_name)
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)
    config_path = os.path.join(config_folder, "config.json")
    return config_path

def save_config(enIndex, frIndex, jpIndex, enRate, frRate, jpRate):
    config_path = get_config_path()
    config = {
        "enIndex": enIndex,
        "frIndex": frIndex,
        "jpIndex": jpIndex,
        "enRate": enRate,
        "frRate": frRate,
        "jpRate": jpRate
    }
    with open(config_path, "w") as f:
        json.dump(config, f)
        
def reset_config():
    config = {}

    config_path = get_config_path()

    with open(config_path, "w") as f:
        json.dump(config, f)

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = {"EN": None, "FR": None, "JP": None, "EN_rate": None, "FR_rate": None, "JP_rate": None}
    return config
    
def selectVoicesSpeeds():
    print("\n" * 30)
    print("------------------------------------------------")
    print("    koe")
    print("    " + ver)
    print("  by GokaGokai")
    print("------------------------------------------------")
    print("\nAfter selecting voices and speed rates, leave it in the background\n")

    reset_config()
    printSelectVoices()
    printSelectRate()
    save_config(enIndex, frIndex, jpIndex, enRate, frRate, jpRate)

    if langs[selectedLang] == "":
        additional = ""
    else:
        additional = "and Speaking in "

    printMenu()

    stop()
    if not listening:
        speak("Ignoring")
        print(f"{'Ignoring':<{os.get_terminal_size().columns}}", end="\r")
    elif listening:
        speak("Listening")
        print(f"{'Listening ' + additional + langs[selectedLang]:<{os.get_terminal_size().columns}}", end="\r")


# ------
# Prints
# ------
enIndex = 0
frIndex = 0
jpIndex = 0
enRate = 100
frRate = 100
jpRate = 100

def get_integer_input(prompt, min_value, max_value):
    while True:
        try:
            value = int(input(prompt))
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Please enter a value between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def printSelectVoices():
    global enIndex
    global frIndex
    global jpIndex

    config = load_config()
    if config is not None and "enIndex" in config and "frIndex" in config and "jpIndex" in config:
        enIndex = config["enIndex"]
        frIndex = config["frIndex"]
        jpIndex = config["jpIndex"]
        print("Using voice indices from config file.")
    else:
        voices = engine.getProperty('voices')
        i = 0

        print("------")
        for voice in voices:
            elements = voice.id.split("\\")
            last_element = elements[-1]
            print(str(i) + " - " + last_element)
            i += 1

        print("\nIf you don't see the language, just type 0 for now")
        enIndex = get_integer_input("What to choose for EN? [0-" + str(i-1) + "] ", 0, i-1)
        frIndex = get_integer_input("What to choose for FR? [0-" + str(i-1) + "] ", 0, i-1)
        jpIndex = get_integer_input("What to choose for JP? [0-" + str(i-1) + "] ", 0, i-1)
        print("\nGotcha!\n\n")

def printSelectRate():
    global enRate
    global frRate
    global jpRate

    config = load_config()
    if config is not None and "enRate" in config and "frRate" in config and "jpRate" in config:
        enRate = config["enRate"]
        frRate = config["frRate"]
        jpRate = config["jpRate"]
        print("Using speed rates from config file.")
    else:
        print("------")
        print("\nFor reference, the normal Speed is 100")
        enRate = get_integer_input("Speed Rate for EN? [1-500] ", 1, 500)
        frRate = get_integer_input("Speed Rate for FR? [1-500] ", 1, 500)
        jpRate = get_integer_input("Speed Rate for JP? [1-500] ", 1, 500)
        
        print("\nGotcha!\n\n")

def printPrompt():
    print("\n" * 30)
    print("------------------------------------------------")
    print("    koe")
    print("    " + ver)
    print("  by GokaGokai")
    print("------------------------------------------------")
    print("\nAfter selecting voices and speed rates, leave it in the background\n")
    printSelectVoices()
    printSelectRate()
    save_config(enIndex, frIndex, jpIndex, enRate, frRate, jpRate)
    printMenu()

def printMenu():
    print("\n" * 30)
    print("------------------------------------------------")
    print("    koe")
    print("    " + ver)
    print("  by GokaGokai")
    print("------------------------------------------------")
    print("\nLeave it in the background\n")
    print("Speak:               ctrl+c")
    print("Interrupt:           ctrl+alt")
    print("ToggleListen:        ctrl+shift+x")
    print("SelectForceLang:     ctrl+shift+alt+x")
    print("SelectVoicesSpeeds:  ctrl+alt+p")
    print("\n")
    print("---Status---")

# ------
# Main
# ------
printPrompt()
toggleListen()

try:
    while True:
        task = task_queue.get()
        if task == "action":
            action()
        elif task == "interrupt":
            interrupt()
        elif task == "toggleListen":
            toggleListen()
        elif task == "selectForceLang":
            selectForceLang()
        elif task == "selectVoicesSpeeds":
            selectVoicesSpeeds()

except KeyboardInterrupt:
    print("\nExiting the program...")