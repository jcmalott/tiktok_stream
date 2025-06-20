# MAIN: https://github.com/zerodytrash/TikTok-Live-Connector
# PYTHON: https://github.com/isaackogan/TikTokLive/tree/master
# - WEBSOCKET: ws://127.0.0.1:3005/ws?unique_id=tv_asahi_news&client_id=[your-random-id]
# - CHECK RATE LIMIT: https://tiktok.eulerstream.com/webcast/rate_limits?apiKey=N2E0MzcwMzMxZjliY2EwNzlkNmQyMjMzMWFiNzM4OTk0YTkwN2M0ZDFkZjc0ZmI0OTVjMjEy
# TODO: https://github.com/Camb-ai/MARS5-TTS
import asyncio
import os
import threading
from typing import Dict, List, Any, Optional

import json

import nest_asyncio
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import argparse

from TikTokLive import TikTokLiveClient
from TikTokLive.client.web.web_settings import WebDefaults
from TikTokLive.events import (
    ConnectEvent, CommentEvent, DisconnectEvent, JoinEvent,
    GiftEvent, FollowEvent, SubscribeEvent
)

from helper import play_walk_on, play_gift_sound, check_game_name
from comment import StreamComment
from database import save_to_file

# Setup environment
load_dotenv()
nest_asyncio.apply()  # Allow asyncio within synchronous contexts

# TODO: Events that use the same timer, like game name
# - gifters get rocket voice over a certain amount, based on a month like a sub

# Configuration
TIKTOK_USERNAME = "@identityunk"
IS_TESTING = False
# TIKTOK_USERNAME = "@yoyo_savagemike"
# IS_TESTING = True
SOCKET_CORS_ORIGINS = ["http://localhost:3000", "http://localhost.com:3000"]
SOUND_COOLDOWN = 15.0
GIFT_COOLDOWN = 5.0
TITLE_COOLDOWN = 3.0

# Configure TikTok API
WebDefaults.tiktok_sign_api_key = "N2E0MzcwMzMxZjliY2EwNzlkNmQyMjMzMWFiNzM4OTk0YTkwN2M0ZDFkZjc0ZmI0OTVjMjEy"


