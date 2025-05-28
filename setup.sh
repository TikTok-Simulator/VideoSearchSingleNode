#!/bin/bash

# Function to print messages
print_message() {
    echo "========================================"
    echo "$1"
    echo "========================================"
}

# Step 1: Clone Required Repositories
print_message "Cloning Required Repositories"
if [ ! -d "Milvus-Setup" ]; then
    git clone https://github.com/your-org/Milvus-Setup.git
else
    echo "Milvus-Setup already exists. Skipping clone."
fi

if [ ! -d "video-fetch-and-trim" ]; then
    git clone https://github.com/TikTok-Simulator/video-fetch-and-trim.git
else
    echo "video-fetch-and-trim already exists. Skipping clone."
fi

# Step 2: Start Docker Services
print_message "Starting Docker Services"
cd Milvus-Setup
docker-compose up -d
cd ..

# Step 3: Set Up Python Environment
print_message "Setting Up Python Environment"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists. Skipping creation."
fi

source .venv/bin/activate
pip install -r requirements.txt
echo "Python dependencies installed."

# Step 4: Check ffmpeg Installation
print_message "Checking ffmpeg Installation"
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg not found. Please install it manually."
    exit 1
else
    echo "ffmpeg is installed."
fi

# Step 5: Create .env File
print_message "Setting Up Environment Variables"
if [ ! -f ".env" ]; then
    cat <<EOL > .env
TWELVE_LABS_API_KEY=<your-api-key>
HUGGING_FACE_TOKEN=<your-hugging-face-token>
CATEGORY=Education
MAX_VIDEOS_PER_CATEGORY=10
DB_URL=http://localhost:19530
DB_URLs=http://localhost:19530 # Can add more DB URL, seperate by ","
VIDEO_COLLECTION_NAME=video_embedding
TEXT_COLLECTION_NAME=text_embedding
GRADIO_TEMP_DIR=video-fetch-and-trim/videos
EOL
    echo ".env file created. Please update it with your API keys."
else
    echo ".env file already exists. Skipping creation."
fi

# Step 6: Final Message
print_message "Setup Complete"
echo "You can now run the following commands:"
echo "1. Build the vector database: python3 build_database.py"
echo "2. Perform video retrieval: python3 run.py"
echo "3. Launch Gradio demo: python3 gradio_demo.py"
