import speech_recognition as sr
import pyttsx3
import os
import subprocess
import webbrowser
import pywhatkit
import sounddevice as sd
from scipy.io import wavfile
import time
import threading
import datetime
from pathlib import Path
from google import genai
from google.genai import types

try:
    client = genai.Client()
    AI_BRAIN_ACTIVE = True
    print("[STATUS] AI Brain (Gemini API) initialized successfully.")
except Exception as e:
    AI_BRAIN_ACTIVE = False
    print(f"[WARNING] AI Brain failed to initialize. System running offline: {e}")

print("[VERIFICATION] Modern Python 3.14 libraries loaded successfully.")



def speak(text):
    print(f"Jarvis: {text}")
    try:
        engine = pyttsx3.init('sapi5')
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[ERROR] Text-to-speech failed: {e}")
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as fallback_error:
            print(f"[ERROR] Fallback engine also failed: {fallback_error}")
        
def ask_ai_brain(prompt):
    """Sends unmapped commands to the Gemini LLM for a smart response."""
    if not AI_BRAIN_ACTIVE:
        return "My cloud network is currently offline, Rakesh. I can only perform local commands."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="You are Jarvis, a highly advanced, witty, and helpful AI assistant. Keep responses short, direct, and conversational for text-to-speech.",
                max_output_tokens=150,
                temperature=0.7
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Gemini API execution failed: {e}")
        return "I encountered a connectivity glitch inside my neural array."

def listen_command(seconds=4): 
    fs = 44100  
    temp_filename = "temp_voice.wav"

    print(f"\n[STATUS] Jarvis is listening ({seconds}-second window)...")
    

    print("\n[STATUS] Jarvis is listening (4-second window)...")
    
    try:
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  
        wavfile.write(temp_filename, fs, myrecording)

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_filename) as source:
            audio = recognizer.record(source)
        
        print("[STATUS] Processing audio...")
        command = recognizer.recognize_google(audio)
        print(f"[USER]: {command}")
        
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        return command.lower().strip()
        
    except sr.UnknownValueError:
        print("[OUTPUT] Audio heard, but intent unclear.")
        return ""
    except Exception as e:
        print(f"[STATUS] Listening window closed or reset: {e}")
        if os.path.exists(temp_filename):
            try: os.remove(temp_filename)
            except: pass
        return ""

if __name__ == "__main__":
    speak("Phase two systems operational. Systems online, Rakesh.")
    
    is_awakened = False
    last_activity_time = time.time()
    SESSION_TIMEOUT = 15 
    
    while True:
        current_time = time.time()
        
        if is_awakened and (current_time - last_activity_time > SESSION_TIMEOUT):
            print("[STATUS] Session timed out due to inactivity. Re-entering passive scanning mode.")
            is_awakened = False
            
        if not is_awakened:
            print("[PASSIVE MODE] Scanning ambient audio (Short 2s window)...")
            ambient_input = listen_command(seconds=2)
            
            if any(wake in ambient_input for wake in ["jarvis", "wake up", "hey jarvis"]):
                print("\n[ALERT] Wake word detected! Session activated.")
                speak("Yes, Rakesh?")
                is_awakened = True
                last_activity_time = time.time() 
                time.sleep(0.4) 
            continue
            
        print(f"[ACTIVE MODE] Listening... ({int(SESSION_TIMEOUT - (time.time() - last_activity_time))}s left in session)")
        command = listen_command(seconds=4)
        
        if not command:
            continue
            
        last_activity_time = time.time()
            
        if any(word in command for word in ["exit", "goodbye", "stop", "power down"]):
            speak("Powering down system. Goodbye, Rakesh.")
            break
            
        elif "time" in command:
            current_time_str = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The current time is {current_time_str}.")
            
        elif "date" in command or "today" in command:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            speak(f"Today is {current_date}.")
            
        elif "open notepad" in command:
            speak("Opening Notepad application.")
            subprocess.Popen(["notepad.exe"])
            
        elif "open chrome" in command or "open google" in command:
            speak("Launching Google Chrome browser.")
            def launch_browser():
                webbrowser.open("https://www.google.com")
            threading.Thread(target=launch_browser).start()
               
        elif "play" in command and ("youtube" in command or "song" in command):
            query = command.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
            if query:
                speak(f"Playing {query} on YouTube.")
                threading.Thread(target=lambda: pywhatkit.playonyt(query)).start()
            else:
                speak("What would you like me to play?")
            
        elif "your name" in command:
            speak("My name is Jarvis, your system assistant.")

        elif "my name" in command:
            speak("Your name is Rakesh.")
            
        else:
            print(f"[OUTPUT] Command recognized but unmapped: '{command}'. Routing to AI Brain...")
            ai_response = ask_ai_brain(command)
            speak(ai_response)
            
        time.sleep(1.2)
        
        last_activity_time = time.time()