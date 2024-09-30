import gc
import hashlib
import os
import shlex
import subprocess
import librosa
import torch
import numpy as np
import soundfile as sf
import gradio as gr
from rvc import Config, load_hubert, get_vc, rvc_infer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RVC_MODELS_DIR = os.path.join(BASE_DIR, 'rvc_models')
OUTPUT_DIR = os.path.join(BASE_DIR, 'song_output')

def get_rvc_model(voice_model):
    print(f'Loading RVC model for: {voice_model}')
    model_dir = os.path.join(RVC_MODELS_DIR, voice_model)
    rvc_model_path = next((os.path.join(model_dir, f) for f in os.listdir(model_dir) if f.endswith('.pth')), None)
    rvc_index_path = next((os.path.join(model_dir, f) for f in os.listdir(model_dir) if f.endswith('.index')), None)

    if rvc_model_path is None:
        raise FileNotFoundError(f'There is no model file in the {model_dir} directory.')

    return rvc_model_path, rvc_index_path

def convert_to_stereo(audio_path):
    print(f'Converting {audio_path} to stereo if needed...')
    wave, sr = librosa.load(audio_path, mono=False, sr=44100)
    if type(wave[0]) != np.ndarray:
        stereo_path = 'Voice_stereo.wav'
        command = shlex.split(f'ffmpeg -y -loglevel error -i "{audio_path}" -ac 2 -f wav "{stereo_path}"')
        subprocess.run(command)
        print(f'Converted to stereo: {stereo_path}')
        return stereo_path
    print('Audio already in stereo.')
    return audio_path

def get_hash(filepath):
    print(f'Generating hash for file: {filepath}')
    file_hash = hashlib.blake2b()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()[:11]

def display_progress(percent, message, progress=gr.Progress()):
    progress(percent, desc=message)
    print(f'{message} - {percent*100}% complete')

def voice_change(voice_model, vocals_path, output_path, pitch_change, f0_method, index_rate, filter_radius, rms_mix_rate, protect, crepe_hop_length, f0_min, f0_max):
    print(f'Starting voice conversion for {vocals_path} with {voice_model} model.')
    rvc_model_path, rvc_index_path = get_rvc_model(voice_model)

    if torch.cuda.is_available():
        device = 'cuda:0'
    else:
        device = 'cpu'

    print(f'Using device: {device}')
    config = Config(device, True)
    hubert_model = load_hubert(device, config.is_half, os.path.join(RVC_MODELS_DIR, 'hubert_base.pt'))
    cpt, version, net_g, tgt_sr, vc = get_vc(device, config.is_half, config, rvc_model_path)

    rvc_infer(rvc_index_path, index_rate, vocals_path, output_path, pitch_change, f0_method, cpt, version, net_g,
              filter_radius, tgt_sr, rms_mix_rate, protect, crepe_hop_length, vc, hubert_model, f0_min, f0_max)
    
    del hubert_model, cpt, net_g, vc
    gc.collect()
    torch.cuda.empty_cache()
    print(f'Voice conversion complete. Output saved to {output_path}')

def pipeline_inference(uploaded_file, voice_model, pitch_change, index_rate=0.5, filter_radius=3, rms_mix_rate=0.25, f0_method='rmvpe',
                        crepe_hop_length=128, protect=0.33, output_format='mp3', progress=gr.Progress(), f0_min=50, f0_max=1100):

    print('Starting song cover pipeline...')
    if not uploaded_file or not voice_model:
        raise ValueError('Make sure that the song input field and voice model field are filled in.')

    display_progress(0, '[~] Starting the AI cover generation pipeline...', progress)

    if not os.path.exists(uploaded_file):
        raise FileNotFoundError(f'{uploaded_file} does not exist.')

    song_id = get_hash(uploaded_file)
    song_dir = os.path.join(OUTPUT_DIR, song_id)
    os.makedirs(song_dir, exist_ok=True)

    orig_song_path = convert_to_stereo(uploaded_file)
    ai_cover_path = os.path.join(song_dir, f'Converted_Voice.{output_format}')

    if os.path.exists(ai_cover_path):
        os.remove(ai_cover_path)

    display_progress(0.5, '[~] Converting vocals...', progress)
    voice_change(voice_model, orig_song_path, ai_cover_path, pitch_change, f0_method, index_rate,
                 filter_radius, rms_mix_rate, protect, crepe_hop_length, f0_min, f0_max)

    print(f'AI cover generation complete. File saved at {ai_cover_path}')
    return ai_cover_path
