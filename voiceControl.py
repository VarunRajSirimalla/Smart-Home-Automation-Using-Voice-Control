import pyttsx3 # Text-to-speech
import speech_recognition as sr # Speech recognition
import datetime
import RPi.GPIO as gpio
import os
# Initialize the speech engine
engine = pyttsx3.init()

PINS = {
    "buzzer": 4,
    "light": 3,
    "fan": 2
}
WAKE_WORD = "jarvis"
# Wake word
def setup_board():
    """Setup the GPIO pins for the Raspberry Pi."""
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    for pin in PINS.values():
        gpio.setup(pin, gpio.OUT)
        gpio.output(pin, gpio.LOW)
def speak(text):
    """Convert text into speech."""
    engine.say(text)
    engine.runAndWait()
def greet_user():
    """Greet the user based on the current time (morning, afternoon, or evening)."""
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        greeting = "Good morning Master!"
    elif 12 <= hour < 18:
        greeting = "Good afternoon Master!"
    else:
        greeting = "Good evening Master!"
    speak(greeting)
    speak("Hello, I am Jarvis. How can I help you today?")
    print("Hello, I am Jarvis. How can I help you today?")
def listen_for_wake_word():
    """Continuously listen for the wake word."""
    count = 1
    recognizer = sr.Recognizer()
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word...")
                recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
                audio = recognizer.listen(source)  # Capture the audio
            # Recognize speech
            text = recognizer.recognize_google(audio).lower()
            print(f"Heard: {text}")
            # Check if the wake word is detected
            if WAKE_WORD in text:
                speak("Yes, Master?")
                print("Wake word detected. Listening for command...")
                return True
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError:
            print("Could not request results. Check your internet connection.")
        except Exception as e:
            print(f"An error occurred: {e}")
def take_command():
    """Fetch the user's voice command and return it as text."""
    recognizer = sr.Recognizer()
    command = ""  # Default value to avoid UnboundLocalError
    try:
        with sr.Microphone() as source:
            print("Listening to Master...")
            recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
            audio = recognizer.listen(source)  # Capture the audio from the user
        command = recognizer.recognize_google(audio)  # Convert speech to text
        command = command.lower()  # Convert to lowercase
        print(f"You said: {command}")
    except sr.UnknownValueError:
        print("Sorry, I did not understand.")
        speak("Sorry, I did not understand. Please say it again.")
    except sr.RequestError:
        print("Could not request results. Please check your internet connection.")
        speak("Could not request results. Please check your internet connection.")
    except Exception as e:
        print(f"An error occurred: {e}")
        speak("An error occurred while trying to recognize your speech.")
    return command
def control_device(action, device):
    """Control specified device with feedback."""
    if device not in PINS:
        speak(f"Forgive me, Master, I'm not familiar with a {device}.")
        return
    pin = PINS[device]
    device_name = device.capitalize()
    if action == "on":
        gpio.output(pin, gpio.HIGH)
        speak(f"{device_name} is now activated, Master.")
    elif action == "off":
        gpio.output(pin, gpio.LOW)
        speak(f"{device_name} has been deactivated, Master.")
def process_command(command):
    """Process and execute commands with assistant-like responses."""
    if not command:
        return
    if "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}, Master.")
    elif "hello" in command or "hi" in command:
        speak("Greetings, Master! How may I serve you today?")
    elif "how are you" in command:
        speak("I'm functioning perfectly, Master. Thank you for asking!")
    else:
        # Check for device control commands
        for device in PINS:
            if f"on {device}" in command:
                control_device("on", device)
                return
            elif f"off {device}" in command:
                control_device("off", device)
                return
        speak("I'm not sure I understood that command, Master. Could you please clarify?")
count = 0

def run_awik():
    """Main function to run the Awik-style voice assistant."""
    setup_board()
    greet_user()  # Greet the user
    while True:
        # Listen for the wake word
        if listen_for_wake_word():
            # Take a command after the wake word is detected
            command = take_command()
            if "stop" in command or "exit" in command:
                speak("Farewell, Master. It was an honor serving you.")
                gpio.cleanup()
                return
            process_command(command)

# Run the Awik assistant
if __name__ == "__main__":
    run_awik()