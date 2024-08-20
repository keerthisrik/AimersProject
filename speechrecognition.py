import pyttsx3
import os
import google.generativeai as genai
import speech_recognition as sr
import time

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Configure Google Generative AI
genai.configure(api_key="AIzaSyBPvaV1ZPKajfoC9ez3ALyn8E9IuuSwrs0")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=safety_settings,
    generation_config=generation_config,
)

chat_session = model.start_chat(
    history=[
        {"role": "user", "parts": ["hello\n"]},
        {"role": "model", "parts": ["Hello! How can I help you today? \n"]},
    ]
)

def main():
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Use the microphone as the source for input
    with sr.Microphone() as source:
        print("Adjusting for ambient noise. Please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=5)
        print("Listening...")

        # Listen for the first phrase and extract it into audio data
        audio_data = recognizer.listen(source)

        try:
            # Recognize speech using Google Web Speech API
            print("Recognizing...")
            text = recognizer.recognize_google(audio_data)
            print(f"Text: {text}")

            # Retry logic for the Google Generative AI request
            retries = 3
            for attempt in range(retries):
                try:
                    response = chat_session.send_message(f"Limit 100 words \n{text}")
                    print(response.text)
                    engine.say(response.text)
                    engine.runAndWait()
                    break  # Exit the retry loop if successful
                except google.api_core.exceptions.InternalServerError as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        print("Max retries reached. Exiting.")
                        raise

        except sr.UnknownValueError:
            print("Google Web Speech API could not understand the audio")
        except sr.RequestError:
            print("Could not request results from Google Web Speech API")

if __name__ == "__main__":
    main()
