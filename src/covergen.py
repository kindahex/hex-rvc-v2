import os
import json
import shutil
import urllib.request
import zipfile
import gdown
import gradio as gr

from main import song_cover_pipeline
from audio_effects import add_audio_effects
from modules.model_management import ignore_files, update_models_list, extract_zip, download_from_url, upload_zip_model
from modules.ui_updates import show_hop_slider, update_f0_method, update_button_text, update_button_text_voc, update_button_text_inst
from modules.file_processing import process_file_upload

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rvc_models_dir = os.path.join(BASE_DIR, 'rvc_models')
output_dir = os.path.join(BASE_DIR, 'song_output')

if __name__ == '__main__':
    voice_models = ignore_files(rvc_models_dir)

    with gr.Blocks(title='CoverGen Lite - Politrees (v0.2)', theme=gr.themes.Soft(primary_hue="green", secondary_hue="green", neutral_hue="neutral", spacing_size="sm", radius_size="lg")) as app:
        with gr.Tab("Welcome/Contacts"):
            gr.HTML("<center><h1>Welcome to CoverGen Lite - Politrees (v0.2)</h1></center>")
            with gr.Row():
                with gr.Column(variant='panel'):
                    gr.HTML("<center><h2><a href='https://t.me/Politrees2'>Telegram</a></h2></center>")
                    gr.HTML("<center><h2><a href='https://vk.com/artem__bebroy'>VKontakte</a></h2></center>")
                with gr.Column(variant='panel'):
                    gr.HTML("<center><h2><a href='https://t.me/pol1trees'>Telegram Channel</a></h2></center>")
                    gr.HTML("<center><h2><a href='https://t.me/+GMTP7hZqY0E4OGRi'>Telegram Chat</a></h2></center>")
            with gr.Column(variant='panel'):
                gr.HTML("<center><h2><a href='https://www.youtube.com/channel/UCHb3fZEVxUisnqLqCrEM8ZA'>YouTube</a></h2></center>")
                gr.HTML("<center><h2><a href='https://github.com/Bebra777228'>GitHub</a></h2></center>")

        with gr.Tab("Voice Conversion"):
            with gr.Row(equal_height=False):
                with gr.Column(scale=1, variant='panel'):
                    with gr.Group():
                        rvc_model = gr.Dropdown(voice_models, label='Voice Models')
                        ref_btn = gr.Button('Refresh Models List', variant='primary')
                    with gr.Group():
                        pitch = gr.Slider(-24, 24, value=0, step=0.5, label='Pitch Adjustment', info='-24 - male voice || 24 - female voice')

                with gr.Column(scale=2, variant='panel'):
                    with gr.Group():
                        local_file = gr.Audio(label='Audio File', interactive=False, show_download_button=False, show_share_button=False)
                        uploaded_file = gr.UploadButton(label='Upload Audio File', file_types=['audio'], variant='primary')
                        uploaded_file.upload(process_file_upload, inputs=[uploaded_file], outputs=[local_file])
                        uploaded_file.upload(update_button_text, outputs=[uploaded_file])

            with gr.Group():
                with gr.Row(variant='panel'):
                    generate_btn = gr.Button("Generate", variant='primary', scale=1)
                    converted_voice = gr.Audio(label='Converted Voice', scale=5, show_share_button=False)
                    output_format = gr.Dropdown(['mp3', 'flac', 'wav'], value='mp3', label='File Format', scale=0.1, allow_custom_value=False, filterable=False)

            with gr.Accordion('Voice Conversion Settings', open=False):
                with gr.Group():
                    with gr.Column(variant='panel'):
                        use_hybrid_methods = gr.Checkbox(label="Use Hybrid Methods", value=False)
                        f0_method = gr.Dropdown(['rmvpe+', 'fcpe', 'rmvpe', 'mangio-crepe', 'crepe'], value='rmvpe+', label='F0 Method', allow_custom_value=False, filterable=False)
                        use_hybrid_methods.change(update_f0_method, inputs=use_hybrid_methods, outputs=f0_method)
                        crepe_hop_length = gr.Slider(8, 512, value=128, step=8, visible=False, label='Crepe Hop Length')
                        f0_method.change(show_hop_slider, inputs=f0_method, outputs=crepe_hop_length)
                    with gr.Column(variant='panel'):
                        index_rate = gr.Slider(0, 1, value=0, label='Index Rate', info='Controls the extent to which the index file influences the analysis results. A higher value increases the influence of the index file, but may amplify breathing artifacts in the audio. Choosing a lower value may help reduce artifacts.')
                        filter_radius = gr.Slider(0, 7, value=3, step=1, label='Filter Radius', info='Manages the radius of filtering the pitch analysis results. If the filtering value is three or higher, median filtering is applied to reduce breathing noise in the audio recording.')
                        rms_mix_rate = gr.Slider(0, 1, value=0.25, step=0.01, label='RMS Mix Rate', info='Controls the extent to which the output signal is mixed with its envelope. A value close to 1 increases the use of the envelope of the output signal, which may improve sound quality.')
                        protect = gr.Slider(0, 0.5, value=0.33, step=0.01, label='Consonant Protection', info='Controls the extent to which individual consonants and breathing sounds are protected from electroacoustic breaks and other artifacts. A maximum value of 0.5 provides the most protection, but may increase the indexing effect, which may negatively impact sound quality. Reducing the value may decrease the extent of protection, but reduce the indexing effect.')

            ref_btn.click(update_models_list, None, outputs=rvc_model)
            generate_btn.click(song_cover_pipeline,
                              inputs=[uploaded_file, rvc_model, pitch, index_rate, filter_radius, rms_mix_rate, f0_method, crepe_hop_length, protect, output_format],
                              outputs=[converted_voice])

        with gr.Tab('Merge/Process'):
            with gr.Row(equal_height=False):
                with gr.Column(variant='panel'):
                    with gr.Group():
                        vocal_audio = gr.Audio(label='Vocals', interactive=False, show_download_button=False, show_share_button=False)
                        upload_vocal_audio = gr.UploadButton(label='Upload Vocals', file_types=['audio'], variant='primary')
                        upload_vocal_audio.upload(process_file_upload, inputs=[upload_vocal_audio], outputs=[vocal_audio])
                        upload_vocal_audio.upload(update_button_text_voc, outputs=[upload_vocal_audio])

                with gr.Column(variant='panel'):
                    with gr.Group():
                        instrumental_audio = gr.Audio(label='Instrumental', interactive=False, show_download_button=False, show_share_button=False)
                        upload_instrumental_audio = gr.UploadButton(label='Upload Instrumental', file_types=['audio'], variant='primary')
                        upload_instrumental_audio.upload(process_file_upload, inputs=[upload_instrumental_audio], outputs=[instrumental_audio])
                        upload_instrumental_audio.upload(update_button_text_inst, outputs=[upload_instrumental_audio])

            with gr.Group():
                with gr.Row(variant='panel'):
                    process_btn = gr.Button("Process", variant='primary', scale=1)
                    ai_cover = gr.Audio(label='AI-Cover', scale=5, show_share_button=False)
                    output_format = gr.Dropdown(['mp3', 'flac', 'wav'], value='mp3', label='File Format', scale=0.1, allow_custom_value=False, filterable=False)

            with gr.Accordion('Audio Mixing Settings', open=False):
                gr.HTML('<center><h2>Volume Adjustment</h2></center>')
                with gr.Row(variant='panel'):
                    vocal_gain = gr.Slider(-10, 10, value=0, step=1, label='Vocals', scale=1)
                    instrumental_gain = gr.Slider(-10, 10, value=0, step=1, label='Instrumental', scale=1)
                    clear_btn = gr.Button("Clear All Effects", scale=0.1)

                with gr.Accordion('Effects', open=False):
                    with gr.Accordion('Reverb', open=False):
                        with gr.Group():
                            with gr.Column(variant='panel'):
                                with gr.Row():
                                    reverb_rm_size = gr.Slider(0, 1, value=0.15, label='Room Size', info='This parameter determines the size of the virtual room in which the reverb will sound. A higher value means a larger room and a longer reverb tail.')
                                    reverb_width = gr.Slider(0, 1, value=1.0, label='Reverb Width', info='This parameter determines the width of the reverb sound. The higher the value, the wider the reverb sound.')
                                with gr.Row():
                                    reverb_wet = gr.Slider(0, 1, value=0.1, label='Wet Level', info='This parameter determines the level of reverb. The higher the value, the stronger the reverb effect and the longer the "tail".')
                                    reverb_dry = gr.Slider(0, 1, value=0.8, label='Dry Level', info='This parameter determines the level of the original sound without reverb. The lower the value, the quieter the AI voice. If the value is 0, the original sound will disappear completely.')
                                with gr.Row():
                                    reverb_damping = gr.Slider(0, 1, value=0.7, label='Damping Level', info='This parameter determines the absorption of high frequencies in the reverb. The higher the value, the stronger the absorption of frequencies and the less "bright" the reverb sound.')

                    with gr.Accordion('Chorus', open=False):
                        with gr.Group():
                            with gr.Column(variant='panel'):
                                with gr.Row():
                                    chorus_rate_hz = gr.Slider(0.1, 10, value=0, label='Chorus Rate', info='This parameter determines the speed of the chorus effect in hertz. The higher the value, the faster the sounds will oscillate.')
                                    chorus_depth = gr.Slider(0, 1, value=0, label='Chorus Depth', info='This parameter determines the depth of the chorus effect. The higher the value, the stronger the chorus effect.')
                                with gr.Row():
                                    chorus_centre_delay_ms = gr.Slider(0, 50, value=0, label='Centre Delay (ms)', info='This parameter determines the delay of the central signal of the chorus effect in milliseconds. The higher the value, the longer the delay.')
                                    chorus_feedback = gr.Slider(0, 1, value=0, label='Feedback', info='This parameter determines the level of feedback of the chorus effect. The higher the value, the stronger the feedback effect.')
                                with gr.Row():
                                    chorus_mix = gr.Slider(0, 1, value=0, label='Mix', info='This parameter determines the level of mixing the original signal and the chorus effect. The higher the value, the stronger the chorus effect.')

                with gr.Accordion('Processing', open=False):
                    with gr.Accordion('Compressor', open=False):
                        with gr.Row(variant='panel'):
                            compressor_ratio = gr.Slider(1, 20, value=4, label='Ratio', info='This parameter controls the amount of compression applied to the audio. A higher value means more compression, which reduces the dynamic range of the audio, making loud parts quieter and quiet parts louder.')
                            compressor_threshold = gr.Slider(-60, 0, value=-16, label='Threshold', info='This parameter sets the threshold level in decibels below which the compressor begins to operate. The compressor compresses loud sounds to make the sound more even. The lower the threshold, the more sounds will be subject to compression.')

                    with gr.Accordion('Filters', open=False):
                        with gr.Row(variant='panel'):
                            low_shelf_gain = gr.Slider(-20, 20, value=0, label='Low Shelf Filter', info='This parameter controls the gain (volume) of low frequencies. A positive value boosts low frequencies, making the sound bassier. A negative value cuts low frequencies, making the sound brighter.')
                            high_shelf_gain = gr.Slider(-20, 20, value=0, label='High Shelf Filter', info='This parameter controls the gain of high frequencies. A positive value boosts high frequencies, making the sound brighter. A negative value cuts high frequencies, making the sound duller.')

                    with gr.Accordion('Noise Gate', open=False):
                        with gr.Group():
                            with gr.Column(variant='panel'):
                                with gr.Row():
                                    noise_gate_threshold = gr.Slider(-60, 0, value=-30, label='Threshold', info='This parameter sets the threshold level in decibels below which the signal is considered noise. When the signal drops below this threshold, the noise gate activates and reduces the signal level.')
                                    noise_gate_ratio = gr.Slider(1, 20, value=6, label='Ratio', info='This parameter sets the level of noise reduction. A higher value means more noise reduction.')
                                with gr.Row():
                                    noise_gate_attack = gr.Slider(0, 100, value=10, label='Attack Time (ms)', info='This parameter controls the speed at which the noise gate opens when the sound becomes loud enough. A higher value means the gate opens slower.')
                                    noise_gate_release = gr.Slider(0, 1000, value=100, label='Release Time (ms)', info='This parameter controls the speed at which the noise gate closes when the sound becomes quiet enough. A higher value means the gate closes slower.')

            process_btn.click(add_audio_effects,
                            inputs=[upload_vocal_audio, upload_instrumental_audio, reverb_rm_size, reverb_wet, reverb_dry, reverb_damping,
                            reverb_width, low_shelf_gain, high_shelf_gain, compressor_ratio, compressor_threshold,
                            noise_gate_threshold, noise_gate_ratio, noise_gate_attack, noise_gate_release,
                            chorus_rate_hz, chorus_depth, chorus_centre_delay_ms, chorus_feedback, chorus_mix,
                            output_format, vocal_gain, instrumental_gain],
                            outputs=[ai_cover])

            default_values = [0, 0, 0.15, 1.0, 0.1, 0.8, 0.7, 0, 0, 0, 0, 0, 4, -16, 0, 0, -30, 6, 10, 100]
            clear_btn.click(lambda: default_values,
                            outputs=[vocal_gain, instrumental_gain, reverb_rm_size, reverb_width, reverb_wet, reverb_dry, reverb_damping,
                            chorus_rate_hz, chorus_depth, chorus_centre_delay_ms, chorus_feedback, chorus_mix,
                            compressor_ratio, compressor_threshold, low_shelf_gain, high_shelf_gain, noise_gate_threshold,
                            noise_gate_ratio, noise_gate_attack, noise_gate_release])

        with gr.Tab('Model downloader'):
            with gr.Tab('download from Link'):
                with gr.Row():
                    with gr.Column(variant='panel'):
                        gr.HTML("<center><h3>Paste the link from <a href='https://huggingface.co/' target='_blank'>HuggingFace</a>, <a href='https://pixeldrain.com/' target='_blank'>Pixeldrain</a>, <a href='https://drive.google.com/' target='_blank'>Google Drive</a> or <a href='https://mega.nz/' target='_blank'>Mega</a> into the field below</h3></center>")
                        model_zip_link = gr.Text(label='Model Download Link')
                    with gr.Column(variant='panel'):
                        with gr.Group():
                            model_name = gr.Text(label='Model Name', info='Give your uploaded model a unique name, different from other voice models.')
                            download_btn = gr.Button('Download Model', variant='primary')

                dl_output_message = gr.Text(label='Output Message', interactive=False)
                download_btn.click(download_from_url, inputs=[model_zip_link, model_name], outputs=dl_output_message)

            with gr.Tab('Upload Locally'):
                with gr.Row(equal_height=False):
                    with gr.Column(variant='panel'):
                        zip_file = gr.File(label='Zip File', file_types=['.zip'], file_count='single')
                    with gr.Column(variant='panel'):
                        gr.HTML("<h3>1. Find and download the files: .pth and optional .index file</h3>")
                        gr.HTML("<h3>2. Put the file(s) into a ZIP archive and place it in the upload area</h3>")
                        gr.HTML('<h3>3. Wait for the ZIP archive to fully upload to the interface</h3>')
                        with gr.Group():
                            local_model_name = gr.Text(label='Model Name', info='Give your uploaded model a unique name, different from other voice models.')
                            model_upload_button = gr.Button('Upload Model', variant='primary')

                local_upload_output_message = gr.Text(label='Output Message', interactive=False)
                model_upload_button.click(upload_zip_model, inputs=[zip_file, local_model_name], outputs=local_upload_output_message)

    app.launch(max_threads=512, quiet=True, show_error=True, show_api=False).queue(max_size=1022, default_concurrency_limit=1, api_open=False)