from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from diffusers import DiffusionPipeline
from diffusers.utils import export_to_video  # Import missing function
import torch
from PIL import Image
import io
import os
import gc  # For memory management

app = FastAPI()

# Initialize model (but don't load it yet)
pipe = None

def load_model():
    global pipe
    if pipe is None:
        pipe = DiffusionPipeline.from_pretrained(
            "cerspense/zeroscope_v2_576w",
            torch_dtype=torch.float16,
        )
        pipe.to("cuda")
        pipe.enable_model_cpu_offload()

@app.on_event("startup")
async def startup_event():
    load_model()

@app.post("/generate-video")
async def generate_video(
    prompt: str = "A robot dancing on the moon",
    image: UploadFile = File(None),
    num_frames: int = 12,
):
    try:
        # Ensure model is loaded
        load_model()
        
        # Process image if provided
        img = None
        if image:
            img_data = await image.read()
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            if not prompt or prompt == "A video based on the uploaded image":
                prompt = "High quality animation of the image with smooth motion"

        # Generate video
        generator = torch.Generator(device="cuda").manual_seed(42)  # For reproducibility
        frames = pipe(
            prompt,
            image=img,  # Pass image directly if provided
            num_frames=num_frames,
            generator=generator
        ).frames

        # Save and return video
        output_path = "generated_video.mp4"
        export_to_video(frames, output_path, fps=8)
        
        # Clean up
        del frames
        torch.cuda.empty_cache()
        gc.collect()
        
        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename="generated_video.mp4"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists("generated_video.mp4"):
            os.remove("generated_video.mp4")  # Clean up temp file