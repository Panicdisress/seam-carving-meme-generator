import cv2
import os
import numpy as np
import time
import gc
import json

print("Initializing GPU...")
import cupy as cp

if not cp.cuda.is_available():
    print("ERROR: CUDA not available!")
    exit(1)

device = cp.cuda.Device(0)
props = cp.cuda.runtime.getDeviceProperties(0)
print(f"GPU: {props['name'].decode()}")
print(f"GPU Memory: {props['totalGlobalMem'] / 1024**3:.2f} GB\n")

print("Pre-warming GPU...")
x = cp.array([1, 2, 3])
_ = x * 2
_ = cp.asnumpy(x)
print("GPU Ready!\n")

from seam_carving import seam_carve

def get_gpu_memory():
    free, total = device.mem_info
    used = total - free
    return used / 1024**2, total / 1024**2

def generate_animation_sequence():
    # Load config from JSON FIRST
    if not os.path.exists("config.json"):
        print("ERROR: config.json not found! Run GUI.py first.")
        return
    
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    input_image = config["input_image"]
    output_folder = config["output_folder"]
    total_frames = config["total_frames"]
    max_squish_percent = config["max_squish_percent"]
    
    # Chaos parameters
    frame_jitter = config.get("frame_jitter", 2)
    energy_noise = config.get("energy_noise", 50)
    use_forward_energy = config.get("use_forward_energy", False)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    current_frame = cv2.imread(input_image)
    if current_frame is None:
        print(f"ERROR: Could not find {input_image}")
        return

    h, w = current_frame.shape[:2]
    
    total_dx = -int(max_squish_percent * w)
    total_dy = -int(max_squish_percent * h)
    dx_per_frame = total_dx / (total_frames - 1)
    dy_per_frame = total_dy / (total_frames - 1)
    
    # Print header
    print("=" * 60)
    print("STARTING PROCESSING (INCREMENTAL MODE)")
    print("=" * 60)
    print(f"Image: {w}x{h} | Frames: {total_frames} | Squish: {max_squish_percent*100:.0f}%")
    print(f"Total reduction: {total_dx}x{total_dy} pixels")
    print(f"Per frame: {dx_per_frame:.1f}x{dy_per_frame:.1f} pixels")
    print(f"Frame Jitter: {frame_jitter} | Energy Noise: {energy_noise}")
    print("=" * 60)
    print()

    print("STARTING PROCESSING\n")
    start_time = time.time()
    frame_times = []
    
    for i in range(total_frames):
        frame_start = time.time()
        gpu_before, _ = get_gpu_memory()
        
        if i == 0:
            dx_step, dy_step = 0, 0
        else:
            shiver = np.random.randint(-frame_jitter, frame_jitter + 1)
            dx_step = int(dx_per_frame) + shiver
            dy_step = int(dy_per_frame) + shiver
        
        output, _ = seam_carve(current_frame, dy=dy_step, dx=dx_step, 
                               vis=False, energy_noise=energy_noise,
                               use_forward_energy=use_forward_energy)
        
        frame_path = os.path.join(output_folder, f"frame_{i:04d}.png")
        cv2.imwrite(frame_path, output)
        
        current_frame = output
        
        frame_time = time.time() - frame_start
        frame_times.append(frame_time)
        gpu_after, _ = get_gpu_memory()
        
        elapsed = time.time() - start_time
        avg = sum(frame_times) / len(frame_times)
        eta = avg * (total_frames - i - 1)
        
        # Progress line (overwrites previous line)
        print(f"Frame {i+1:3d}: {frame_time:5.1f}s | "
              f"Avg: {avg:5.1f}s | "
              f"GPU: {gpu_before:.0f}->{gpu_after:.0f} MB | "
              f"ETA: {eta:.0f}s | "
              f"Total: {elapsed/60:.1f}min", end='\r')
        
        if (i + 1) % 5 == 0:
            gc.collect()
            cp.get_default_memory_pool().free_all_blocks()
    
    total_time = time.time() - start_time
    
    # ============================================================
    # FINAL SUMMARY - Save to config.json
    # ============================================================
    summary = {
        "total_frames": total_frames,
        "total_time_seconds": round(total_time, 2),
        "total_time_minutes": round(total_time / 60, 2),
        "average_time_per_frame": round(total_time / total_frames, 2),
        "fastest_frame": round(min(frame_times), 2),
        "slowest_frame": round(max(frame_times), 2),
        "output_folder": output_folder
    }
    
    # Save summary to config
    config["processing_summary"] = summary
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    # Print summary to console (GUI will capture this)
    print("\n\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total Frames Generated: {total_frames}")
    print(f"Total Time Taken:       {total_time:.1f} seconds ({total_time/60:.2f} minutes)")
    print(f"Average Time per Frame: {total_time/total_frames:.2f} seconds")
    print(f"Fastest Frame:          {min(frame_times):.2f} seconds")
    print(f"Slowest Frame:          {max(frame_times):.2f} seconds")
    print(f"Output Folder:          {output_folder}")
    print("=" * 60)

if __name__ == "__main__":
    generate_animation_sequence()