import gradio as gr
    

def show_hop_slider(pitch_detection_algo):
    if pitch_detection_algo in ['mangio-crepe']:
        return gr.update(visible=True)
    else:
        return gr.update(visible=False)


def update_f0_method(use_hybrid_methods):
    if use_hybrid_methods:
        return gr.update(choices=['hybrid[rmvpe+fcpe]', 'hybrid[rmvpe+crepe]', 'hybrid[crepe+rmvpe]', 'hybrid[crepe+fcpe]', 'hybrid[crepe+rmvpe+fcpe]'], value='hybrid[rmvpe+fcpe]')
    else:
        return gr.update(choices=['rmvpe+', 'fcpe', 'rmvpe', 'mangio-crepe', 'crepe'], value='rmvpe+')


def update_button_text():
    return gr.update(label="Upload different audio file")

def update_button_text_voc():
    return gr.update(label="Upload different vocals")

def update_button_text_inst():
    return gr.update(label="Upload different instrumental")
