# [Project Name] - seam-carving-meme-generator
# Derived from: https://github.com/andrewdcampbell/seam-carving
# Modified for GPU acceleration: Copyright (c) 2026 [Your Name]
#
# Licensed under GNU General Public License v3.0



import cupy as cp
import cupyx.scipy.ndimage as ndi
import cv2
import numpy as np
import time

# Configuration (defaults, overridden by config.json)
USE_FORWARD_ENERGY = False
ENERGY_MASK_CONST = 100000.0
MASK_THRESHOLD = 10

# Get GPU device for memory tracking
device = cp.cuda.Device(0)

def get_gpu_mem():
    free, total = device.mem_info
    return (total - free) / 1024**2

def visualize(im_gpu, boolmask_gpu=None, rotate=False):
    vis = cp.asnumpy(im_gpu).astype(np.uint8)
    if boolmask_gpu is not None:
        mask_cpu = cp.asnumpy(boolmask_gpu)
        vis[np.where(mask_cpu == False)] = np.array([255, 200, 200])
    if rotate:
        vis = np.rot90(vis, 3)
    cv2.imshow("visualization", vis)
    cv2.waitKey(1)
    return vis

def rotate_image(image, clockwise):
    k = 1 if clockwise else 3
    return cp.rot90(image, k)

def backward_energy(im_gpu, energy_noise=50):
    xgrad = ndi.convolve1d(im_gpu, cp.array([1, 0, -1], dtype=cp.float64), axis=1, mode='wrap')
    ygrad = ndi.convolve1d(im_gpu, cp.array([1, 0, -1], dtype=cp.float64), axis=0, mode='wrap')
    grad_mag = cp.sqrt(cp.sum(xgrad**2, axis=2) + cp.sum(ygrad**2, axis=2))
    
    # Add chaos noise (configurable)
    if energy_noise > 0:
        noise = cp.random.normal(0, energy_noise, grad_mag.shape)
        return grad_mag + noise
    return grad_mag

def forward_energy(im_gpu):
    h, w = im_gpu.shape[:2]
    if im_gpu.dtype == cp.uint8:
        im_cpu = cp.asnumpy(im_gpu)
        im_gray = cv2.cvtColor(im_cpu, cv2.COLOR_BGR2GRAY).astype(cp.float64)
        im_gray = cp.asarray(im_gray)
    else:
        if len(im_gpu.shape) == 3:
            im_gray = cp.mean(im_gpu, axis=2)
        else:
            im_gray = im_gpu

    m = cp.zeros((h, w), dtype=cp.float64)
    energy = cp.zeros((h, w), dtype=cp.float64)
    
    U = cp.roll(im_gray, 1, axis=0)
    L = cp.roll(im_gray, 1, axis=1)
    R = cp.roll(im_gray, -1, axis=1)
    
    cU = cp.abs(R - L)
    cL = cp.abs(U - L) + cU
    cR = cp.abs(U - R) + cU
    
    for i in range(1, h):
        m_prev = m[i-1]
        mL = cp.roll(m_prev, 1)
        mR = cp.roll(m_prev, -1)
        mU = m_prev
        
        vU = mU + cU[i]
        vL = mL + cL[i]
        vR = mR + cR[i]
        
        candidates = cp.stack([vU, vL, vR], axis=0)
        min_idx = cp.argmin(candidates, axis=0)
        
        maskU = (min_idx == 0)
        maskL = (min_idx == 1)
        maskR = (min_idx == 2)
        
        m[i] = cp.minimum(vU, cp.minimum(vL, vR))
        e_row = cU[i] * maskU + cL[i] * maskL + cR[i] * maskR
        energy[i] = e_row

    return energy

def remove_seam(im_gpu, boolmask_gpu):
    h, w = im_gpu.shape[:2]
    if im_gpu.ndim == 3:
        boolmask3c = cp.stack([boolmask_gpu] * 3, axis=2)
        return im_gpu[boolmask3c].reshape((h, w - 1, 3))
    else:
        return im_gpu[boolmask_gpu].reshape((h, w - 1))

def remove_seam_grayscale(im_gpu, boolmask_gpu):
    h, w = im_gpu.shape[:2]
    return im_gpu[boolmask_gpu].reshape((h, w - 1))

def add_seam(im_gpu, seam_idx_cpu):
    h, w = im_gpu.shape[:2]
    output = cp.zeros((h, w + 1, 3), dtype=im_gpu.dtype)
    
    for row in range(h):
        col = int(seam_idx_cpu[row])
        if col == 0:
            avg = (im_gpu[row, col, :] + im_gpu[row, col+1, :]) / 2.0
        else:
            avg = (im_gpu[row, col-1, :] + im_gpu[row, col, :]) / 2.0
        output[row, :col, :] = im_gpu[row, :col, :]
        output[row, col, :] = avg
        output[row, col+1:, :] = im_gpu[row, col:, :]
    return output

def add_seam_grayscale(im_gpu, seam_idx_cpu):
    h, w = im_gpu.shape[:2]
    output = cp.zeros((h, w + 1), dtype=im_gpu.dtype)
    for row in range(h):
        col = int(seam_idx_cpu[row])
        if col == 0:
            avg = (im_gpu[row, col] + im_gpu[row, col+1]) / 2.0
        else:
            avg = (im_gpu[row, col-1] + im_gpu[row, col]) / 2.0
        output[row, :col] = im_gpu[row, :col]
        output[row, col] = avg
        output[row, col+1:] = im_gpu[row, col:]
    return output

