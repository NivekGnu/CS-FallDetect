# 4945 Personal Project
## Requirements
1. Python version `3.12.*` as any newer will not work with mediapipe
2. Ensure you have created a venv for python:
```
# Make sure you're in the folder you want to create the environment for all dependencies

# On Windows
python -m venv .venv
# MacOS or Linux
python3 -m venv .venv
```

## Setup

### Installing frontend dependencies
From the root directory enter into the command line:
```
cd client
npm install
```

### Installing backend dependencies
From the root directory enter into the command line:
```
cd server
pip install -r requirements.txt
```

### Installing model of VOSK
1. Create a new directory names `models` in the root directory
2. Go to https://alphacephei.com/vosk/models 
3. Download the model `vosk-model-small-en-us-0.15`
4. Unzip and place entire folder into `models`