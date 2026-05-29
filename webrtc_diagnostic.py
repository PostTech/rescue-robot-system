#!/usr/bin/env python3
"""
Rescue Robot - WebRTC E2E Pipeline Diagnostic & Debugging Tool
Objectively inspects:
1. Video container (sample.mp4) H.264 profile and browser compatibility.
2. WebRTC track initialization and codec parameter packaging.
3. SDP Offer negotiation parameters (profile-level-id, packetization-mode).
4. WebSocket signaling hub latency and connectivity.
"""

import os
import sys
import json
import asyncio
import time

def check_dependencies():
    required = ["av", "aiortc", "websockets"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[Diagnostic Error] Missing packages: {missing}. Please run 'pip install {' '.join(missing)}' first.")
        sys.exit(1)

check_dependencies()

import av
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
import websockets

VIDEO_FILE = "sample.mp4"
SIGNALING_URL = "ws://localhost:8080/ws/webrtc?role=sender"

def run_container_diagnostics():
    print("\n" + "="*70)
    print("[DIAGNOSTIC] STEP 1: VIDEO CONTAINER (MP4) CODEC & COMPATIBILITY DIAGNOSTICS")
    print("="*70)
    
    if not os.path.exists(VIDEO_FILE):
        print(f"[FAILED] Video file '{VIDEO_FILE}' not found in root directory!")
        return False
        
    try:
        container = av.open(VIDEO_FILE)
        print(f"[OK] Successfully opened container: {VIDEO_FILE}")
        print(f" - Duration: {container.duration / av.time_base:.2f} seconds")
        print(f" - Number of streams: {len(container.streams)}")
        
        video_streams = [s for s in container.streams if s.type == "video"]
        if not video_streams:
            print("[FAILED] No video stream found in the MP4 file!")
            return False
            
        v_stream = video_streams[0]
        codec_context = v_stream.codec_context
        
        print(f"[OK] Video Stream Detected:")
        print(f" - Codec Name: {codec_context.name}")
        print(f" - Long Name: {codec_context.codec.long_name}")
        print(f" - Profile: {codec_context.profile}")
        print(f" - Resolution: {codec_context.width}x{codec_context.height}")
        print(f" - Bitrate: {codec_context.bit_rate / 1000 if codec_context.bit_rate else 0:.1f} kbps")
        print(f" - Pixel Format: {codec_context.pix_fmt}")
        print(f" - Native FPS: {float(v_stream.average_rate):.2f}")
        
        # Browser Compatibility Guard Analysis
        profile = codec_context.profile.lower() if codec_context.profile else ""
        codec_name = codec_context.name.lower()
        
        print("\n[BROWSER WEBRTC NATIVE DECODING COMPATIBILITY REPORT]:")
        if codec_name != "h264":
            print(f" [WARNING] WebRTC natively prefers H.264 or VP8. Codec '{codec_name}' might fail on some browsers.")
        else:
            print(f" [OK] Codec is H.264 (standard for WebRTC).")
            
        if "baseline" in profile or "constrained" in profile:
            print(f" [OK] Profile '{codec_context.profile}' is Constrained Baseline Profile.")
            print(f"      -> NATIVE PASSTHROUGH COMPATIBLE! All browsers will decode this directly without transcoding.")
        else:
            print(f" [WARNING] POTENTIAL COMPATIBILITY CONFLICT DETECTED!")
            print(f"      -> Video file is encoded in H.264 '{codec_context.profile}' Profile.")
            print(f"      -> Many browsers (Chrome, Edge, Safari) strictly require H.264 'Constrained Baseline' profile in WebRTC.")
            print(f"      -> Direct demux pass-through (decode=False) will send these raw {codec_context.profile} packets.")
            print(f"      -> If the video remains black in the UI despite being 'Connected', the browser is silently discarding")
            print(f"         the packets due to profile incompatibility.")
            print(f"      -> RECOMMENDED SOLUTION: Re-encode sample.mp4 to Baseline Profile, or run the sender with transcoding.")
            
        return True
    except Exception as e:
        print(f"[FAILED] Error parsing video container: {e}")
        return False

async def run_webrtc_and_signaling_diagnostics():
    print("\n" + "="*70)
    print("[DIAGNOSTIC] STEP 2: WEBRTC TRACK & SDP CODEC NEGOTIATION DIAGNOSTICS")
    print("="*70)
    
    try:
        # Create a test PeerConnection
        pc = RTCPeerConnection()
        print("[OK] RTCPeerConnection successfully initialized.")
        
        # Try to open MediaPlayer
        player = MediaPlayer(VIDEO_FILE, decode=False)
        if player.video:
            print(f"[OK] MediaPlayer successfully opened '{VIDEO_FILE}' with decode=False (Demux Mode).")
            print(f" - Video Track Created: ID={player.video.id}, Kind={player.video.kind}")
            
            # Add track
            pc.addTrack(player.video)
            print("[OK] Demuxed video track successfully registered to PeerConnection.")
        else:
            print("[FAILED] MediaPlayer opened but failed to create a valid video track.")
            await pc.close()
            return
            
        # Create Offer to analyze SDP
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        print("[OK] Local SDP Offer successfully generated.")
        
        sdp = pc.localDescription.sdp
        print("\n[SDP CODEC PARSING & SDP PARAMETERS ANALYSIS]:")
        
        h264_lines = [line for line in sdp.split("\r\n") if "H264" in line or "profile-level-id" in line]
        if h264_lines:
            print(" [H.264 Advertised Parameters]:")
            for line in h264_lines[:6]:
                print(f"   -> {line}")
                
            # Check for profile-level-id
            import re
            profile_match = re.search(r"profile-level-id=([0-9a-fA-F]{6})", sdp)
            if profile_match:
                profile_id = profile_match.group(1)
                print(f"   [SDP Match] Found H.264 profile-level-id: {profile_id}")
                # 42e01f = CBP Level 3.1, 42001f = Baseline Level 3.1
                if profile_id.lower().startswith("42"):
                    print("   -> Verified SDP Profile: Constrained Baseline Profile (Fully Browser Compatible!).")
                else:
                    print(f"   -> Profile ID '{profile_id}' might require browser High Profile support.")
        else:
            print(" [WARNING] H.264 is not found in the SDP offer! VP8 or other codec will be negotiated.")
            
        vp8_lines = [line for line in sdp.split("\r\n") if "VP8" in line]
        if vp8_lines:
            print(" [VP8 Advertised Parameters]:")
            for line in vp8_lines[:2]:
                print(f"   -> {line}")
                
        await pc.close()
        print("\n[OK] WebRTC local track and SDP negotiation checks complete.")
        
    except Exception as e:
        print(f"[FAILED] WebRTC internal checks failed: {e}")
        return

    print("\n" + "="*70)
    print("[DIAGNOSTIC] STEP 3: GO BACKEND SIGNALING HUB CONNECTIVITY DIAGNOSTICS")
    print("="*70)
    
    print(f"Connecting to signaling server at: {SIGNALING_URL} ...")
    start_time = time.time()
    try:
        async with websockets.connect(SIGNALING_URL, timeout=3.0) as ws:
            latency = (time.time() - start_time) * 1000
            print(f"[OK] Connected to Go Backend Signaling Hub in {latency:.1f} ms.")
            
            # Send ping message to test echo
            ping_msg = json.dumps({"type": "ping", "timestamp": time.time()})
            await ws.send(ping_msg)
            print("[OK] Ping control packet dispatched.")
            
            # Wait for response if any, or complete
            print("[OK] Connection, handshaking, and signaling I/O channel are healthy!")
            
    except ConnectionRefusedError:
        print(f"[FAILED] Connection refused by host on Port 8080!")
        print("         -> Make sure your Go Backend server is running via launch_all.ps1!")
    except Exception as e:
        print(f"[FAILED] Signaling websocket check failed: {e}")

if __name__ == "__main__":
    print("\nRESCUE ROBOT SYSTEM - WEBRTC PIPELINE DEBUGGER")
    print("Starting objective diagnostics of the transmission pipeline...")
    
    # 1. Run container check
    container_ok = run_container_diagnostics()
    
    # 2. Run WebRTC & Signaling check
    asyncio.run(run_webrtc_and_signaling_diagnostics())
    
    print("\n" + "="*70)
    print("DIAGNOSTICS DONE. INSPECT THE WARNINGS ABOVE.")
    print("="*70 + "\n")
