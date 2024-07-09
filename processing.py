from g4f.client import Client
import requests
import assemblyai as aai
import json
from pydub import AudioSegment
import random 
from moviepy.editor import *
from math import ceil
from os import path, mkdir, system
from shutil import rmtree
import json
from sys import platform
import seewav
import requests
import tempfile
from pathlib import Path
from time import *



f_dat = open('api_keys.json','r').read()
data = eval(f_dat)
assmebly_ai_api = data["AssemblyAI_API"]
urs_api=data["UnrealSpeech_API"]





def v_merger(clip1, clip2):

    #split screen two videos

    final = clips_array([[clip1], [clip2]])
    return final
    


def json_to_srt(json_file_path, srt_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    with open(srt_file_path, 'w') as srt_file:
        index = 1
        for subtitle in data:
            start_time = subtitle['start']
            end_time = subtitle['end'] - 0.003           # -0.003 to ensure that the sutitles dont overlap
            text = subtitle['word']
            if end_time>=180.00 :
                raise ValueError("Clip size of more than a minute not supported!")
            
            
            srt_file.write(f"{index}\n")
            srt_file.write(f"00:00:{start_time:06.3f} --> 00:00:{end_time:06.3f}\n")
            srt_file.write(f"{text}\n\n")
            index += 1


def a_mixer(num):

    #mixes base audio with a background music

    if num==1: au_path = "Minecraft"
    if num==2: au_path = "Subwoofer_Lullaby"
    if num==3: au_path = "Moog_City_2"

    sound1 = AudioSegment.from_file(f"music/{au_path}.mp3", format="mp3")
    sound2 = AudioSegment.from_file("tmp/output.mp3", format="mp3")

    overlay = sound2.overlay(sound1, position=0)
    overlay.export("tmp/F_output.mp3", format="mp3")
    return AudioFileClip("tmp/F_output.mp3")



def backdrop(buzz):

    #subclips the gameplay video according to the playtime of the audio
    
    if buzz==1:
        video_path='backdrop/minecraft.mp4'
    if buzz==2:
        video_path='backdrop/fh5.mp4'        
    if buzz==3:
        video_path='backdrop/gtav.mp4'
    if buzz==4:
        video_path='backdrop/trackmania.mp4'
    

    def vid_dur(file_path):
       TempClip= VideoFileClip(file_path)
       vid_duration=TempClip.duration
       return vid_duration
    

    audio_duration = AudioSegment.from_file('tmp/output.mp3').duration_seconds
    video_duration = vid_dur(video_path)
    
    s_time = random.randint(0,ceil(video_duration-(audio_duration + 5)))
    e_time = s_time+ ceil(audio_duration)
    video= VideoFileClip(video_path).subclip(s_time,e_time)
    return video


def sub_append(font_no, weight=16, color="&H0099ff"):

    if font_no==1 :
        font="Permanant Marker"
    if font_no==2 :
        font="Archivo Black"
    if font_no==3 :
        font="Bebas Neue"
    if font_no==4 :
        font="Jersey 10"
    if font_no==5 :
        font="VT323"

    #adds subtitle
     

    time_tup = localtime() 
    time_string = strftime("%d_%m_%Y__%H%M%S", time_tup)

    system(f"ffmpeg -hide_banner -loglevel error -i tmp/subs.srt tmp/subtitle.ass")   
    ass_file_path = 'tmp/subtitle.ass'
    new_style_definition = f'Style: Default,{font},{weight},{color},&Hffffff,&H0,&H0,1,0,0,0,100,100,0,0,1,1,2,5,50,50,50,1\n'

    with open(ass_file_path, 'r', encoding='utf-8') as file:
         lines = file.readlines()

    for line in lines:
        if line.strip().startswith('Style:'):
            lines[(lines.index(line))]=new_style_definition
    with open('tmp/subtitle.ass', 'w') as file:
        file.write(''.join(lines))
    
    system(f'ffmpeg -hide_banner -loglevel error -i tmp/temporary.mp4 -vf "ass=tmp/subtitle.ass" -c:a copy -c:v libx264 -crf 23 -preset veryfast {time_string}.mp4')
    return time_string


def add_aud(videoclip, audioclip):
    
    #adds audio to the given video

    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    videoclip.write_videofile("tmp/temporary.mp4", codec='libx264', audio_codec='aac')


def subs():

    #generates subtitles using AssemblyAI API 
    #this function is called only when "Timestamp captions" are set to "Sentence"

    aai.settings.api_key = assmebly_ai_api
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe('tmp/output.mp3')
    with open('tmp/subs.srt', 'a+') as handler:
        handler.write(transcript.export_subtitles_srt())


def model(buzz):

    #generates Transcript of the video using g4f gpt 3.5 Turbo model

    client = Client()
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Just answer the given question under 100 words in English, DO NOT include any titles, bullet points, Citations, or any special charecters, just the transcript. Now here is the Prompt :  " + buzz  }],
    )
    gen=response.choices[0].message.content
    return(buzz)


