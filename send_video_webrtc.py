#!/usr/bin/env python3
"""
🤖 Rescue Robot - WebRTC H.264/VP8 Compressed Video Streamer
Streams video from local webcam (or dynamic diagnostic fallback pattern)
to the Go Backend signaling relay.
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
            # Execute pip install
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

class WebcamVideoStreamTrack(MediaStreamTrack):
    """
    Custom MediaStreamTrack that grabs frames from OpenCV VideoCapture
    or falls back to a high-fidelity synthetic glowing dynamic visual diagnostic screen.
    """
    kind = "video"

    def __init__(self, cap):
        super().__init__()
        self.cap = cap
        self.time_base = fractions.Fraction(1, 90000)
        self.pts = 0
        self.consecutive_failures = 0
        
        # Test if cap is open
        if self.cap is not None and self.cap.isOpened():
            self.has_camera = True
            # Read native FPS if possible
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.fps = fps if (0 < fps <= 60) else 30.0
            print(f"[Track] Physical camera detected. Operating at {self.fps} native FPS.")
        else:
            self.has_camera = False
            self.fps = 30.0
            print("[Track] No camera detected or camera failed to open. Initializing premium dynamic visual diagnostic pattern fallback.")

    async def recv(self):
        pts, time_base = self.pts, self.time_base
        
        frame = None
        if self.has_camera and self.cap is not None:
            ret, frame = self.cap.read()
            if not ret:
                self.consecutive_failures += 1
                if self.consecutive_failures > 30:
                    print("[Track] Consecutive frame capture failures. Swapping to diagnostic fallback...")
                    self.has_camera = False
            else:
                self.consecutive_failures = 0

        if frame is None:
            frame = self._generate_diagnostic_frame()

        # Scale down for efficient low-bandwidth H.264/VP8 transmission
        # SOPPanel standard size is optimized at 480x320 width
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
        # 90000 / 30 FPS = 3000 increments per frame
        self.pts += int(90000 / self.fps)
        
        # Pace the stream to match Target FPS (e.g. 30 FPS -> 33ms sleep)
        await asyncio.sleep(1.0 / self.fps)
        
        return yuv_frame

    def _generate_diagnostic_frame(self):
        """
        Generates a state-of-the-art diagnostic dynamic synthetic screen with
        neon cyan glowing circles, sweeping radar sweep lines, and a real-time timestamp counter.
        """
        img = np.zeros((320, 480, 3), dtype=np.uint8)
        
        # Draw tech matrix background grid lines
        for x in range(0, 480, 40):
            cv2.line(img, (x, 0), (x, 320), (15, 20, 25), 1)
        for y in range(0, 320, 40):
            cv2.line(img, (0, y), (480, y), (15, 20, 25), 1)
            
        t = time.time()
        
        # Draw pulsing concentric rings in neon cyan
        center_x, center_y = 240, 160
        pulse_val = np.sin(t * 4)
        for offset in [0, 40, 80]:
            radius = int(50 + offset + 8 * pulse_val)
            cv2.circle(img, (center_x, center_y), radius, (235, 206, 0), 1) # Cyan BGR (235, 206, 0)
            
        # Draw center target crosshairs
        cv2.line(img, (center_x - 15, center_y), (center_x + 15, center_y), (0, 0, 255), 1)
        cv2.line(img, (center_x, center_y - 15), (center_x, center_y + 15), (0, 0, 255), 1)
        cv2.circle(img, (center_x, center_y), 4, (0, 0, 255), -1)
        
        # Sweeping radar green beam
        scan_angle = t * 2.0
        end_x = int(center_x + 130 * np.cos(scan_angle))
        end_y = int(center_y + 130 * np.sin(scan_angle))
        cv2.line(img, (center_x, center_y), (end_x, end_y), (0, 255, 0), 2)
        
        # Header Info Card
        cv2.putText(img, "RESCUE ROBOT - CAM SYNC OVERRIDE", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, "MODE: WEBRTC COMPRESSED H.264/VP8", (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 220, 255), 1, cv2.LINE_AA)
        
        # Connection status pulsating dot
        dot_color = (0, 0, 255) if int(t * 2) % 2 == 0 else (0, 75, 150) # pulsates red
        cv2.circle(img, (25, 75), 4, dot_color, -1)
        cv2.putText(img, "EMULATED SENSOR ACTIVE (NO CAMERA DETECTED)", (38, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (180, 180, 180), 1, cv2.LINE_AA)
        
        # Bottom real-time timestamp display
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ms_str = f"{(t % 1) * 1000:03.0f}"
        cv2.putText(img, f"RTC TIME: {time_str}.{ms_str} UTC+9", (20, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (120, 130, 140), 1, cv2.LINE_AA)
        cv2.putText(img, f"BANDWIDTH RESCUE PRESET: 30 FPS / 480p", (20, 298), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 128), 1, cv2.LINE_AA)
        
        return img

async def run_sender():
    print("==================================================================")
    print("[WebRTC] Rescue Robot - Compressed Video Streamer Initializing...")
    print(f"Signaling Relay: {SIGNALING_URL}")
    print("==================================================================")

    # Store active PeerConnection, track, and camera capture
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
            print("[WebRTC] Releasing physical webcam...")
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
                        print(f"[WebSocket] Received non-JSON message: {message}")
                        continue
                        
                    msg_type = data.get("type")
                    
                    if msg_type == "ready":
                        print("\n[Signaling] React Control UI joined! Starting new WebRTC E2E stream negotiation...")
                        await cleanup_webrtc()
                        
                        # Open camera dynamically when receiver joins
                        print("[WebRTC] Initializing physical webcam camera index 0...")
                        cap = cv2.VideoCapture(0)
                        
                        # Create new PeerConnection
                        pc = RTCPeerConnection()
                        
                        # Instantiate track and attach to connection
                        track = WebcamVideoStreamTrack(cap)
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
                            print("[Signaling Warning] Received SDP Answer but no active PeerConnection exists. Skipping.")
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

if __name__ == "__main__":
    try:
        asyncio.run(run_sender())
    except KeyboardInterrupt:
        print("\n[Streamer] Closed by Operator (Ctrl+C). Exiting.")
