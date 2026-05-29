#!/usr/bin/env python3
"""Script to stream a real video file or webcam feed to the Go backend WebSocket server.

Extracts frames from any video file (e.g., .mp4, .avi) or local webcam,
encodes them as base64 JPEGs, and broadcasts them through the Go core API.
"""

import os
import sys
import time
import base64
import urllib.request
import urllib.error
import json
import subprocess

# Self-healing package checks
def check_dependencies():
    required_packages = {
        "cv2": "opencv-python",
    }
    
    for module_name, pip_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            print(f"[Video Streamer] '{pip_name}' is not installed. Installing automatically...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", pip_name], check=True)
                print(f"[Video Streamer] '{pip_name}' installed successfully!")
            except Exception as e:
                print(f"[Video Streamer] Failed to auto-install '{pip_name}': {e}")
                print(f"[Video Streamer] Please run 'pip install {pip_name}' manually.")
                sys.exit(1)

# Check dependencies before proceeding
check_dependencies()

import cv2

SERVER_URL = "http://localhost:8080/api/demo/send-frame"

def main():
    print("==================================================================")
    print("🤖 Rescue Robot - Real Video / Camera Streamer")
    print("==================================================================")
    
    # 1. Parse arguments for video source
    video_source = None
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        # Check if argument is integer (webcam index)
        if arg.isdigit():
            video_source = int(arg)
            print(f"[Source] Selected Webcam Index: {video_source}")
        elif arg.lower() in ["webcam", "camera", "cam"]:
            video_source = 0
            print(f"[Source] Selected Default Webcam")
        else:
            video_source = arg
            if not os.path.exists(video_source):
                print(f"[Error] The specified video file does not exist: {video_source}")
                print("Please provide a valid file path or specify 'webcam' to stream camera feed.")
                sys.exit(1)
            print(f"[Source] Selected Video File: {video_source}")
    else:
        # Default fallback or instructions
        print("Usage:")
        print("  python send_video_file.py <path_to_video.mp4>  - Stream a video file")
        print("  python send_video_file.py webcam               - Stream from default camera")
        print("\nSearching for any video file in the current directory...")
        
        # Search for mp4 files
        mp4_files = [f for f in os.listdir('.') if f.endswith('.mp4')]
        if mp4_files:
            video_source = mp4_files[0]
            print(f"[Source] Auto-detected video file in root: {video_source}")
        else:
            print("[Warning] No video files (.mp4) found in the root directory.")
            print("[Fallback] Falling back to default webcam (0).")
            video_source = 0

    print(f"Target Server: {SERVER_URL}")
    print("Press Ctrl+C to stop the stream.")
    print("------------------------------------------------------------------")

    # 2. Open Video Capture
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print(f"[Error] Failed to open video source: {video_source}")
        sys.exit(1)

    # Read properties for pacing
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or fps > 60:
        fps = 15.0  # default fallback
    
    delay = 1.0 / fps
    print(f"[Stream Info] Native FPS: {fps:.1f} (Frame interval: {delay*1000:.1f}ms)")

    frame_count = 0
    start_time = time.time()

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                # If it's a video file, loop it for infinite playback convenience
                if isinstance(video_source, str):
                    print("\n[Stream] Reached end of video file. Rewinding and looping...")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    print("\n[Stream] Connection to camera lost.")
                    break

            frame_count += 1

            # 3. Downscale frame for ultra-low latency WebSocket transmission
            # Thermal dashboard standard resolution is compact (e.g. width=400px)
            h, w = frame.shape[:2]
            target_w = 400
            target_h = int(h * (target_w / w))
            resized_frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)

            # 4. Encode to JPG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70] # 70% quality for optimal compression
            result, encimg = cv2.imencode('.jpg', resized_frame, encode_param)
            if not result:
                continue

            # 5. Base64 encoding
            base64_data = base64.b64encode(encimg).decode('utf-8')

            # 6. Dispatch HTTP POST request to Go core endpoint
            payload = {
                "frame_data": base64_data,
                "sensor_type": "RGB" if not isinstance(video_source, int) else "THERMAL",
                "timestamp_ms": int(time.time() * 1000)
            }
            json_payload = json.dumps(payload).encode('utf-8')

            req = urllib.request.Request(
                SERVER_URL,
                data=json_payload,
                headers={"Content-Type": "application/json"}
            )

            try:
                with urllib.request.urlopen(req) as response:
                    response.read()
                    elapsed = time.time() - start_time
                    current_fps = frame_count / elapsed if elapsed > 0 else 0
                    print(f"\r[Stream] Dispatched Frame #{frame_count:05d} | Target: {video_source} | Stream FPS: {current_fps:.1f}", end="")
            except urllib.error.URLError as ue:
                print(f"\n[Stream Error] Dispatch failed. Is Go Backend server online at 8080? ({ue.reason})")
                time.sleep(2.0)
                continue

            # Pacing delay to match source FPS
            time.sleep(delay)

    except KeyboardInterrupt:
        print("\n\n[Stream] Stopped by operator (Ctrl+C).")
    finally:
        cap.release()
        print("==================================================================")

if __name__ == "__main__":
    main()
