#!/usr/bin/env python3
"""
🤖 Rescue Robot - WebRTC Video File Streamer (OpenCV Custom Track)
Pipeline:
  1. [COMPONENT A] sample.mp4 → OpenCV VideoCapture (Parser/Demuxer)
  2. [COMPONENT B] VideoFileStreamTrack → frames → aiortc encoder → H.264 CBP
  3. [COMPONENT C] RTCPeerConnection → ICE → E2E Tunnel → Browser
"""

import os
import sys
import time
import json
import asyncio
import subprocess
import fractions

# ========================================================================
# Self-healing dependency check
# ========================================================================
def check_dependencies():
    required = {"aiortc": "aiortc", "websockets": "websockets", "av": "av", "cv2": "opencv-python"}
    missing = []
    for mod, pip_name in required.items():
        try:
            __import__(mod)
        except ImportError:
            missing.append(pip_name)
    if missing:
        print(f"[Setup] Installing missing packages: {missing}")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing, check=True)

check_dependencies()

import av
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
import websockets

SIGNALING_URL = "ws://localhost:8080/ws/webrtc?role=sender"

# ========================================================================
# 🧩 [COMPONENT A] - Video File Parser (OpenCV Demuxer)
# ========================================================================
class VideoFileParser:
    """Opens and parses an MP4 file, extracting metadata and providing frame access."""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.cap = None
        self.fps = 25.0
        self.width = 0
        self.height = 0
        self.total_frames = 0
        self.codec_info = ""
        
    def open(self):
        """Open video container and extract metadata."""
        print(f"\n[Parser] Opening video container: {self.filepath}")
        self.cap = cv2.VideoCapture(self.filepath)
        if not self.cap.isOpened():
            print(f"[Parser ERROR] Failed to open: {self.filepath}")
            return False
            
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc_int = int(self.cap.get(cv2.CAP_PROP_FOURCC))
        self.codec_info = "".join([chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4)])
        
        print(f"[Parser] ✓ Codec: {self.codec_info}")
        print(f"[Parser] ✓ Resolution: {self.width}x{self.height}")
        print(f"[Parser] ✓ FPS: {self.fps}")
        print(f"[Parser] ✓ Total Frames: {self.total_frames}")
        return True
        
    def read_frame(self):
        """Read next BGR frame from the container. Returns None at EOF (loops)."""
        if self.cap is None:
            return None
        ret, frame = self.cap.read()
        if not ret:
            # Loop: rewind to beginning
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                return None
        return frame
        
    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None


# ========================================================================
# 🚀 [COMPONENT B] - WebRTC Video Stream Track (Frame Producer)
# ========================================================================
class VideoFileStreamTrack(MediaStreamTrack):
    """
    Custom MediaStreamTrack that reads frames from VideoFileParser.
    aiortc's internal encoder will automatically re-encode to H.264 CBP
    (Constrained Baseline Profile) for browser compatibility.
    """
    kind = "video"
    
    def __init__(self, parser: VideoFileParser):
        super().__init__()
        self.parser = parser
        self._timestamp = 0
        self._frame_duration = int(90000 / parser.fps)  # RTP clock = 90kHz
        self._frame_count = 0
        self._start_time = time.time()
        self._total_prep_time = 0.0  # cumulative frame preparation time
        print(f"[Track] VideoFileStreamTrack initialized @ {parser.fps} FPS")
        
    async def recv(self):
        """Called by aiortc to get the next video frame."""
        # Pace frame delivery to match source FPS
        pts = self._timestamp
        self._timestamp += self._frame_duration
        
        # Wait until it's time for this frame
        target_time = self._start_time + (self._frame_count / self.parser.fps)
        now = time.time()
        wait = target_time - now
        if wait > 0:
            await asyncio.sleep(wait)
        
        # Measure frame preparation time (read + convert)
        t0 = time.perf_counter()
        
        # Read raw BGR frame from parser
        bgr_frame = self.parser.read_frame()
        if bgr_frame is None:
            # Return a black frame as a fallback
            bgr_frame = np.zeros((self.parser.height, self.parser.width, 3), dtype=np.uint8)
        
        # Convert BGR → YUV420P VideoFrame (what aiortc encoder expects)
        frame = av.VideoFrame.from_ndarray(bgr_frame, format="bgr24")
        frame.pts = pts
        frame.time_base = fractions.Fraction(1, 90000)
        
        prep_ms = (time.perf_counter() - t0) * 1000
        self._total_prep_time += prep_ms
        
        self._frame_count += 1
        if self._frame_count % 100 == 0:
            elapsed = time.time() - self._start_time
            actual_fps = self._frame_count / elapsed if elapsed > 0 else 0
            avg_prep = self._total_prep_time / self._frame_count
            print(f"[Track] Sent {self._frame_count} frames | FPS: {actual_fps:.1f} | Avg prep: {avg_prep:.2f}ms/frame")
        
        return frame


