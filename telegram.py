""" This module sends messages to a Telegram chat using the Telegram Bot API.
"""

import requests
import os
import json
import genai
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
telegram_token = os.getenv('TELEGRAM_TOKEN')

# Set base url
base_url = "https://api.telegram.org/bot"
count = 1

user_stats = {}

# Send Quiz to Telegram
def send_quiz(quiz, chat_id):
    """ This function is responsible for sending a quiz to Telegram

    Args:
        quiz (_type_): dict
                        The quiz from the genai module
    """
    
    # Construct quiz
    question = quiz['question']
    options = json.dumps(quiz['options'])
    correct_option_id = quiz['correct_option_id']
    explanation = quiz['explanation']

    parameters = {
    "chat_id" : chat_id,
    "question": f"🤔💻 *Question {count}:* \n\n{question}",
    "options": options,
    "correct_option_id": correct_option_id,
    "explanation": explanation,
    "is_anonymous": False,
    "type" : "quiz"
    }

    # Send quiz to Telegram
    url = f"{base_url}{telegram_token}/sendPoll"

    try:
        response = requests.post(url, data=parameters)
        response.raise_for_status()
        print(f"Quiz sent to Telegram chat {id}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending quiz: {e}")
    return None

def send_message(chat_id, text):
    url = f"{base_url}{telegram_token}/sendMessage"
    params = {'chat_id': chat_id, 'text': text}

    try:
        response = requests.post(url, json=params)
        response.raise_for_status()
        print(f"Message sent to Telegram chat {chat_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
    return None


def process_command(update):
    message = update.get('message')
    if message:
        text = message.get('text')
        chat_id = message['chat']['id']
        user_id = message['from']['id']

        if text == '/start':
            send_message(chat_id, "Hi! I'm a Programming Quiz bot")
        elif text == '/help':
            send_message(chat_id, "Hi! I'm a Programming Quiz bot. \nUse commands: /start, /help, /quiz, /stats to interact with me.")
        elif text == '/quiz':
            quiz = genai.prompt_model()
            send_quiz(quiz, chat_id)
        
            # Update user statistics
            if user_id not in user_stats:
                user_stats[user_id] = {'quizzes_taken': 0, 'correct_answers': 0, 'incorrect_answers': 0}
            user_stats[user_id]['quizzes_taken'] += 1

            # Check if user answered correctly
            for option in update['poll']['options']:
                if option['voter_count'] > 0:
                    user_answer = option['voter_count']
            if quiz['correct_option_id'] == user_answer:
                user_stats[user_id]['correct_answers'] += 1
            else:
                user_stats[user_id]['incorrect_answers'] += 1
        
        elif text == '/stats':
            if user_id in user_stats:
                stats = user_stats[user_id]
                send_message(chat_id, f"You have taken {stats['quizzes_taken']} quizzes.\n"
                                      f"Correct answers: {stats['correct_answers']}\n"
                                      f"Incorrect answers: {stats['incorrect_answers']}")
            else:
                send_message(chat_id, "You haven't taken any quizzes yet.")
        else:
            # Update user statistics
            if user_id not in user_stats:
                user_stats[user_id] = {'quizzes_taken': 0, 'correct_answers': 0, 'incorrect_answers': 0}

            # Send message to Telegram chat
            send_message(chat_id, 'Sorry, I do not understand that command. Please type /help for a list of commands.')


def get_updates(offset=None):
    url = f"{base_url}{telegram_token}/getUpdates"
    params = {'offset': offset}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting updates: {e}")

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates['result']:
            process_command(update)
            offset = update['update_id'] + 1

if __name__ == '__main__':
    main()