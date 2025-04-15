FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY ./app /app

# Instala dependências Python (incluindo torch com CUDA 12.1)
RUN pip install --no-cache-dir numpy==1.26.4  # Versão compatível
RUN pip install --no-cache-dir -r requirements.txt


# Verifica as instalações
RUN python3 -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
RUN python3 -c "import torch; print(f'PyTorch version: {torch.__version__}')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]