from pathlib import Path
import requests

RVC_DOWNLOAD_LINK = 'https://huggingface.co/kindahex/voice-conversion/resolve/main/'

BASE_DIR = Path(__file__).resolve().parent.parent
rvc_models_dir = BASE_DIR / 'rvc_models'


def dl_model(link, model_name, dir_name):
    with requests.get(f'{link}{model_name}') as r:
        r.raise_for_status()
        with open(dir_name / model_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

if __name__ == '__main__':
    rvc_other_names = ['rmvpe.pt', 'fcpe.pt', 'hubert_base.pt']
    for model in rvc_other_names:
        print(f'Downloading {model}...')
        dl_model(RVC_DOWNLOAD_LINK, model, rvc_models_dir)


    print(f'A {model} downloaded!')
