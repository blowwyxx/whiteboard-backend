from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os
from moviepy.editor import ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()

OUTPUT_DIR = "videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ScriptRequest(BaseModel):
    script: str

@app.post("/generate")
def generate_video(data: ScriptRequest):
    script_text = data.script
    video_id = str(uuid.uuid4())
    frames = []

    # Use a default system font (for Linux/Render compatibility)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = 36
    font = ImageFont.truetype(font_path, font_size)

    lines = script_text.strip().split("\n")

    for i, line in enumerate(lines):
        img = Image.new("RGB", (1280, 720), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        w, h = draw.textsize(line, font=font)
        draw.text(((1280 - w) / 2, (720 - h) / 2), line, font=font, fill=(0, 0, 0))
        frame_path = f"/tmp/frame_{video_id}_{i}.png"
        img.save(frame_path)
        frames.append(frame_path)

    clips = [ImageClip(f).set_duration(1.5) for f in frames]
    final_video = concatenate_videoclips(clips, method="compose")
    output_path = os.path.join(OUTPUT_DIR, f"{video_id}.mp4")
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio=False)

    for frame in frames:
        os.remove(frame)

    return {"video_url": f"/video/{video_id}"}

@app.get("/video/{video_id}")
def get_video(video_id: str):
    file_path = os.path.join(OUTPUT_DIR, f"{video_id}.mp4")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="video/mp4")
    return {"error": "Video not found"}
