#!/usr/bin/env python3
"""Script to stream mock thermal video frames to the FastAPI/WebSocket dashboard.

Generates realistic thermal camera frames (using gradient colors, structural scan lines,
and active victim hot spots with green bounding boxes) and broadcasts them at ~10 FPS.
"""

import base64
import json
import math
import subprocess
import sys
import time
import urllib.error
import urllib.request

# Auto-install Pillow if not already present to ensure self-healing execution
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[Video Test] Pillow (PIL) is not installed. Installing Pillow automatically...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
        from PIL import Image, ImageDraw, ImageFont

        print("[Video Test] Pillow installed successfully!")
    except Exception as e:
        print(f"[Video Test] Failed to auto-install Pillow: {e}")
        print("[Video Test] Please run 'pip install Pillow' manually and try again.")
        sys.exit(1)

from io import BytesIO

SERVER_URL = "http://localhost:8080/api/demo/send-frame"


def generate_thermal_frame(frame_num: int) -> str:
    """Generate a high-quality mock thermal camera JPEG frame in base64.

    Generates a 320x240 image mimicking a FLIR thermal camera,
    with a moving structural human heat silhouette (hot spot) and scanning artifacts.
    """
    width, height = 320, 240

    # 1. Base Image - Cold background (Deep Blue/Purple)
    # Create radial gradient centered at center
    img = Image.new("RGB", (width, height), color=(15, 10, 45))
    draw = ImageDraw.Draw(img)

    # Render static scan lines to look like low-res thermal sensor
    for y in range(0, height, 4):
        draw.line([(0, y), (width, y)], fill=(12, 8, 35), width=1)

    # 2. Add moving heat sources (Ambient warm objects)
    # Warm rock
    draw.ellipse([50, 160, 110, 200], fill=(70, 20, 110))
    # Hot pipe
    draw.line([0, 40, width, 50], fill=(85, 30, 120), width=8)

    # 3. Add Human Silhouette (Active target)
    # Make the position move dynamically over time using trig functions
    t = frame_num * 0.05
    cx = int(width / 2 + math.sin(t) * 60)
    cy = int(height / 2 + math.cos(t * 1.5) * 30 + 10)

    # Draw hot body (Red/Orange center, yellow aura)
    # Head aura
    draw.ellipse([cx - 18, cy - 38, cx + 18, cy - 2], fill=(220, 100, 10))
    # Torso aura
    draw.ellipse([cx - 28, cy - 5, cx + 28, cy + 55], fill=(220, 100, 10))

    # Head core (Hot white-yellow)
    draw.ellipse([cx - 12, cy - 32, cx + 12, cy - 8], fill=(255, 235, 120))
    # Torso core (Hot white-yellow)
    draw.ellipse([cx - 18, cy, cx + 18, cy + 45], fill=(255, 235, 120))

    # 4. Draw Detection Bounding Box (simulating Sensor Fusion overlay)
    bx1 = cx - 35
    by1 = cy - 45
    bx2 = cx + 35
    by2 = cy + 60

    # Draw box lines (Green)
    draw.rectangle([bx1, by1, bx2, by2], outline=(34, 197, 94), width=2)

    # Draw bounding box text background
    draw.rectangle([bx1, by1 - 15, bx1 + 120, by1], fill=(34, 197, 94))

    # Write text inside the box (Simple default font fallback)
    # Since custom fonts might not be present, we use default bitmap font
    font = ImageFont.load_default()
    draw.text(
        (bx1 + 4, by1 - 14),
        f"VICTIM ALIVE: {94.8 + math.sin(t) * 2:.1f}%",
        fill=(0, 0, 0),
        font=font,
    )

    # 5. Overlays - Crosshair and temperature indicators
    draw.line(
        [width // 2 - 10, height // 2, width // 2 + 10, height // 2], fill=(255, 255, 255), width=1
    )
    draw.line(
        [width // 2, height // 2 - 10, width // 2, height // 2 + 10], fill=(255, 255, 255), width=1
    )

    # Temperature texts
    draw.text((10, 10), "FLIR E60", fill=(255, 255, 255), font=font)
    draw.text((width - 50, 10), "36.8 C", fill=(255, 235, 120), font=font)
    draw.text((width - 50, height - 20), "12.4 C", fill=(80, 80, 250), font=font)

    # Convert image to Base64 JPEG string in-memory
    buffered = BytesIO()
    img.save(buffered, format="JPEG", quality=75)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_str


def main():
    print("==================================================================")
    print("🤖 Rescue Robot Live Video Stream Simulator")
    print("==================================================================")
    print(f"Target Server: {SERVER_URL}")
    print("Press Ctrl+C to terminate the video stream.")
    print("------------------------------------------------------------------")

    frame_count = 0

    # Delay slightly to allow FastAPI to start up if run sequentially
    time.sleep(0.5)

    try:
        while True:
            frame_count += 1

            # 1. Generate new visual frame
            base64_data = generate_thermal_frame(frame_count)

            # 2. Assemble HTTP payload
            payload = {
                "frame_data": base64_data,
                "sensor_type": "THERMAL",
                "timestamp_ms": int(time.time() * 1000),
            }

            json_payload = json.dumps(payload).encode("utf-8")

            # 3. Dispatch POST request
            req = urllib.request.Request(
                SERVER_URL, data=json_payload, headers={"Content-Type": "application/json"}
            )

            try:
                with urllib.request.urlopen(req) as response:
                    response.read().decode("utf-8")
                    # Optionally print frame indicator
                    print(
                        f"\r[Stream] Dispatched Frame #{frame_count:04d} (JPEG Base64) to WebSocket -> SUCCESS",
                        end="",
                    )
            except urllib.error.URLError as ue:
                print(f"\n[Stream Error] Connection failed. Is FastAPI online? ({ue.reason})")
                print("[Stream] Retrying in 2 seconds...")
                time.sleep(2.0)
                continue

            # Stream at ~10 FPS (100ms interval)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n[Stream] Stream transmission terminated by operator (Ctrl+C).")
        print("==================================================================")


if __name__ == "__main__":
    main()
