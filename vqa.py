import os
import cv2
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForQuestionAnswering
import speech_recognition as sr
import pyttsx3

def capture_and_save_image(filename="webcam_capture.jpg"):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error opening webcam!")
        return

    print("Press 'q' to capture image.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame!")
            break

        cv2.imshow("Webcam", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to capture
            cv2.imwrite(filename, frame)
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Image captured and saved as {filename}")

def analyze_image(image_path, question):
    processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
    model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")

    image = Image.open(image_path).convert('RGB')
    inputs = processor(image, question, return_tensors="pt")
    out = model.generate(**inputs)
    answer = processor.decode(out[0], skip_special_tokens=True)
    return answer

def speech_to_text(timeout=5, phrase_time_limit=10):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduced duration for quicker calibration
        print("Listening for your question...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
            return None

    try:
        question = recognizer.recognize_google(audio)
        print(f"You asked: {question}")
        return question
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        print("Could not request results; check your network connection.")
        return None

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    filename = "webcam_capture.jpg"
    capture_and_save_image(filename)

    while True:
        print("Please ask a question about the image (or say 'exit' to quit):")
        question = speech_to_text()
        if question is None:
            continue
        if question.lower() == 'exit':
            break
        answer = analyze_image(filename, question)
        print(f"Answer: {answer}")
        text_to_speech(f"The answer is: {answer}")

if __name__ == "__main__":
    # Disable GPU usage and oneDNN optimizations
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

    main()
