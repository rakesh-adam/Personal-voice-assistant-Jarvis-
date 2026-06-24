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
import psutil
CONTACTS = {
    "my phone": "+9",
    "friend": "+",   
    "bro": "+91XXXXXXXXXX"
}

try:
    client = genai.Client(api_key="_api_key_here")
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
                system_instruction="You are Jarvis, a concise AI assistant." \
                " IMPORTANT: Answer in exactly 2-3 short, punchy sentences maximum." \
                " Be factual and complete within those sentences. End with a period.",
                max_output_tokens=600,
                temperature=0.3
            )
        )
        
        raw_text = ""
        
        if not response.candidates or len(response.candidates) == 0:
            print("[ERROR] No candidates in Gemini response")
            return "I encountered an issue retrieving a response from my neural network."
        
        candidate = response.candidates[0]
        
        finish_reason = candidate.finish_reason if hasattr(candidate, 'finish_reason') else None
        if finish_reason == "MAX_TOKENS":
            print("[WARNING] Response truncated due to token limit - increasing tokens may help")
        
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text:
                    raw_text += part.text
        
        raw_text = raw_text.strip()
        
        if not raw_text:
            print("[ERROR] No text extracted from Gemini response")
            return "I encountered an issue processing my response."
        
        clean_text = raw_text.replace("**", "").replace("*", "").replace("`", "").replace("_", "")
        return clean_text
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

        elif "cpu" in command or "processor" in command:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            speak(f"Current core load is at {cpu_usage} percent, Rakesh.")
            
        elif "battery" in command or "power status" in command:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                is_plugged = "plugged in and charging" if battery.power_plugged else "running on battery power"
                speak(f"The system is at {percent} percent capacity and currently {is_plugged}.")
            else:
                speak("I am unable to detect a hardware battery array on this machine.")
                
        elif "network" in command or "internet speed" in command:
            speak("Running quick network diagnostic check.")
            try:
                import socket
                start_time = time.time()
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                latency = round((time.time() - start_time) * 1000, 1)
                speak(f"Network status: Operational. Ping latency is {latency} milliseconds.")
            except Exception:
                speak("Network status: Offline or experiencing high packet drops.")

        elif "whatsapp" in command or "send a message" in command:
            speak("Who do you want to message, Rakesh?")
            recipient = listen_command(seconds=4)
            
            if recipient in CONTACTS:
                phone_number = CONTACTS[recipient]
                speak(f"Found {recipient}. What is the message?")
                message_text = listen_command(seconds=6) 
                
                if message_text:
                    speak(f"Sending message to {recipient} now.")
                    
                    def send_whatsapp():
                        pywhatkit.sendwhatmsg_instantly(
                            phone_no=phone_number,
                            message=message_text,
                            wait_time=15, 
                            tab_close=True, 
                            close_time=3
                        )
                    
                    threading.Thread(target=send_whatsapp).start()
                else:
                    speak("Message was empty. Outbound sequence aborted.")
            else:
                speak(f"I couldn't find {recipient} in your contact database.")

        else:
            print(f"[OUTPUT] Command recognized but unmapped: '{command}'. Routing to AI Brain...")
            ai_response = ask_ai_brain(command)
            speak(ai_response)
            cooldown_duration = max(1.5, min(1.0, len(ai_response) / 30))
            print(f"[SYSTEM] Keeping microphone closed for {round(cooldown_duration, 1)}s until speech finishes...")
            time.sleep(cooldown_duration)
            
        time.sleep(0.4) 
        last_activity_time = time.time()