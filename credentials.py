import os
from dotenv import load_dotenv

load_dotenv()

def load_credentials():
    """ This function is responsible for extracting user data to be used for the intranet
    """
    credentials = []

    for key, value in os.environ.items():
        if key.startswith('TELEGRAM_CHAT_ID'):
            user_id = value

            if user_id:
                credentials.append({'chat_id': int(user_id)})
    print(credentials)
    
load_credentials()