# VideoSearchSingleNode

## Key Features
- Generate embeddings from video and description (text) using Twelve Labs API
- Store data at vector database using Milvus
- Retrieve similar videos from given video (and description)

## Setup Environment

**Notes**: Make sure to install `ffmpeg`  (in Linux, use `apt` command) to perform video processing.

This project can run on Linux and MacOS devices only, because of `Milvus Lite` restrictions on operating systems. The following steps are used for Linux.

### 1. Create `.venv`:
```bash
python3 -m venv .venv
```

### 2. Access virtual environment:
```bash
source .venv/bin/activate
```

### 3. Install requirements:
```bash
pip install -r requirements.txt
```

## Create Twelve Labs API key and add to environment file

### 1. Create Twelve Labs API key:
- Sign up at [Twelve Labs API key](https://playground.twelvelabs.io/)
- Go to account and get API key. This is free to use but has **limit usage**.

### 2. Add to environment file:

Create a `.env` file at the root directory and add the following line:
```
TWELVE_LABS_API_KEY=<your-api-key>
```

## Run example

You can now run example code within two steps:

### Step 1. Build vector database

The `build_database.py` file implements a sample guide to create a Milvus Lite database (`.db` file locally), create collections to store embeddings and add some sample video URLs (can be files also) and text descriptions.

```bash
python3 build_database.py
```

### Step 2. Run video retrieval

After building the database, a video file/URL and an optional text description can be used to retrieve lists of similar videos, with the limit set default as 10 (`limit=1` in example code for demonstration though).

```bash 
python3 run.py
```

## Integration
To run entire services as a consistency system. Please clone two more repositories as follow architecture:
```bash
Milvus-Setup/
    - docker-compose.yml
    - main.py
src
static
video-fetch-and-trim/
    - main.py
    - requirements.txt
.gitignore
build_database.py
run.py
.env        <---- You have to add environment variables here
```

```bash
# .env
HUGGING_FACE_TOKEN=<HUGGING_FACE_TOKEN>
CATEGORY=Education # check out https://github.com/TikTok-Simulator/video-fetch-and-trim?tab=readme-ov-file#list-of-categories
MAX_VIDEOS_PER_CATEGORY=10
TWELVE_LABS_API_KEY=<TWELVE_LABS_API_KEY>
DB_URL=http://localhost:19530
VIDEO_COLLECTION_NAME=video_embedding
TEXT_COLLECTION_NAME=text_embedding
GRADIO_TEMP_DIR=video-fetch-and-trim/videos # !important store the downloaded video from internet url
```

## Gradio demo
- `gradio_demo.py`: run `python gradio_demo.py` to start a demo UI 
- `gradio_main.py`: contains exported function used to `gradio_demo.py`
- `gradio_download.py`: test streaming video: download a video from the internet and concat to a local video until end
- `gradio_stream.py`: test streaming video: streaming video by continious loading and displaying the local video