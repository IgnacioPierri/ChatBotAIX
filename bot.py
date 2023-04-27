import openai_secret_manager
import telepot
import openai
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = telepot.Bot(TELEGRAM_TOKEN)

# Configurar caché
cache = {}
CACHE_TIME = timedelta(minutes=5) # Tiempo de vida de la caché

def send_message(chat_id, message):
    bot.sendMessage(chat_id=chat_id, text=message)

def get_response(message):
    if message in cache and datetime.now() - cache[message]['timestamp'] < CACHE_TIME:
        return cache[message]['response']
    else:
        try:
            openai.api_key = openai_secret_manager.get_secret("openai")["api_key"]
        except Exception as e:
            print(f"Error al obtener la clave de API de OpenAI: {e}")
            return None
        
        completions = openai.Completion.create(engine="text-davinci-002", prompt=message, max_tokens=100)
        response = completions.choices[0].text
        
        cache[message] = {
            'response': response,
            'timestamp': datetime.now()
        }
        
        return response

def run(msg):
    chat_id = msg['chat']['id']
    message = msg['text']
    
    response = get_response(message)
    
    if response:
        send_message(chat_id, response)
    else:
        send_message(chat_id, "Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, intenta nuevamente más tarde.")

bot.message_loop(run)

print("Listening...")

while True:
    pass
