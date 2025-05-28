# Video Retrieval System

## Overview

This project enables video retrieval by generating embeddings from videos and descriptions (text) using the Twelve Labs API. These embeddings are stored in a vector database powered by Milvus, allowing for efficient similarity searches. The system supports retrieving similar videos based on a given video and optional text description.

## Key Features

- Generate embeddings for videos and text descriptions using the Twelve Labs API.
- Store embeddings in a Milvus vector database.
- Retrieve similar videos based on input video and/or text description.
- Gradio-based demo for interactive testing.

## Prerequisites

1. **Install `ffmpeg`**: Required for video processing. On Linux, use:
   ```bash
   sudo apt install ffmpeg
   ```
2. **Supported Platforms**: This project runs on Linux and macOS only due to Milvus Lite's operating system restrictions.

## Quick Setup with `setup.sh`

To simplify the setup process, you can use the provided `setup.sh` script. This script automates the following steps:
- Cloning required repositories.
- Starting Docker services.
- Setting up the Python virtual environment.
- Installing dependencies.
- Creating the `.env` file.

### Usage

1. Make the script executable:
   ```bash
   chmod +x setup.sh
   ```
2. Run the script:
   ```bash
   ./setup.sh
   ```
3. Follow the instructions printed by the script. If the `.env` file is created, update it with your API keys and other required values.

## Manual Setup

If you prefer to set up the project manually, follow the steps below.

### Step 1: Clone Required Repositories

Clone the following repositories and organize them as shown below:

```bash
git clone https://github.com/your-org/Milvus-Setup.git
git clone https://github.com/TikTok-Simulator/video-fetch-and-trim.git
```

Directory structure:
```
VideoSearchSingleNode/
├── Milvus-Setup/
│   ├── docker-compose.yml
│   ├── main.py
├── video-fetch-and-trim/
│   ├── main.py
│   ├── requirements.txt
├── src/
├── static/
├── build_database.py
├── run.py
├── gradio_demo.py
├── gradio_main.py
├── gradio_download.py
├── gradio_stream.py
├── .env
```

### Step 2: Start Docker Services

Navigate to the `Milvus-Setup` directory and start the required services using Docker Compose:

```bash
cd Milvus-Setup
docker-compose up -d
```

### Step 3: Set Up the Python Environment
You are at the root of `VideoSearchSingleNode`
1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```
2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Twelve Labs API Key

1. Sign up at [Twelve Labs](https://playground.twelvelabs.io/) and obtain an API key.
2. Create a `.env` file in the root directory and add the following:
   ```
   TWELVE_LABS_API_KEY=<your-api-key>
   ```

### Additional Environment Variables

Add the following variables to the `.env` file:
```
HUGGING_FACE_TOKEN=<your-hugging-face-token>
CATEGORY=Education
MAX_VIDEOS_PER_CATEGORY=10
DB_URL=http://localhost:19530
VIDEO_COLLECTION_NAME=video_embedding
TEXT_COLLECTION_NAME=text_embedding
GRADIO_TEMP_DIR=video-fetch-and-trim/videos
```

## Usage

### Step 1: Build the Vector Database

Run the `build_database.py` script to populate the Milvus database with video and text embeddings:

```bash
python3 build_database.py
```

### Step 2: Perform Video Retrieval

Use the `run.py` script to retrieve similar videos based on an input video and optional text description:

```bash
python3 run.py
```

### Step 3: Gradio Demo

Run the Gradio demo for an interactive UI:

```bash
python3 gradio_demo.py
```

## Resetting the Database

To reset the Milvus database, run the following commands:

```bash
cd Milvus-Setup
docker-compose down
rm -rf ./volumes/etcd ./volumes/minio ./volumes/milvus
docker-compose up -d
```

## Additional Tools

- `gradio_main.py`: Contains exported functions used by `gradio_demo.py`.
- `gradio_download.py`: Demonstrates video streaming by downloading and concatenating videos.
- `gradio_stream.py`: Demonstrates video streaming by continuously loading and displaying local videos.

## IP Configuration

To retrieve your local IP address, use the following command:

```bash
ipconfig getifaddr en0
```