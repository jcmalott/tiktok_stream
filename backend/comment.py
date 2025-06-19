"""
StreamComment class for handling TikTok live stream comments.
Processes user comments and triggers appropriate actions.
"""
import os
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from helper import play_blerp_sound, play_comment

# Initialize environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("StreamComment")


class StreamComment:
    """Handles the processing and actions for TikTok live stream comments."""
    
    # Class constants
    BASE_URL = "https://tiktok-tts.weilnet.workers.dev/api/generation"
    BLERP_COMMANDS = [
        '/ kidsgame',
        '/ cacaw', 
        '/ lul', 
        '/ ptsd'
    ]
    OWNER_COMMANDS = {
        "gametitle": "/ gametitle"
    }
    SPECIAL_COMMANDS = {
        "/ headshot": "commentEvent"
    }
    
    # Voice configurations
    VOICE_CONFIG = {
        "default": "en_us_ghostface",
        "subscriber": "en_us_rocket",
        # User-specific voice mappings
        "vip_voices": {
            7296220538731496478: "en_us_c3po",
            6716965974274475014: 'en_male_ghosthost'
        },
        "sub_voices": [6716965974274475014, 6909864371456672774, 6819812636462695430, 7081731916503843883, 6589377502404345862]
        # "mod_voices": [7296220538731496478, 7371975398752076842, 6975464603825243142, 6716965974274475014, 6909864371456672774, 7101303622760629291]
    }
    
    def __init__(self, socket):
        """Initialize StreamComment instance with default values."""
        self.game_name = ""
        self.user = None
        self.comment = ""
        self.socket = socket
    
    def handle_on_comment(self, user: str, comment: str, is_sound_playing: bool) -> bool:
        """
        Process the current comment and trigger appropriate actions.
        
        Args:
            is_sound_playing: Whether sound is currently playing
            
        Returns:
            bool: True if a sound was played, False otherwise
        """
        self.user = user
        self.comment = comment
        # Check if the user is the stream owner
        is_owner = os.getenv('OWNER_ID') == str(self.user.id)
        
        # Handle owner commands separately
        # if self.user.id in self.VOICE_CONFIG["mod_voices"]:
        #     self.check_owner_commands()
        # else:
            # Apply validation rules for non-owner comments
        is_follower = self.user.follow_info.follow_status > 0
        
        # Skip if sound is playing, comment is too long, or content is not approved
        if (is_sound_playing or 
            len(self.comment) > 80 or 
            not self._approve_comment()):
            return False
        
        # Get the appropriate voice for the user
        voice = self._get_voice()
        
        # Handle special commands or regular comments
        try:
            if self.comment.startswith("/"):
                self._play_blerp()
                return True
            else:
                play_comment(self.BASE_URL, self.comment, voice)
                return True
        except Exception as e:
            logger.error(f"Error playing comment: {e}")
            return False
    
    def play_game_name(self) -> None:
        """Announce the current game name using text-to-speech."""
        try:
            message = f"Game Name is {self.game_name}" if self.game_name else "Game name has not been set"
            play_comment(self.BASE_URL, message)
        except Exception as e:
            logger.error(f"Error playing game name: {e}")
    
    def check_owner_commands(self, comment) -> None:
        """
        Process commands from the stream owner.
        
        Returns:
            bool: True if a command was processed, False otherwise
        """   
        # Handle other owner commands
        for key, command in self.OWNER_COMMANDS.items():  
            if comment.startswith(command):
                match key:
                    case 'gametitle':
                        self.game_name = comment.replace(self.OWNER_COMMANDS["gametitle"], "").strip()
                        return None
                    # case 'follow':
                    #     try:
                    #         logger.info(f"Owner command triggered: {key}")
                    #         self.socket.emit('followEvent')
                    #         return None
                    #     except Exception as e:
                    #         logger.error(f"Failed to emit {command}: {e}")
                    case _:
                        return None
        
        return None
    
    def _get_voice(self) -> str:
        """
        Determine the appropriate voice based on user status.
        
        Returns:
            str: The voice ID to use for this user
        """
        # Check for user-specific voice configuration
        if self.user.id in self.VOICE_CONFIG["vip_voices"]:
            return self.VOICE_CONFIG["vip_voices"][self.user.id]
        
        # Check for subscriber status
        # if self.user.subscribe_info.is_subscribe:
        #     return self.VOICE_CONFIG["subscriber"]
        
        if self.user.id in self.VOICE_CONFIG["sub_voices"]:
            return self.VOICE_CONFIG["subscriber"]
        
        # Return default voice
        return self.VOICE_CONFIG["default"]
    
    def _play_blerp(self) -> None:
        """
        Process blerp commands and special commands.
        
        Returns:
            bool: True if a sound was played, False otherwise
        """
        # Tells Frontend that a special command is being fired
        for cmd, event in self.SPECIAL_COMMANDS.items():
            if self.comment == cmd:
                try:
                    logger.info(f"Special command triggered: {cmd}")
                    # TODO: They will all be comments with different package sent
                    # self.socket.emit(commentEvent, "comment")
                    self.socket.emit(event)
                    return None
                except Exception as e:
                    logger.error(f"Failed to emit {event}: {e}")
        
        # Check for blerp sounds
        if self.comment in self.BLERP_COMMANDS:
            try:
                sound_name = self.comment[2:]  # Remove "/ " prefix
                # logger.info(f"Playing blerp sound: {sound_name}")
                play_blerp_sound(sound_name)
                return None
            except Exception as e:
                logger.error(f"Failed to play blerp sound: {e}")
        
        return None
    
    def _approve_comment(self) -> bool:
        """
        Check if a comment is approved for TTS.
        
        Returns:
            bool: True if the comment is approved, False otherwise
        """
        # Filter out mentions and links
        if (self.comment.startswith("@") or 
            self.comment.startswith("http")):
            return False
        
        # Add more filters here as needed
        
        return True