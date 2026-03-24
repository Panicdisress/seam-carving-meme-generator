import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, scrolledtext
import json
import subprocess
import os
import sys
import threading
from datetime import datetime

class SeamCarvingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Content-Aware Distortion")
        self.root.geometry("650x750")
        self.root.resizable(False, False)
        
        self.image_path = tk.StringVar()
        self.process = None
        self.is_processing = False
        self.convert_to_video = tk.BooleanVar(value=True)
        self.video_framerate = tk.StringVar(value="30")
        self.video_quality = tk.StringVar(value="high")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        tk.Label(self.root, text="Content-Aware Distortion", 
                font=("Arial", 20, "bold")).pack(pady=10)
        
        # IMAGE SELECTION
        frame1 = tk.Frame(self.root)
        frame1.pack(pady=10, padx=20, fill="x")
        tk.Label(frame1, text="Image:", font=("Arial", 11)).pack(side="left")
        tk.Entry(frame1, textvariable=self.image_path, width=35).pack(side="left", padx=10)
        tk.Button(frame1, text="Browse", command=self.browse_image).pack(side="left")
        
        # FRAMES
        frame2 = tk.Frame(self.root)
        frame2.pack(pady=10, padx=20, fill="x")
        tk.Label(frame2, text="Frames:", font=("Arial", 11), width=10).pack(side="left")
        self.frames_entry = tk.Entry(frame2, width=10)
        self.frames_entry.pack(side="left", padx=10)
        self.frames_entry.insert(0, "60")
        
        # SQUISH PERCENTAGE
        frame3 = tk.Frame(self.root)
        frame3.pack(pady=10, padx=20, fill="x")
        tk.Label(frame3, text="Squish %:", font=("Arial", 11), width=10).pack(side="left")
        self.squish_entry = tk.Entry(frame3, width=10)
        self.squish_entry.pack(side="left", padx=10)
        self.squish_entry.insert(0, "0.6")
        tk.Label(frame3, text="(0.01 to 1.0) default = 0.6", font=("Arial", 9), fg="gray").pack(side="left", padx=5)
        
        # CHAOS OPTIONS
        chaos_frame = tk.LabelFrame(self.root, text="Chaos / Jitter Options", 
                                   font=("Arial", 11, "bold"), padx=10, pady=10)
        chaos_frame.pack(pady=15, padx=20, fill="x")
        
        # Frame Jitter
        tk.Label(chaos_frame, text="Frame Jitter:", 
                font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.jitter_entry = tk.Entry(chaos_frame, width=8)
        self.jitter_entry.grid(row=0, column=1, sticky="w", padx=10)
        self.jitter_entry.insert(0, "2")
        tk.Label(chaos_frame, text="pixels (0-10) default = 2", font=("Arial", 9), 
                fg="gray").grid(row=0, column=2, sticky="w")
        
        # Energy Noise
        tk.Label(chaos_frame, text="Energy Noise:", 
                font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.noise_entry = tk.Entry(chaos_frame, width=8)
        self.noise_entry.grid(row=1, column=1, sticky="w", padx=10)
        self.noise_entry.insert(0, "50")
        tk.Label(chaos_frame, text="std dev (0-200) default = 50", font=("Arial", 9), 
                fg="gray").grid(row=1, column=2, sticky="w")
        
        # Forward Energy Toggle
        self.forward_energy_var = tk.BooleanVar(value=False)
        tk.Checkbutton(chaos_frame, text="Use Forward Energy (slower, better quality)", 
                      variable=self.forward_energy_var,
                      font=("Arial", 10)).grid(row=2, column=0, columnspan=3, 
                                               sticky="w", pady=5)
        
        # Store widgets that support state
        self.chaos_widgets = [
            self.jitter_entry,
            self.noise_entry
        ]
        
        # VIDEO OPTIONS
        video_frame = tk.LabelFrame(self.root, text="Video Export Options", 
                                   font=("Arial", 11, "bold"), padx=10, pady=10)
        video_frame.pack(pady=15, padx=20, fill="x")
        
        tk.Checkbutton(video_frame, text="Convert to video after processing", 
                      variable=self.convert_to_video, command=self.toggle_video_options,
                      font=("Arial", 10)).pack(anchor="w", pady=5)
        
        self.video_settings_frame = tk.Frame(video_frame)
        self.video_settings_frame.pack(fill="x", pady=5)
        
        tk.Label(self.video_settings_frame, text="Framerate:", 
                font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.fps_entry = tk.Entry(self.video_settings_frame, textvariable=self.video_framerate, 
                width=8)
        self.fps_entry.grid(row=0, column=1, sticky="w", padx=10)
        tk.Label(self.video_settings_frame, text="fps", font=("Arial", 9), 
                fg="gray").grid(row=0, column=2, sticky="w")
        
        tk.Label(self.video_settings_frame, text="Quality:", 
                font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        quality_frame = tk.Frame(self.video_settings_frame)
        quality_frame.grid(row=1, column=1, columnspan=2, sticky="w")
        
        self.quality_high = tk.Radiobutton(quality_frame, text="High", variable=self.video_quality, 
                      value="high")
        self.quality_high.pack(side="left")
        self.quality_medium = tk.Radiobutton(quality_frame, text="Medium", variable=self.video_quality, 
                      value="medium")
        self.quality_medium.pack(side="left", padx=10)
        self.quality_low = tk.Radiobutton(quality_frame, text="Low", variable=self.video_quality, 
                      value="low")
        self.quality_low.pack(side="left")
        
        # Store for toggle function
        self.video_widgets = [
            self.fps_entry,
            self.quality_high,
            self.quality_medium,
            self.quality_low
        ]
        
        # START BUTTON
        self.start_btn = tk.Button(self.root, text="Start Processing", 
                                  command=self.start_processing,
                                  font=("Arial", 14, "bold"), 
                                  bg="#4CAF50", fg="white",
                                  padx=30, pady=12)
        self.start_btn.pack(pady=15)
        
        # SEPARATE VIDEO BUTTON
        self.video_btn = tk.Button(self.root, text="Convert Last Result to Video", 
                                  command=self.convert_frames_to_video,
                                  font=("Arial", 11), 
                                  bg="#2196F3", fg="white",
                                  padx=20, pady=8)
        self.video_btn.pack(pady=5)
        
        # STATUS LABEL
        self.status_label = tk.Label(self.root, text="Ready", 
                                    font=("Arial", 12), fg="green")
        self.status_label.pack(pady=5)
        
        # PROGRESS BAR
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, 
                                               maximum=100, length=500)
        self.progress_bar.pack(pady=5)
        
        # LOG TEXT AREA
        tk.Label(self.root, text="Processing Log:", font=("Arial", 10, "bold")).pack(pady=(10,0))
        self.log_text = scrolledtext.ScrolledText(self.root, width=75, height=12, 
                                                  font=("Consolas", 9))
        self.log_text.pack(pady=5, padx=10)
        self.log_text.config(state=tk.DISABLED)
        
        self.toggle_video_options()
        self.toggle_chaos_options()
        
    def toggle_video_options(self):
        """Enable/disable video settings based on checkbox"""
        state = tk.NORMAL if self.convert_to_video.get() else tk.DISABLED
        for widget in self.video_widgets:
            widget.config(state=state)
            
    def toggle_chaos_options(self):
        """Enable/disable chaos settings (placeholder for future expansion)"""
        pass
            
    def browse_image(self):
        filepath = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if filepath:
            self.image_path.set(filepath)
            self.log(f"Selected image: {filepath}")
            
    def validate_inputs(self):
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image!")
            return False
            
        if not os.path.exists(self.image_path.get()):
            messagebox.showerror("Error", f"Image not found: {self.image_path.get()}")
            return False
            
        try:
            frames = int(self.frames_entry.get())
            if frames <= 0 or frames > 1000:
                raise ValueError("Frames must be between 1 and 1000")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid frames value: {e}")
            return False
            
        try:
            squish = float(self.squish_entry.get())
            if squish <= 0 or squish > 1.0:
                raise ValueError("Squish must be between 0.01 and 1.0")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid squish value: {e}")
            return False
            
        try:
            jitter = int(self.jitter_entry.get())
            if jitter < 0 or jitter > 10:
                raise ValueError("Jitter must be between 0 and 10")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid jitter value: {e}")
            return False
            
        try:
            noise = int(self.noise_entry.get())
            if noise < 0 or noise > 200:
                raise ValueError("Noise must be between 0 and 200")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid noise value: {e}")
            return False
            
        try:
            fps = int(self.video_framerate.get())
            if fps <= 0 or fps > 60:
                raise ValueError("Framerate must be between 1 and 60")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid framerate: {e}")
            return False
            
        if not os.path.exists("frame-generator.py"):
            messagebox.showerror("Error", "frame-generator.py not found!")
            return False
            
        if not os.path.exists("seam_carving.py"):
            messagebox.showerror("Error", "seam_carving.py not found!")
            return False
            
        return True
        
    def save_config(self):
        config = {
            "input_image": self.image_path.get(),
            "total_frames": int(self.frames_entry.get()),
            "max_squish_percent": float(self.squish_entry.get()),
            "output_folder": "output_frames",
            
            # Chaos parameters
            "frame_jitter": int(self.jitter_entry.get()),
            "energy_noise": int(self.noise_entry.get()),
            "use_forward_energy": self.forward_energy_var.get(),
            
            "convert_to_video": self.convert_to_video.get(),
            "video_framerate": int(self.video_framerate.get()),
            "video_quality": self.video_quality.get()
        }
        
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
            
        self.log(f"Config saved")
        return config
        
    def check_ffmpeg(self):
        try:
            result = subprocess.run(["ffmpeg", "-version"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, 
                                  text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
            
    def convert_frames_to_video(self):
        if not os.path.exists("output_frames"):
            messagebox.showerror("Error", "No frames found in 'output_frames' folder!\nGenerate frames first.")
            return
            
        thread = threading.Thread(target=self._run_video_conversion, daemon=True)
        thread.start()
        
    def _run_video_conversion(self):
        try:
            self.log("=" * 60)
            self.log("Starting video conversion...")
            
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                output_folder = config.get("output_folder", "output_frames")
                self.log(f"Reading frames from: {output_folder}")
            else:
                output_folder = "output_frames"
                self.log("config.json not found, using default: output_frames")
            
            if not os.path.exists(output_folder):
                self.log(f"ERROR: Folder '{output_folder}' not found!", "ERROR")
                self.root.after(0, lambda: messagebox.showerror("Error", 
                    f"No frames found in '{output_folder}' folder!\nGenerate frames first."))
                return
            
            frame_files = [f for f in os.listdir(output_folder) if f.startswith("frame_") and f.endswith(".png")]
            if not frame_files:
                self.log(f"ERROR: No frame files found in {output_folder}!", "ERROR")
                self.root.after(0, lambda: messagebox.showerror("Error", 
                    f"No frame files (frame_*.png) found in '{output_folder}'!"))
                return
            
            self.log(f"Found {len(frame_files)} frames in {output_folder}")
            
            fps = int(self.video_framerate.get())
            quality = self.video_quality.get()
            
            quality_map = {
                "high": "18",
                "medium": "23",
                "low": "28"
            }
            crf = quality_map[quality]
            
            base_name = "output_video"
            ext = ".mp4"
            num = ""
            output_file = f"{base_name}{ext}"
            
            while os.path.exists(output_file):
                if num == "":
                    num = 1
                else:
                    num += 1
                output_file = f"{base_name}{num}{ext}"
            
            input_pattern = os.path.join(output_folder, "frame_%04d.png")
            
            cmd = [
                "ffmpeg", "-y",
                "-framerate", str(fps),
                "-i", input_pattern,
                "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                "-c:v", "libx264",
                "-crf", crf,
                "-pix_fmt", "yuv420p",
                output_file
            ]
            
            self.log(f"FFmpeg command: {' '.join(cmd)}")
            self.log(f"Input: {input_pattern}")
            self.log(f"Output: {output_file}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            for line in process.stdout:
                if "frame=" in line and "fps=" in line and "time=" in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith("time="):
                            time_str = part.split("=")[1]
                            self.log(f"Converting... {time_str}", "INFO")
                            break
                elif "Output file" in line:
                    self.log(line.strip())
                    
            process.wait()
            
            if process.returncode == 0:
                self.log(f"Video created: {output_file}", "SUCCESS")
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                    f"Video created successfully!\n\n{output_file}"))
            else:
                self.log(f"Video conversion failed", "ERROR")
                self.root.after(0, lambda: messagebox.showerror("Error", 
                    "Video conversion failed!\nCheck log for details."))
                
        except Exception as e:
            self.log(f"Error: {str(e)}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            
    def run_processing(self):
        """Run processing in a separate thread"""
        try:
            self.log("=" * 60)
            self.log("Starting frame generation...")
            
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                output_folder = config.get("output_folder", "output_frames")
            else:
                output_folder = "output_frames"
            
            self.log(f"Output folder: {output_folder}")
            
            # Run frame-generator.py and capture output
            process = subprocess.Popen(
                [sys.executable, "frame-generator.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )
            
            # Read output line by line in real-time
            for line in process.stdout:
                if line.strip():
                    self.log(line.strip())
                    
            process.wait()
            
            # In run_processing() method, replace the summary section with this:

            if process.returncode == 0:
                self.log("Frame generation completed!", "SUCCESS")
                
                # Read summary from config
                summary_text = f"Processing completed!\n\nFrames saved in: {output_folder}"
                
                try:
                    with open("config.json", "r", encoding="utf-8") as f:
                        config = json.load(f)
                    summary = config.get("processing_summary", {})
                    
                    if summary:
                        summary_text = (
                            "=======================================\n"
                            "        PROCESSING COMPLETE!\n"
                            "=======================================\n\n"
                            f"  Total Frames:      {summary.get('total_frames', 'N/A')}\n"
                            f"  Total Time:        {summary.get('total_time_seconds', 'N/A')} s\n"
                            f"                     ({summary.get('total_time_minutes', 'N/A')} min)\n"
                            f"  Avg per Frame:     {summary.get('average_time_per_frame', 'N/A')} s\n"
                            f"  Fastest Frame:     {summary.get('fastest_frame', 'N/A')} s\n"
                            f"  Slowest Frame:     {summary.get('slowest_frame', 'N/A')} s\n\n"
                            "--------------------------------------------------\n"
                            f"  Output Folder:\n"
                            f"  {summary.get('output_folder', 'N/A')}\n"
                            "=======================================\n\n"
                            
                        )
                except Exception as e:
                    self.log(f"Could not read summary: {e}", "WARNING")
                
                # Auto-convert to video if checkbox is checked
                if self.convert_to_video.get():
                    self.log("\n" + "=" * 60)
                    self.log("Auto-converting to video...")
                    self._run_video_conversion()
                
                # Show success popup with summary
                self.root.after(0, lambda: messagebox.showinfo("Meme Generator", summary_text))
                
        except Exception as e:
            self.log(f"Error: {str(e)}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.is_processing = False
            self.root.after(0, self.reset_ui)
        
    def start_processing(self):
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing is already running!")
            return
            
        if not self.validate_inputs():
            return
            
        if self.convert_to_video.get():
            if not self.check_ffmpeg():
                response = messagebox.askyesno("FFmpeg Not Found", 
                    "FFmpeg is not installed or not in PATH.\n\n"
                    "Do you want to continue without video conversion?\n\n"
                    "Install FFmpeg from: https://ffmpeg.org/download.html")
                if response:
                    self.convert_to_video.set(False)
                    self.toggle_video_options()
                else:
                    return
            
        config = self.save_config()
        
        self.is_processing = True
        self.start_btn.config(state=tk.DISABLED, text="Processing...")
        self.status_label.config(text="Processing...", fg="blue")
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.run_processing, daemon=True)
        thread.start()
        
    def reset_ui(self):
        self.start_btn.config(state=tk.NORMAL, text="Start Processing")
        self.status_label.config(text="Ready", fg="green")
        
    def log(self, message, level="INFO"):
        def append_log():
            self.log_text.config(state=tk.NORMAL)
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        self.root.after(0, append_log)
        
    def on_closing(self):
        if self.is_processing:
            if messagebox.askokcancel("Quit", "Processing is running. Do you want to quit?"):
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = SeamCarvingGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()