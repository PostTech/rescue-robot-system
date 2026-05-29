#!/usr/bin/env python3
"""
🤖 Rescue Robot - WebRTC H.264/VP8 Video File Streamer
Reads any local video file (e.g., .mp4), compresses it, and streams it
in an infinite seamless loop to the Go Backend signaling relay.
"""

import os
import sys
import time
import json
import asyncio
import subprocess

# 1. Self-healing dependency check and auto-installation
def check_dependencies():
    required_packages = {
        "cv2": "opencv-python",
        "numpy": "numpy",
        "aiortc": "aiortc",
        "websockets": "websockets",
    }
    
    missing_packages = []
    for module_name, pip_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(pip_name)
            
    if missing_packages:
        print(f"[WebRTC Streamer] Missing required packages: {missing_packages}. Installing automatically...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
            print("[WebRTC Streamer] All dependencies installed successfully!")
        except Exception as e:
            print(f"[WebRTC Streamer] Failed to auto-install dependencies: {e}")
            print(f"[WebRTC Streamer] Please run: pip install {' '.join(missing_packages)}")
            sys.exit(1)

check_dependencies()

# Core dependencies are now guaranteed to be imported successfully
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from av import VideoFrame
import fractions
import websockets

SIGNALING_URL = "ws://localhost:8080/ws/webrtc?role=sender"

class VideoFileStreamTrack(MediaStreamTrack):
    """
    Custom MediaStreamTrack that decodes frames from an OpenCV VideoCapture (file)
    and loops infinitely.
    """
    kind = "video"

    def __init__(self, cap, video_path):
        super().__init__()
        self.cap = cap
        self.video_path = video_path
        self.time_base = fractions.Fraction(1, 90000)
        self.pts = 0
        
        # Read native properties
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps = fps if (0 < fps <= 60) else 25.0
        print(f"[Track] Successfully loaded video file: {self.video_path}")
        print(f"[Track] Operating at native Video FPS: {self.fps:.1f}")

    async def recv(self):
        pts, time_base = self.pts, self.time_base
        
        ret, frame = self.cap.read()
        if not ret:
            # Reached end of video file, rewind and loop seamlessly!
            print("\n[Track] Reached end of video file. Rewinding and looping...")
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                # If still fails, generate dynamic diagnostic pattern as fallback
                frame = self._generate_diagnostic_frame()

        # Scale down for efficient low-bandwidth WebRTC transmission
        # Dashboard standard width is 480px
        h, w = frame.shape[:2]
        target_w = 480
        target_h = int(h * (target_w / w))
        frame = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)

        # Convert OpenCV BGR frame (numpy array) to PyAV VideoFrame and reformat to YUV420P
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        yuv_frame = video_frame.reformat(format="yuv420p")
        yuv_frame.pts = pts
        yuv_frame.time_base = time_base
        
        # Increment PTS based on FPS (90000 time base increments per second)
        self.pts += int(90000 / self.fps)
        
        # Pace the stream to match Target FPS exactly
        await asyncio.sleep(1.0 / self.fps)
        
        return yuv_frame

    def _generate_diagnostic_frame(self):
        """Dynamic tech matrix fallback pattern if video file read fails completely"""
        img = np.zeros((320, 480, 3), dtype=np.uint8)
        for x in range(0, 480, 40):
            cv2.line(img, (x, 0), (x, 320), (15, 20, 25), 1)
        for y in range(0, 320, 40):
            cv2.line(img, (0, y), (480, y), (15, 20, 25), 1)
        t = time.time()
        cv2.putText(img, "RESCUE ROBOT - VIDEO STREAM ERROR", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        return img

async def run_sender(video_source):
    print("==================================================================")
    print("[WebRTC] Rescue Robot - Compressed Video File Streamer Initializing...")
    print(f"Video Source: {video_source}")
    print(f"Signaling Relay: {SIGNALING_URL}")
    print("==================================================================")

    # Store active PeerConnection, track, and video capture
    cap = None
    pc = None
    track = None
    
    async def cleanup_webrtc():
        nonlocal pc, track, cap
        if pc is not None:
            print("[WebRTC] Closing active peer connection...")
            try:
                await pc.close()
            except Exception:
                pass
            pc = None
        if track is not None:
            track = None
        if cap is not None:
            print("[WebRTC] Releasing video file capture...")
            try:
                cap.release()
            except Exception:
                pass
            cap = None
        # Allow async loops to settle connection states before recreating
        await asyncio.sleep(0.3)
            
    while True:
        try:
            print(f"[WebSocket] Connecting to signaling server...")
            async with websockets.connect(SIGNALING_URL) as ws:
                print("[WebSocket] Connected successfully! Standing by for React UI to request feed...")
                
                async for message in ws:
                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError:
                        continue
                        
                    msg_type = data.get("type")
                    
                    if msg_type == "ready":
                        print("\n[Signaling] React Control UI joined! Starting new WebRTC E2E stream negotiation...")
                        await cleanup_webrtc()
                        
                        # Open video file dynamically when receiver joins
                        print(f"[WebRTC] Opening video file: {video_source}")
                        cap = cv2.VideoCapture(video_source)
                        if not cap.isOpened():
                            print(f"[WebRTC Error] Failed to open video file: {video_source}")
                            await cleanup_webrtc()
                            continue
                        
                        # Create new PeerConnection
                        pc = RTCPeerConnection()
                        
                        # Instantiate track and attach to connection
                        track = VideoFileStreamTrack(cap, video_source)
                        pc.addTrack(track)
                        
                        # Create Offer
                        offer = await pc.createOffer()
                        await pc.setLocalDescription(offer)
                        
                        # Wait for complete ICE gathering before sending (Non-Trickle approach)
                        print("[WebRTC] Gathering ICE candidates...")
                        while pc.iceGatheringState != "complete":
                            await asyncio.sleep(0.05)
                        print("[WebRTC] ICE candidates gathered successfully.")
                        
                        # Dispatch SDP Offer to React UI
                        offer_payload = {
                            "type": "offer",
                            "sdp": pc.localDescription.sdp
                        }
                        await ws.send(json.dumps(offer_payload))
                        print("[Signaling] SDP Offer successfully dispatched to receiver.")
                        
                    elif msg_type == "answer":
                        if pc is None:
                            continue
                        print("[Signaling] SDP Answer received from receiver. Finalizing connection...")
                        answer = RTCSessionDescription(sdp=data["sdp"], type="answer")
                        await pc.setRemoteDescription(answer)
                        print("[WebRTC] E2E media tunnel successfully negotiated and opened!")
                        
                    elif msg_type == "bye":
                        print("[Signaling] Receiver dispatched 'bye' signal. Tearing down connection.")
                        await cleanup_webrtc()
                        
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
            print(f"[WebSocket Error] Lost connection to Go backend: {e}. Reconnecting in 3 seconds...")
            await cleanup_webrtc()
            await asyncio.sleep(3.0)
        except Exception as e:
            print(f"[Unexpected Error] {e}")
            await cleanup_webrtc()
            await asyncio.sleep(3.0)
            
    # Release camera on exit
    if cap is not None:
        cap.release()

import urllib.request

def download_sample_video(target_path):
    url = "https://www.w3schools.com/html/mov_bbb.mp4"
    print(f"[WebRTC] No local MP4 file found. Automatically downloading a lightweight public sample video (Big Buck Bunny)...")
    print(f"Source URL: {url}")
    print("Please wait a moment (under 1MB)...")
    try:
        urllib.request.urlretrieve(url, target_path)
        print(f"[WebRTC] Successfully downloaded sample video to: {target_path}")
        return True
    except Exception as e:
        print(f"[WebRTC Error] Failed to download sample video: {e}")
        return False

if __name__ == "__main__":
    # 1. Parse arguments for video source
    video_source = None
    if len(sys.argv) > 1:
        video_source = sys.argv[1]
    else:
        # Search for any mp4 files in the current root directory
        mp4_files = [f for f in os.listdir('.') if f.endswith('.mp4')]
        if mp4_files:
            video_source = mp4_files[0]
            print(f"[WebRTC] Auto-detected local video file: {video_source}")
        else:
            video_source = "sample.mp4"
            if not os.path.exists(video_source):
                success = download_sample_video(video_source)
                if not success:
                    print("[Error] Failed to acquire a video source. Exiting.")
                    sys.exit(1)
            else:
                print(f"[WebRTC] Using cached sample video: {video_source}")
            
    if not os.path.exists(video_source):
        print(f"[Error] The specified video file does not exist: {video_source}")
        sys.exit(1)

    try:
        asyncio.run(run_sender(video_source))
    except KeyboardInterrupt:
        print("\n[Streamer] Closed by Operator (Ctrl+C). Exiting.")
