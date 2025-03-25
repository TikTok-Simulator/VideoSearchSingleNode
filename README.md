# VideoSearchSingleNode

## Key Features
- Generate embeddings from video and description (text) using Twelve Labs API
- Store data at vector database using Milvus
- Video retrival (In progress)

## Setup Environment
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
- Go to account and get API key. This is free to use but has limit usage.

### 2. Add to environment file:

Create a `.env` file at the root directory and add the following line:
```
TWELVE_LABS_API_KEY=<your-api-key>
```

## Run example

You can now run example code at `run.py`.
```bash
python3 run.py
```