def get_minimum_seam(im_gpu, mask_gpu=None, remove_mask_gpu=None):
    h, w = im_gpu.shape[:2]
    energyfn = forward_energy if USE_FORWARD_ENERGY else backward_energy
    M = energyfn(im_gpu)

    if mask_gpu is not None:
        M = M + (mask_gpu > MASK_THRESHOLD) * ENERGY_MASK_CONST
    if remove_mask_gpu is not None:
        M = M - (remove_mask_gpu > MASK_THRESHOLD) * (ENERGY_MASK_CONST * 100)

    M_cpu = cp.asnumpy(M)
    backtrack = np.zeros((h, w), dtype=np.int32)

    for i in range(1, h):
        for j in range(w):
            if j == 0:
                idx = np.argmin(M_cpu[i - 1, j:j + 2])
                backtrack[i, j] = idx + j
                min_energy = M_cpu[i-1, idx + j]
            else:
                idx = np.argmin(M_cpu[i - 1, j - 1:j + 2])
                backtrack[i, j] = idx + j - 1
                min_energy = M_cpu[i - 1, idx + j - 1]
            M_cpu[i, j] += min_energy

    seam_idx = []
    boolmask = np.ones((h, w), dtype=np.bool_)
    j = np.argmin(M_cpu[-1])
    for i in range(h-1, -1, -1):
        boolmask[i, j] = False
        seam_idx.append(j)
        j = backtrack[i, j]

    seam_idx.reverse()
    return np.array(seam_idx), cp.asarray(boolmask)

def seams_removal(im_gpu, num_remove, mask_gpu=None, vis=False, rot=False):
    remaining = num_remove
    while remaining > 0:
        seam_idx, boolmask = get_minimum_seam(im_gpu, mask_gpu)
        im_gpu = remove_seam(im_gpu, boolmask)
        if mask_gpu is not None: 
            mask_gpu = remove_seam_grayscale(mask_gpu, boolmask)
        remaining -= 1
        cp.get_default_memory_pool().free_all_blocks()
    return im_gpu, mask_gpu

def seams_insertion(im_gpu, num_add, mask_gpu=None, vis=False, rot=False):
    seams_record = []
    temp_im = im_gpu.copy()
    temp_mask = mask_gpu.copy() if mask_gpu is not None else None
    
    for _ in range(num_add):
        seam_idx, boolmask = get_minimum_seam(temp_im, temp_mask)
        seams_record.append(seam_idx)
        temp_im = remove_seam(temp_im, boolmask)
        if temp_mask is not None: 
            temp_mask = remove_seam_grayscale(temp_mask, boolmask)
            
    seams_record.reverse()
    
    for _ in range(num_add):
        seam = seams_record.pop()
        im_gpu = add_seam(im_gpu, seam)
        if mask_gpu is not None: 
            mask_gpu = add_seam_grayscale(mask_gpu, seam)
        for i, remaining_seam in enumerate(seams_record):
            remaining_seam[np.where(remaining_seam >= seam)] += 2         
    return im_gpu, mask_gpu

def seam_carve(im_cpu, dy, dx, mask=None, vis=False, energy_noise=50, use_forward_energy=False):
    """Main function with configurable chaos parameters"""
    global USE_FORWARD_ENERGY
    USE_FORWARD_ENERGY = use_forward_energy
    
    print(f"\n  [INFO] seam_carve START | GPU: {get_gpu_mem():.1f} MB")
    print(f"  [INFO] Energy Noise: {energy_noise} | Forward Energy: {use_forward_energy}")
    
    # 1. Transfer Input to GPU
    t0 = time.time()
    im_gpu = cp.asarray(im_cpu.astype(cp.float64))
    mask_gpu = cp.asarray(mask.astype(cp.float64)) if mask is not None else None
    print(f"  [INFO] Input to GPU: {time.time()-t0:.3f}s | GPU: {get_gpu_mem():.1f} MB")
    
    output_gpu = im_gpu
    
    # 2. Process dx (width)
    if dx != 0:
        t0 = time.time()
        if dx < 0: 
            output_gpu, mask_gpu = seams_removal(output_gpu, -dx, mask_gpu, vis)
        else: 
            output_gpu, mask_gpu = seams_insertion(output_gpu, dx, mask_gpu, vis)
        print(f"  [INFO] DX processing: {time.time()-t0:.3f}s | GPU: {get_gpu_mem():.1f} MB")
        
    # 3. Process dy (height)
    if dy != 0:
        t0 = time.time()
        output_gpu = rotate_image(output_gpu, True)
        if mask_gpu is not None: 
            mask_gpu = rotate_image(mask_gpu, True)
        
        if dy < 0: 
            output_gpu, mask_gpu = seams_removal(output_gpu, -dy, mask_gpu, vis, rot=True)
        else: 
            output_gpu, mask_gpu = seams_insertion(output_gpu, dy, mask_gpu, vis, rot=True)
            
        output_gpu = rotate_image(output_gpu, False)
        if mask_gpu is not None: 
            mask_gpu = rotate_image(mask_gpu, False)
        print(f"  [INFO] DY processing: {time.time()-t0:.3f}s | GPU: {get_gpu_mem():.1f} MB")

    # 4. Transfer Output back to CPU
    t0 = time.time()
    output_cpu = cp.asnumpy(output_gpu).astype(np.uint8)
    mask_cpu = cp.asnumpy(mask_gpu).astype(np.uint8) if mask_gpu is not None else None
    print(f"  [INFO] Output to CPU: {time.time()-t0:.3f}s | GPU: {get_gpu_mem():.1f} MB")
    
    # CRITICAL: Clean up GPU memory BEFORE returning
    del im_gpu, output_gpu, mask_gpu
    cp.get_default_memory_pool().free_all_blocks()
    cp.get_default_pinned_memory_pool().free_all_blocks()
    print(f"  [INFO] After cleanup: {get_gpu_mem():.1f} MB")
    
    return output_cpu, mask_cpu