def voice_charecter(chr, trs):

    #generates voice
    if chr==1 : charecter="Dan"
    if chr==2 : charecter="Will"
    if chr==3 : charecter="Scarlett"
    if chr==4 : charecter="Liv"
    if chr==5 : charecter="Amy"

    response = requests.post(
      'https://api.v6.unrealspeech.com/stream',
      headers = {
        'Authorization' : f"Bearer {urs_api}"
      },
      json = {
        'Text': trs, # Up to 1,000 characters
        'VoiceId': charecter, # Scarlett, Dan, Liv, Will, Amy
        'Bitrate': '192k', # 320k, 256k, 192k, ...
        'Speed': '0', # -1.0 to 1.0
        'Pitch': '1', # 0.5 to 1.5
        'Codec': 'libmp3lame', # libmp3lame or pcm_mulaw
      }
    )

    with open('tmp/output.mp3', 'wb') as f:
        f.write(response.content)


def voice_charecter_speech(chr, trs):

    #generates voice
    if chr==1 : charecter="Dan"
    if chr==2 : charecter="Will"
    if chr==3 : charecter="Scarlett"
    if chr==4 : charecter="Liv"
    if chr==5 : charecter="Amy"


    url = "https://api.v6.unrealspeech.com/speech"
    
    payload = {
        "Text": trs,
        "VoiceId": charecter,
        "Bitrate": "192k",
        "Speed": "0",
        "Pitch": "1",
        "TimestampType": "word"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {urs_api}"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    sleep(5)
    
    res = json.loads(response.text)
    voiceover = requests.get(res["OutputUri"])
    with open("tmp/output.mp3", 'wb') as f:
        for i in voiceover :
            f.write(i)

    subs = requests.get(res["TimestampsUri"])
    with open("tmp/subs.json", 'wb') as f:
        for i in subs :
            f.write(i)
    


def clear():
        
    if platform.startswith('win'):
        system("cls")
    else :
        system("clear")

    print('\033[94m'+'''
                                                                      
''')



def process(script, video, voice, font):
    clear()
    if path.exists("tmp") :
          rmtree("tmp")
          mkdir("tmp")
    else :
          mkdir("tmp")


    #Choice-form

    QueryList={}
    QueryList["script"]= script

    QueryList["voices"]= voice
    """\n3. Coose a voice :
3.1 : Dan: Young Male (press 1)
3.2 : Will: Mature Male (press 2)
3.3 : Scarlett: Young Female (press 3)
3.4 : Liv: Young Female (press 4)
3.5 : Amy: Mature Female (press 5)

>>>))
    
    clear()"""

    QueryList["music"] = 1
    """int(input('''\n2. Use Background music?
    2.1 : Minecraft (press 1)
    2.2 : Subwoofer Lullaby (press 2)
    2.3 : Moog City 2 (press 3)

    >>> '''))"""


    QueryList["backdrop"]= video
    """int(input('''4. Choose a background gameplay :
4.1 : Minecraft (press 1)
4.2 : Forza Horizon 5 (press 2)
4.3 : GTAV (press 3)
4.4 : trackmania (press 4)


>>> ''')))
    
    clear()"""


    QueryList["SubType"]= 1
    """int(input('''\n6. Subtitles or Timestamps type :
6.1 : Word (press 1)
6.2 : Sentence (press 2)

>>> '''))"""
    

    QueryList["Font"] = 1
    """int(input('''\n7. Choose a Font :
7.1 : Permanant Marker (press 1)
7.2 : Archivo Black (press 2)
7.3 : Bebas Neue (press 3)
7.4 : Jersey 10 (press 4)
7.5 : VT323 (press 5)

>>> '''))

    clear()"""

    #main-code
    script = model(QueryList['script'])
    print(script)
    print('\n'+'[*] Script Generated\n')


    if QueryList["SubType"]==1 :
        voice_charecter_speech(QueryList['voices'], script)
        print('\n'+'[*] Voice Generated\n')
        json_to_srt('tmp/subs.json', 'tmp/subs.srt' )

    else : 
        voice_charecter(QueryList['voices'], script)
        print('\n'+'[*] Voice Generated\n')
        subs()
    
    bckdrp = backdrop(QueryList["backdrop"])
    print('\n'+'[*] Background Video Generated\n')

    a_mixed = a_mixer(QueryList['music'])

    print('\n'+'[*] Mixing Audio\n')
    add_aud(bckdrp, a_mixed)


    print('\n'+'[*] Burning Captions\n')
    file =sub_append(QueryList["Font"])
    
    #--
    
    print("\n[*] Job Finished")
    return file




    
