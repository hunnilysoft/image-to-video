### Image-to-Video API com Docker
Este projeto permite gerar vídeos a partir de texto (Text-to-Video) ou imagens (Image-to-Video) usando o modelo Zeroscope_v2_576w, otimizado para GPUs NVIDIA com 12GB de VRAM.


| Cenário                          | Prompt | Imagem | Efeito                                                                 |
|----------------------------------|--------|--------|------------------------------------------------------------------------|
| **working    Text-to-Video (Criação do zero)** | ✅ Sim  | ❌ Não  | Gera um vídeo totalmente novo baseado na descrição textual.           |
| **Não Implementado Image-to-Video (Animação fiel)**  | ❌ Não  | ✅ Sim  | Anima a imagem fornecida sem alterar seu conteúdo.                    |
| **Não Implementado Image-to-Video + Edição**         | ✅ Sim  | ✅ Sim  | Transforma a imagem durante a animação (ex: muda estilo, adiciona efeitos). |


🚀 Como Rodar no Docker
Pré-requisitos
GPU NVIDIA (RTX 3060 12GB ou superior)

Docker e NVIDIA Container Toolkit instalados
Python 3.8+ (para testes locais opcionais)

🔧 Passo 1: Clone o Repositório
```bash
Copy
git clone https://github.com/seu-usuario/image-to-video-api.git
cd image-to-video-api
```
```bash

🐳 Passo 2: Construa e Execute o Container
```bash
Copy
# Construa a imagem (pode demorar na primeira vez)
docker-compose build
```
```bash
# Inicie o serviço
docker-compose up -d
⚠️ Verifique se a GPU está sendo detectada:
```
```bash
Copy
docker exec -it zeroscope-api nvidia-smi
🌐 Passo 3: Acesse a API
A API estará disponível em:
```
Copy
http://localhost:8000
Endpoint Principal
http
Copy
POST /generate-video
Content-Type: multipart/form-data
Exemplo de requisição (Bruno API / cURL):

bash
Copy
curl -X POST http://localhost:8000/generate-video \
  -F "prompt=Um gato astronauta em Marte" \
  -F "image=@input.jpg"  # Opcional
⚙️ Variáveis de Ambiente (Opcional)
Edite o docker-compose.yml para ajustar:

yaml
Copy
environment:
  - NUM_FRAMES=24          # Número de frames (padrão: 12)
  - OUTPUT_FPS=10          # Frames por segundo



🔍 Troubleshooting
Problema	Solução
CUDA out of memory	Reduza NUM_FRAMES ou use image.resize((512, 288)).
NVIDIA GPU not detected	Verifique se o NVIDIA Container Toolkit está instalado.
Model download failed	Delete o cache: rm -rf ./cache e reconstrua o container.


📜 Licença
MIT License. Consulte o arquivo LICENSE para detalhes.