# ========================================================================
# 🔄 [COMPONENT C] - Main WebRTC Signaling & Connection Loop
# ========================================================================
async def run_sender(video_source):
    print("=" * 66)
    print("[WebRTC] Rescue Robot - Video File Streamer (OpenCV Track)")
    print(f"Video Source: {video_source}")
    print(f"Pipeline: OpenCV Decode → YUV420P Frame → aiortc H.264 CBP Encode → WebRTC")
    print(f"Signaling: {SIGNALING_URL}")
    print("=" * 66)

    parser = None
    track = None
    pc = None
    
    async def cleanup():
        nonlocal pc, track, parser
        if pc is not None:
            print("[Cleanup] Closing PeerConnection...")
            try:
                await pc.close()
            except Exception:
                pass
            pc = None
        if track is not None:
            try:
                track.stop()
            except Exception:
                pass
            track = None
        if parser is not None:
            print("[Cleanup] Releasing video file handle...")
            parser.release()
            parser = None
        await asyncio.sleep(0.2)
    
    while True:
        try:
            print(f"\n[WebSocket] Connecting to signaling server...")
            async with websockets.connect(SIGNALING_URL) as ws:
                print("[WebSocket] ✓ Connected! Waiting for React UI 'ready' signal...")
                
                async for message in ws:
                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError:
                        continue
                    
                    msg_type = data.get("type")
                    
                    if msg_type == "ready":
                        print("\n[Signal] 📡 React UI joined! Starting WebRTC negotiation...")
                        await cleanup()
                        
                        # === COMPONENT A: Parse video file ===
                        parser = VideoFileParser(video_source)
                        if not parser.open():
                            print("[ERROR] Failed to parse video. Aborting negotiation.")
                            await cleanup()
                            continue
                        
                        # === COMPONENT B: Create video track ===
                        track = VideoFileStreamTrack(parser)
                        
                        # === COMPONENT C: Create PeerConnection & negotiate ===
                        pc = RTCPeerConnection()
                        
                        # Monitor ICE state for diagnostics
                        @pc.on("iceconnectionstatechange")
                        async def on_ice_state():
                            state = pc.iceConnectionState
                            print(f"[ICE] State → {state}")
                            if state == "connected":
                                print("[ICE] ✓ P2P media tunnel ACTIVE! Frames are flowing to browser.")
                            elif state == "failed":
                                print("[ICE] ✗ ICE negotiation FAILED. Check firewall/network.")
                        
                        @pc.on("connectionstatechange")
                        async def on_conn_state():
                            print(f"[CONN] State → {pc.connectionState}")
                        
                        pc.addTrack(track)
                        print("[Sender] ✓ Video track loaded onto PeerConnection")
                        
                        # Create and send offer
                        offer = await pc.createOffer()
                        await pc.setLocalDescription(offer)
                        
                        # Wait for ICE gathering to complete
                        print("[ICE] Gathering candidates...")
                        gather_start = time.time()
                        while pc.iceGatheringState != "complete":
                            await asyncio.sleep(0.05)
                            if time.time() - gather_start > 10:
                                print("[ICE] WARNING: Gathering timeout (10s). Sending partial candidates.")
                                break
                        print(f"[ICE] ✓ Candidates gathered in {time.time()-gather_start:.2f}s")
                        
                        # Dispatch offer to browser via Go relay
                        offer_payload = {
                            "type": "offer",
                            "sdp": pc.localDescription.sdp
                        }
                        await ws.send(json.dumps(offer_payload))
                        print("[Signal] ✓ SDP Offer dispatched to browser")
                        
                    elif msg_type == "answer":
                        if pc is None:
                            print("[Signal] WARNING: Received answer but no active PeerConnection")
                            continue
                        print("[Signal] SDP Answer received from browser. Finalizing...")
                        answer = RTCSessionDescription(sdp=data["sdp"], type="answer")
                        await pc.setRemoteDescription(answer)
                        print("[Signal] ✓ Remote description set. E2E tunnel negotiation complete!")
                        print("[Signal] ✓ Waiting for ICE connectivity check to succeed...")
                        
                    elif msg_type == "bye":
                        print("[Signal] Receiver sent 'bye'. Tearing down connection.")
                        await cleanup()
                        
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
            print(f"[WebSocket] Connection lost: {e}. Retrying in 3s...")
            await cleanup()
            await asyncio.sleep(3.0)
        except Exception as e:
            print(f"[ERROR] Unexpected: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            await cleanup()
            await asyncio.sleep(3.0)
    
    await cleanup()


# ========================================================================
# Entry Point
# ========================================================================
if __name__ == "__main__":
    video_source = None
    if len(sys.argv) > 1:
        video_source = sys.argv[1]
    else:
        mp4_files = [f for f in os.listdir('.') if f.endswith('.mp4')]
        if mp4_files:
            video_source = mp4_files[0]
            print(f"[Setup] Auto-detected video file: {video_source}")
        else:
            print("[ERROR] No .mp4 file found in current directory.")
            print("[ERROR] Usage: python send_video_file_webrtc.py <video_file.mp4>")
            sys.exit(1)
    
    if not os.path.exists(video_source):
        print(f"[ERROR] File not found: {video_source}")
        sys.exit(1)
    
    try:
        asyncio.run(run_sender(video_source))
    except KeyboardInterrupt:
        print("\n[Streamer] Stopped by operator (Ctrl+C).")
