from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from diffusers import DiffusionPipeline
from diffusers.utils import export_to_video
import torch
import os
import gc
import logging
from pathlib import Path
import uuid
from datetime import datetime
import os

# Configurações
app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Diretório de saída (usará a variável de ambiente)
OUTPUT_VIDEOS_DIR = Path(os.getenv("OUTPUT_VIDEOS_DIR", "/app/output_videos"))
OUTPUT_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Pipeline do modelo
zeroscope_pipe = None

def load_zeroscope():
    global zeroscope_pipe
    if zeroscope_pipe is None:
        try:
            logger.info("Carregando modelo Zeroscope...")
            zeroscope_pipe = DiffusionPipeline.from_pretrained(
                "cerspense/zeroscope_v2_576w",
                torch_dtype=torch.float16
            )
            zeroscope_pipe.to("cuda")
            zeroscope_pipe.enable_model_cpu_offload()
            logger.info("Modelo carregado com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}")
            raise

@app.on_event("startup")
async def startup_event():
    load_zeroscope()

def generate_unique_filename():
    """Gera um nome de arquivo único com timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    return OUTPUT_VIDEOS_DIR / f"video_{timestamp}_{unique_id}.mp4"

@app.post("/text-to-video")
async def text_to_video(
    prompt: str = "A robot dancing on the moon",
    num_frames: int = 24,
    height: int = 320,
    width: int = 576
):
    output_path = generate_unique_filename()
    
    try:
        # Limpeza de memória
        torch.cuda.empty_cache()
        gc.collect()

        logger.info(f"Gerando vídeo: {output_path.name}")
        
        # Geração do vídeo
        with torch.inference_mode():
            frames = zeroscope_pipe(
                prompt=prompt,
                num_frames=num_frames,
                height=height,
                width=width,
                generator=torch.Generator(device="cuda").manual_seed(42)
            ).frames

        # Salva o vídeo
        export_to_video(frames, str(output_path), fps=8)
        
        if not output_path.exists():
            raise HTTPException(status_code=500, detail="Falha ao gerar arquivo de vídeo")
        
        return FileResponse(
            str(output_path),
            media_type="video/mp4",
            filename=output_path.name
        )
        
    except torch.cuda.OutOfMemoryError:
        error_msg = "Memória GPU insuficiente. Reduza num_frames ou resolução."
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        logger.error(f"Erro na geração: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        torch.cuda.empty_cache()
        gc.collect()