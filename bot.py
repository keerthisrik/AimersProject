import logging
import requests
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure the Google Generative AI model
genai.configure(api_key='AIzaSyC4VD7VA7gGt9jYUBs8GN1r2qRoW7vNHao')

# Function to get weather information for a specific location (using OpenWeatherMap API)
def get_weather(city):
    api_key = '8d9e0918b17270bd2dbdef6c255be66d'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url).json()
    if 'main' in response:
        temp = response['main']['temp']
        description = response['weather'][0]['description']
        return f"The current weather in {city} is {description} with a temperature of {temp:.1f}°C."
    else:
        return "Sorry, I couldn't retrieve weather information for that location."

# Function to extract the city name from user input
def extract_city_name(user_input):
    words = user_input.lower().split()
    for i, word in enumerate(words):
        if word == "weather" and i + 2 < len(words) and words[i + 1] == "in":
            return words[i + 2].capitalize()  # Extract the next word after "in" as the city name
    return None  # Return None if city extraction fails

# Function to get a response from Google Generative AI using Gemini API
def get_google_response(prompt):
    try:
        model = genai.GenerativeModel(model_name="gemini-1.0-pro-latest")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred while getting response from Google Generative AI: {e}")
        return "I'm sorry, I can't process that right now."

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello! How can I help you?')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    if "weather" in user_input.lower():
        city = extract_city_name(user_input)
        if city:
            weather_response = get_weather(city)
            await update.message.reply_text(weather_response)
        else:
            await update.message.reply_text("Could not determine the city.")
    else:
        response = get_google_response(user_input)
        await update.message.reply_text(response)

def main() -> None:
    # Set up the application
    application = Application.builder().token("7346671613:AAHOxlkz5nRbGUBtle5pDqaa6ZhEnjfNMrY").build()

    # Set up logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
