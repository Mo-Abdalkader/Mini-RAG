# Mini-RAG

A minimal implementation of a Retrieval-Augmented Generation (RAG) system for document-based question answering.

## Project Overview

Mini-RAG is a FastAPI-based backend service that handles document upload, processing, and chunking. It serves as the foundation for a complete RAG pipeline that can later integrate with LLM providers for intelligent document querying.

## What Has Been Done

- **Document Upload API**: Endpoints to upload `.txt` and `.pdf` files to projects
- **Document Processing**: File content extraction using LangChain loaders (TextLoader, PyMuPDFLoader)
- **Text Chunking**: Configurable chunk size and overlap using RecursiveCharacterTextSplitter
- **Project Management**: MongoDB-based project storage with auto-creation on first upload
- **File Validation**: Type and size validation for uploaded files

## File Structure

```
src/
├── main.py                      # FastAPI app entry point, MongoDB connection setup
├── settings.json                # VS Code editor settings
│
├── helpers/
│   ├── config.py                # Settings management via pydantic (env variables)
│   └── __init__.py
│
├── routes/
│   ├── base.py                  # Base API routes (health check, app info)
│   ├── data.py                  # Data endpoints: upload & process files
│   └── schemes/
│       └── data.py              # Pydantic request/response schemas
│
├── controllers/
│   ├── BaseController.py        # Shared utilities (file paths, random strings)
│   ├── DataController.py        # File validation & path generation
│   ├── ProjectController.py     # Project directory management
│   └── ProcessController.py     # File loading & text chunking logic
│
└── models/
    ├── BaseDataModel.py         # MongoDB model base class
    ├── ProjectModel.py          # Project CRUD operations
    ├── enums/
    │   ├── ProcessingEnum.py   # Supported file extensions (.txt, .pdf)
    │   ├── DatabaseEnum.py      # MongoDB collection names
    │   └── ResponseEnum.py      # API response signals
    └── db_schemes/
        ├── project.py           # Project Pydantic schema
        └── data_chunk.py        # Data chunk Pydantic schema

docker/
├── docker-compose.yml           # MongoDB container setup
└── mongodb/                    # MongoDB data volume

assets/
└── files/                      # Uploaded file storage directory
```

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| **FastAPI** | REST API framework for building endpoints |
| **Motor** | Async MongoDB driver for Python |
| **MongoDB** | Database for storing projects and metadata |
| **LangChain** | Document loading and text splitting |
| **PyMuPDF** | PDF text extraction |
| **Pydantic** | Data validation and settings management |
| **aiofiles** | Async file I/O operations |
| **Docker** | Containerized MongoDB service |

## Getting Started

1. **Set up environment variables** in `.env`:
   ```
   APP_NAME=Mini-RAG
   APP_VERSION=1.0.0
   OPENAI_API_KEY=your_key
   MONGODB_URL=mongodb://localhost:27007
   MONGODB_DATABSE=mini_rag
   FILE_MAX_SIZE=50
   FILE_DEFAULT_CHUNK_SIZE=1024
   ```

2. **Start MongoDB**:
   ```bash
   cd docker
   docker-compose up -d
   ```

3. **Run the application**:
   ```bash
   cd src
   uvicorn main:app --reload
   ```

4. **Access API docs**: http://localhost:8000/docs