import os, sys
import shutil
import urllib.request
import zipfile
import gdown
import gradio as gr

from main import song_cover_pipeline
from audio_effects import add_audio_effects
from modules.model_management import ignore_files, update_models_list, extract_zip, download_from_url, upload_zip_model, upload_separate_files
from modules.ui_updates import show_hop_slider, update_f0_method, update_button_text, update_button_text_voc, update_button_text_inst, swap_visibility, swap_buttons
from modules.file_processing import process_file_upload

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rvc_models_dir = os.path.join(BASE_DIR, 'rvc_models')
output_dir = os.path.join(BASE_DIR, 'song_output')


print("\n-------------------------------\n HEX RVC V2 \n-------------------------------\n")

if __name__ == '__main__':
    voice_models = ignore_files(rvc_models_dir)


with gr.Blocks(title="HEX RVC 🔊",theme="Hev832/niceandsimple") as app:
    with gr.Row():
        gr.HTML("<center><h1>HEX RVC</h1></center>")
    with gr.Tabs():
        with gr.TabItem("Inference"):
            with gr.Row():
                rvc_model = gr.Dropdown(voice_models, label='Voice Models')
                pitch = gr.Slider(-12, 12, value=0, step=0.5, label='Pitch Adjustment', info='-12 - male voice || 12 - female voice')
            with gr.Row():
                ref_btn = gr.Button('Refresh Models List', variant='primary')           
                generate_btn = gr.Button("Generate", variant='primary', scale=1)
             
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        song_input = gr.Audio(label='Upload Your Audio File', interactive=True, show_download_button=False, show_share_button=False, type="filepath")                          
                    with gr.Row():
                        output_format = gr.Dropdown(['mp3', 'flac', 'wav'], value='mp3', label='File Format', allow_custom_value=False, filterable=False)
                    
                    
                with gr.Column():
                    with gr.Accordion("General Settings", open=False):
                        f0_method = gr.Dropdown(['rmvpe+', 'fcpe', 'rmvpe', 'mangio-crepe', 'crepe', 'hybrid[rmvpe+fcpe]'], value='rmvpe+', label='F0 Method', allow_custom_value=False, filterable=False)
                        crepe_hop_length = gr.Slider(8, 512, value=128, step=8, visible=False, label='Crepe Hop Length')
                        f0_method.change(show_hop_slider, inputs=f0_method, outputs=crepe_hop_length)
                        f0_min = gr.Slider(label="Minimum pitch range", info="Defines the lower limit of the pitch range that the algorithm will use to determine the fundamental frequency (F0) in the audio signal.", step=1, minimum=1, value=50, maximum=120)
                        f0_max = gr.Slider(label="Maximum pitch range", info="Defines the upper limit of the pitch range that the algorithm will use to determine the fundamental frequency (F0) in the audio signal.", step=1, minimum=380, value=1100, maximum=16000)   
                        rms_mix_rate = gr.Slider(0, 1, value=0.25, step=0.01, label='RMS Mix Rate', info='Controls the extent to which the output signal is mixed with its envelope. A value close to 1 increases the use of the envelope of the output signal, which may improve sound quality.')
                        protect = gr.Slider(0, 0.5, value=0.33, step=0.01, label='Consonant Protection', info='Controls the extent to which individual consonants and breathing sounds are protected from electroacoustic breaks and other artifacts. A maximum value of 0.5 provides the most protection, but may increase the indexing effect, which may negatively impact sound quality. Reducing the value may decrease the extent of protection, but reduce the indexing effect.')
                    with gr.Accordion("Change Index", open=False):
                        index_rate = gr.Slider(0, 1, value=0, label='Index Rate', info='Controls the extent to which the index file influences the analysis results. A higher value increases the influence of the index file, but may amplify breathing artifacts in the audio. Choosing a lower value may help reduce artifacts.')
                        filter_radius = gr.Slider(0, 7, value=3, step=1, label='Filter Radius', info='Manages the radius of filtering the pitch analysis results. If the filtering value is three or higher, median filtering is applied to reduce breathing noise in the audio recording.')       
                    converted_voice = gr.Audio(label='Converted Voice', scale=5, show_share_button=False)                    
                    
                    ref_btn.click(update_models_list, None, outputs=rvc_model)
            
            
            with gr.Row():
                generate_btn.click(song_cover_pipeline,
                              inputs=[song_input, rvc_model, pitch, index_rate, filter_radius, rms_mix_rate, f0_method, crepe_hop_length, protect, output_format],
                              outputs=[converted_voice], api_name="infer_voice")

                
        with gr.TabItem("Download Models"):
            with gr.Row(): 
                model_zip_link = gr.Text(label='Model Download Link')
                model_name = gr.Text(label='Model Name', info='Give your uploaded model a unique name, different from other voice models.')
                download_btn = gr.Button('Download Model', variant='primary')
                dl_output_message = gr.Text(label='Output Message', interactive=False)
                download_btn.click(download_from_url, inputs=[model_zip_link, model_name], outputs=dl_output_message)

                 
    

app.launch(share=True, show_api=False).queue(api_open=False)
