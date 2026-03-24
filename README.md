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

## <em>Fully 📸functional UI with inbuild video conversion.</em>⬇️
<p align="center">
  <img src="media/ui.png" width="500" alt="App Interface">
</p>

## 🎛️ Parameter Guide

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **Frames** | Integer | `60` | Total number of frames to generate for the animation sequence. |
| **Squish %** | Float | `0.6` | The amount of horizontal distortion (0.01 to 1.0). Higher = intense effect. |
| **Frame Jitter** | Pixels | `2` | Adds per-frame random pixel shifts (0-10) for a "shaking" effect. |
| **Energy Noise** | Std Dev | `50` | Injects randomness (0-200) into seam selection for chaotic warping. |
| **Forward Energy** | Toggle | `OFF` | Use look-ahead algorithms to reduce artifacts (Slower, but higher quality). |
| **Framerate** | FPS | `30` | The playback speed of the exported MP4 video. |
| **Quality** | Select | `High` | Compression level for the final FFmpeg video export. |

---

### 💡 Pro-Tips for Best Results

* **For Smooth Warping:** Keep `Frame Jitter` at 0 and `Energy Noise` below 20.
* **For Maximum Chaos:** Crank `Energy Noise` to 100+ and `Frame Jitter` to 5.
* **Resolution Tip:** For the fastest GPU performance, use source images with a width under **512px**.
* **Video Export:** If you change your mind about the framerate after processing, just click **"Convert Last Result to Video"** to re-render without re-calculating the seams!

### ✨ Features

* **⚡ GPU-Accelerated** – 10-20x faster than CPU using CuPy/CUDA kernels.
* **🎯 Content-Aware** – Intelligent seam carving algorithm that preserves important image details.
* **🌀 Customizable Chaos** – Adjust **Frame Jitter** and **Energy Noise** for unique, glitchy effects.
* **🎬 Built-in Video Export** – Integrated FFmpeg support to convert frames to MP4 instantly.
* **🖥️ User-Friendly GUI** – Simple Tkinter-based interface; no coding required to run.
* **⚙️ Fine-Tuned Control** – Toggle **Forward Energy** for higher quality results at the cost of speed.

###🚀 Quick Start
### *Prerequisites*
* **NVIDIA GPU** (Required for CuPy/CUDA acceleration).
* **Python 3.8+**
* **FFmpeg** (Added to system PATH for video export).

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/content-aware-meme.git
cd content-aware-meme
# Install dependencies (includes CUDA runtime)
pip install -r requirements.txt
```

### 📏 Image Size:
* less than 512px: lightning fast⚡
* 512-1080px: slow but steady ✓
* greater than 1080px: Very slow but possible 🐌