class TikTokLiveHandler:
    """Manages TikTok live stream integration and events."""
    
    def __init__(self, unique_id: str, session_id: str, socketio: SocketIO, game_title: str=None):
        self.client = TikTokLiveClient(unique_id=unique_id)
        self.session_id = session_id
        self.socketio = socketio
        self.stream_comment = StreamComment(socketio)
        
        # State tracking
        self.chatters: Dict[int, Dict[str, Any]] = {}
        self.followers: List[str] = []
        self.gifters: Dict[int, Dict[str, Any]] = {}
        self.subs: List[str] = []
        self.vips: Dict[int, str] = {}
        self.blerp_users: List[int] = [7296220538731496478, 7371975398752076842]
        
        # Sound queue management
        self.sound_queue: List[str] = []
        self.is_sound_playing: bool = False
        self.is_gifting_playing: bool = False
        self.is_title_playing: bool = False
        self.connected: bool = False
        
        self.game_title = game_title
        
        # Set up event handlers
        self._register_event_handlers()
        self.mods = [7296220538731496478, 7371975398752076842, 6975464603825243142, 6716965974274475014, 6909864371456672774, 7101303622760629291]
    
    def _register_event_handlers(self) -> None:
        """Register all event handlers for TikTok Live events."""
        self.client.on(ConnectEvent)(self.on_connect)
        self.client.on(DisconnectEvent)(self.on_disconnect)
        self.client.on(JoinEvent)(self.on_join)
        self.client.on(CommentEvent)(self.on_comment)
        self.client.on(FollowEvent)(self.on_follow)
        self.client.on(GiftEvent)(self.on_gift)
        self.client.on(SubscribeEvent)(self.on_subscribe)
    
    async def connect(self) -> None:
        """Connect to TikTok Live."""
        if not self.connected:
            try:
                # self.client.web.set_session_id(self.session_id)
                await self.client.connect()
                self.connected = True
            except Exception as e:
                print(f"Failed to connect to TikTok Live: {e}")
        else:
            print("Already connected to TikTok Live")
    
    async def on_connect(self, event: ConnectEvent) -> None:
        # if game title was set
        if self.game_title:
            print(f"Game Title: {self.game_title}")
            self.stream_comment.check_owner_commands(f"/ gametitle {self.game_title}")
        """Handle connection to TikTok Live."""
        print(f"Connected to @{event.unique_id} (Room ID: {self.client.room_id})")
    
    async def on_disconnect(self, event: DisconnectEvent) -> None:
        """Handle disconnection from TikTok Live."""
        print("Stream has ended!")
        self.connected = False
    
    async def on_join(self, event: JoinEvent) -> None:
        """Handle user join event."""
        user_id = event.user.id
        if user_id in self.blerp_users:
            play_walk_on(user_id)
            self.blerp_users.remove(user_id)
    
    async def on_comment(self, event: CommentEvent) -> None:
        """Handle comment event."""
        user = event.user
        comment = event.comment.strip().lower()
        
        if user.subscribe_info.is_subscribed:
            print(f"SUB: {user}")
        
        # print(f"{check_game_name(comment)}")
        if check_game_name(comment):
            if not self.is_title_playing:
                self.is_title_playing = True
                self.stream_comment.play_game_name()
                timer = threading.Timer(TITLE_COOLDOWN, self._title_timer_callback)
                timer.daemon = True
                timer.start()
        else:
            # Handle regular comments
            is_owner = os.getenv('OWNER_ID') == str(user.id)
            if user.id in self.mods:
                self.stream_comment.check_owner_commands(comment)
            # if is_owner or not self.is_sound_playing:
            if not self.is_sound_playing:
                self.is_sound_playing = self.stream_comment.handle_on_comment(user, comment, self.is_sound_playing)
                if self.is_sound_playing:
                    self._schedule_sound_timer()
            
            # Track user status
            if user.follow_info.follow_status > 0:
                self.vips[user.id] = user.nickname
            
            self.chatters[user.id] = {"name": user.nickname, "visits": 1}
    
    async def on_follow(self, event: FollowEvent) -> None:
        """Handle follow event."""
        user_name = event.user.nickname
        if user_name not in self.followers:
            self.followers.append(user_name)
        
        
        if not self.is_sound_playing:
            self.is_sound_playing = True
            try:
                self.socketio.emit('followEvent')
            except Exception as e:
                print(f"Failed to emit Follow: {e}")
            
            self._schedule_sound_timer()
        else:
            self.sound_queue.append('followEvent')
    
    async def on_gift(self, event: GiftEvent) -> None:
        """Handle gift event."""
        user = event.user
        if user.id in self.gifters:
            self.gifters[user.id]['diamonds'] += event.gift.diamond_count
        else:
            self.gifters[user.id] = {
                'name': user.nickname, 
                'diamonds': event.gift.diamond_count
            }
        
        if not self.is_gifting_playing:
            self.is_gifting_playing = True
            play_gift_sound()
            timer = threading.Timer(GIFT_COOLDOWN, self._gift_timer_callback)
            timer.daemon = True
            timer.start()
    
    async def on_subscribe(self, event: SubscribeEvent) -> None:
        """Handle subscribe event."""
        user_name = event.user.nickname
        if user_name not in self.subs:
            self.subs.append(user_name)
        
        print(f"Subscribe: {user_name}")
        self.socketio.emit('subscribeEvent')
    
    def _sound_timer_callback(self) -> None:
        """Process the next sound in the queue."""
        if self.sound_queue:
            try:
                self.socketio.emit(self.sound_queue.pop(0))
                # Schedule next sound if queue is not empty
                if self.sound_queue:
                    self._schedule_sound_timer()
                else:
                    self.is_sound_playing = False
            except Exception as e:
                print(f"Failed to emit sound event: {e}")
                self.is_sound_playing = False
        else:
            self.is_sound_playing = False
    
    def _gift_timer_callback(self) -> None:
        """Reset gift playing status."""
        self.is_gifting_playing = False
        
    def _title_timer_callback(self) -> None:
        """Reset gift playing status."""
        self.is_title_playing = False
    
    def _schedule_sound_timer(self) -> None:
        """Schedule the sound timer."""
        timer = threading.Timer(SOUND_COOLDOWN, self._sound_timer_callback)
        timer.daemon = True
        timer.start()
    
    def save_data(self) -> None:
        """Save all tracked data to files."""
        if not IS_TESTING:
            save_to_file(self.chatters, 'database/users.json', "visits")
            save_to_file(self.gifters, 'database/gifts.json', 'diamonds')
        
        print("----- CHATTERS -----")
        for _, data in self.chatters.items():
            print(f"{data['name']}")
            
        print("----- FOLLOWERS -----")
        for follower in self.followers:
            print(follower)
            
        print("----- VIPS -----")
        for _, username in self.vips.items():
            print(username)
            
        print("----- SUBS -----")
        for sub in self.subs:
            print(sub)
            
        print("----- GIFTERS -----")
        # for _, data in self.gifters.items():
        #     print(f"{data['name']}")
            
        print(json.dumps(self.gifters, indent=2, ensure_ascii=False))


def create_app() -> tuple:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure CORS
    cors_config = {
        "origins": SOCKET_CORS_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "supports_credentials": True,
        "max_age": 3600
    }
    CORS(app, resources={r"/*": cors_config})
    
    # Configure SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    return app, socketio


def main():
    parser = argparse.ArgumentParser(description="Tiktok Chat Bot")
    parser.add_argument('-t', '--title', type=str, help='Title of Game' )
    args = parser.parse_args()
    
    """Main entry point for the application."""
    app, socketio = create_app()
    
    # Initialize TikTok Live handler
    tiktok_handler = TikTokLiveHandler(
        unique_id=TIKTOK_USERNAME,
        session_id="3440df240c237b317e8e73a37c8b235c",
        socketio=socketio,
        game_title=args.title
    )
    
    # Register SocketIO event handlers
    @socketio.on('connect')
    def handle_connect():
        print("Socket Connected!")
        socketio.emit('connectEvent')
        asyncio.run(tiktok_handler.connect())
    
    @socketio.on('message')
    def handle_message(message):
        print(f"Client: {message}")
    
    # Start the application
    try:
        socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
    finally:
        # Save data when application exits only when their is data to save
        if tiktok_handler.chatters:
            tiktok_handler.save_data()


if __name__ == '__main__':
    main()