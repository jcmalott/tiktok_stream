# Tiktok Overlay

Adds an overlay to a tiktok live stream to increase chatter interaction.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)

## Features

- Displays random Gifs with sound when a user follows or subs
- Sets a default tts voice for all users, that plays randomly with a 15 second cooldown (applies to all)
  - Sets a tts voice for subs only
  - Sets individual tts voice
- Allows for chat commands to fire off events
- Play sounds for certain events like donations

## Installation

Clone repo. <br>
Open a terminal to the file location you want to install the project.
```bash
git clone https://github.com/jcmalott/tiktok_stream.git
cd tiktok_stream
npm install
```

## Usage

Steps for running server and client side application.

Starting from root folder.<br>
```bash
cd backend
py flasktest.py
```
Note: To change tiktok livestream user, within flasktest.py<br>
Change username to your account username.
![Username](images/tiktok_user.jpg)
![Profile](images/Profile.jpg)

Starting from root folder.<br>
```bash
cd frontend
npm start
```


