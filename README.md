# BrainRot GPT
Dieses Projekt entstand beim SelectCode Mini-Hackathon

```bash
# Clone the repo
git clone https://github.com/Fangoling/BrainRotGPT
```

Als nächstes, trag den OpenAI API Key in `.env` ein.

Melde dich bei AssemblyAI und UnrealSpeech an und erstelle accounts.
```bash
# Navigate into the repo
cd ./BrainRotGPT

# Create a virtual environment
python3 -m venv env

# Activate the virtual environment
# For Windows
env\Scripts\activate

# For Unix or MacOS
source env/bin/activate

# Install prerequisites
# For Windows
winget install ffmpeg

# For Unix or Mac OS
sudo apt-get install -y python3-dev libasound2-dev ffmpeg
pip install -r requirements.txt
mkdir ~/.local/share/fonts 
cp fonts/* ~/.local/share/fonts/ && fc-cache -f -v


# Launch chainlit
chainlit run app.py -w
```
