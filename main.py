--- whiteboard_backend/main.py ---

from fastapi import FastAPI, UploadFile, Form from fastapi.responses import FileResponse from pydantic import BaseModel from typing import Optional import uuid import os from moviepy.editor import * from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

OUTPUT_DIR = "videos" os.makedirs(OUTPUT_DIR, exist_ok=True)

class ScriptRequest(BaseModel): script: str

@app.post("/generate") def generate_video(data: ScriptRequest): script_text = data.script video_id = str(uuid.uuid4()) frames = []

# Create frames with text line by line
lines = script_text.split("\n")
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Use system-safe font
font = ImageFont.truetype(font_path, 40)
for i, line in enumerate(lines):
    img = Image.new("RGB", (1280, 720), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((100, 100 + i * 60), line, font=font, fill=(0, 0, 0))
    frame_path = f"/tmp/frame_{video_id}_{i}.png"
    img.save(frame_path)
    frames.append(frame_path)

# Create video
clips = [ImageClip(m).set_duration(1.5) for m in frames]
final_video = concatenate_videoclips(clips, method="compose")
output_path = os.path.join(OUTPUT_DIR, f"{video_id}.mp4")
final_video.write_videofile(output_path, fps=24)

# Cleanup frames
for frame in frames:
    os.remove(frame)

return {"video_url": f"/video/{video_id}"}

@app.get("/video/{video_id}") def get_video(video_id: str): file_path = os.path.join(OUTPUT_DIR, f"{video_id}.mp4") return FileResponse(file_path, media_type="video/mp4")

