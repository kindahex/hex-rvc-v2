# Hex RVC v2

**Hex RVC v2** is an easy-to-use Voice Conversion framework based on VITS, enabling users to create voice models and perform conversions from one voice to another. This repository includes the tools and scripts needed to train models and perform inference with pretrained voice conversion models.

## Features

- **easy voice cloning**: easy to use app to voice clone.
- **Flexible Configuration**: Easily configure and modify model settings.
  
## Requirements
- Python 3.x
- Install dependencies using:
  ```bash
  pip install -r requirements.txt
  ```

## Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kindahex/hex-rvc-v2.git
   cd hex-rvc-v2
   ```

2. **Set up the environment**:
   Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the demo**:
   To test the voice conversion model, use the `demo.py` script:
   ```bash
   python demo.py
   ```



## Folder Structure

- `configs/`: Model configurations.
- `infer_pack/`: Scripts for inference.
- `rvc_models/`: Contains the trained RVC models.
- `song_output/`: Directory for the generated output files.
- `rvc_audios`: Directory for inference file.

# License
This project is licensed under the MIT License.


# feature plan

1. audio separation for inference
2. tts input

# Contribution
If you want to participate and help me with this project feel free to create an [issue](https://github.com/kindahex/hex-rvc-v2/issues) if something goes wrong or make a [pull request](https://github.com/kindahex/hex-rvc-v2/pulls) to improve this project.

**-Any type of contribution is welcome!-**

If you liked this Colab you can star this repository. I will appreciate a lot

## Acknowledgments
Thanks to the open-source community for providing the foundational tools used in this project!

