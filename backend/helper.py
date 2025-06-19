import re
def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                            #    u"\u2700-\u27BF"
                            #    u"\uE000-\uF8FF"
                            #    u"\uDC00-\uDFFF"
                            #    u"\u2011-\u26FF"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def check_game_name(comment):
    if not comment:
        return False
    
    alter_comment = comment.strip().lower()
    game_name_patterns = [
        'game' in alter_comment and any(word in alter_comment for word in ['what', 'name']),
        'game?' in alter_comment,
        'whats this' in alter_comment
    ]
    
    return(any(game_name_patterns))

import datetime
def get_current_time():
    dt = datetime.datetime.now()
    return dt.strftime("%H:%M:%S")

from playsound import playsound
import os
def play_walk_on(username):
    audio_file = os.path.abspath(f"sounds/walk_ons/{username}.mp3")
    if os.path.exists(audio_file): playsound(audio_file)
    
def play_blerp_sound(blerp):
    print("Playing Blerp!")
    audio_file = os.path.abspath(f"sounds/blerps/{blerp}.mp3")
    if os.path.exists(audio_file): playsound(audio_file)
    
def play_gift_sound():
    audio_file = os.path.abspath(f"sounds/gifts/mario_coin.mp3")
    if os.path.exists(audio_file): playsound(audio_file)

# Voice List
# https://github.com/oscie57/tiktok-voice/wiki/Voice-Codes
import requests, base64, io
from pygame import mixer
def play_comment(baseURL, text, voice="en_us_ghostface"):
    mixer.init()
    text_only = remove_emoji(text) 
    body = {"text": text_only, "voice": voice}
    
    try:
        response = requests.post(baseURL, json=body)
        data = response.json()["data"]
        if data:
            audio64 = base64.b64decode(data)
            audio_file = io.BytesIO(audio64)
            sound = mixer.Sound(audio_file)
            sound.play()
    except:
        print("Voice Fail")