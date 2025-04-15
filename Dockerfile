FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY ./app /app

# Instala dependências Python (incluindo torch com CUDA 12.1)
# Configura o ambiente Python
RUN python3 -m pip install --upgrade pip setuptools wheel

# Instala torch com CUDA 12.1 primeiro
# Instala PyTorch primeiro com versões específicas
RUN pip install --no-cache-dir \
    torch==2.1.1+cu121 \
    torchvision==0.16.1+cu121 \
    --extra-index-url https://download.pytorch.org/whl/cu121
RUN pip install --no-cache-dir numpy==1.26.4  # Versão compatível
RUN pip install --no-cache-dir -r requirements.txt

# Cria o diretório de saída
RUN mkdir -p /app/output_videos

# Verificação da instalação
RUN python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); \
    print(f'CUDA: {torch.version.cuda}')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]