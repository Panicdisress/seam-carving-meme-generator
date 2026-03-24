<h1 align="center"> Seam-Carving-Meme-Generator </h1>

<p align="center">
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python"></a>
<a href="https://developer.nvidia.com/cuda-toolkit"><img src="https://img.shields.io/badge/CUDA-11.x-green.svg" alt="CUDA"></a>
<a href="#"><img src="https://img.shields.io/badge/GPU-Required-red.svg" alt="GPU"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
</p>

## GPU-accelerated content-aware image resizing for creating distorted animations.

<p align="center"> <img src="media/shaq.gif" alt="description" width="200"> </p>

|Original Image|image compression 400 X 400 px|image compression 250 X 250 px|
|----------------|-------------------------------|-----------------------------|
|<img src="media/nice.jpg" alt="description" width="400">|<img src="media/nice-400.gif" alt="description" width="400">|<img src="media/nice-250.gif" alt="description" width="400">|
|Time taken-->|`1.4 min.`|`33 sec.`|

## <em>Fully functional UI with inbuild video conversion.</em>⬇️
<img src="media/ui.png" alt="description" width="400">

### ✨ Features

* **⚡GPU-Accelerated** – 10-20x faster than CPU using CuPy/CUDA.
* **🎯Content-Aware** – Intelligent seam carving preserves important features.
* **🎛️Customizable Chaos** – Adjust jitter and energy noise for unique effects.
* **📹Built-in Video Export** – One-click FFmpeg integration.
* **🖥️User-Friendly GUI** – No coding required.
* **⚙️Configurable** – Fine-tune every parameter.

###🚀 Quick Start
*prerequisites*
* NVIDIA GPU with CUDA support
* Updated NVIDIA Drivers
* Python 3.8+

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/content-aware-meme.git
cd content-aware-meme

# Install dependencies (includes CUDA runtime)
pip install -r requirements.txt



