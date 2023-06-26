
from datetime import datetime
import string
import random

def get_greeting():
    current_time = datetime.now()
    if current_time.hour < 12:
        return 'Good morning'
    elif 12 <= current_time.hour < 18:
        return 'Good afternoon'
    else:
        return 'Good evening'


def generate_demo_url(length=6):
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(length))
    return short_url

