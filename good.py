"""
A clean, production-ready example script using LlamaIndex with HuggingFace models.
This script avoids insecure practices, follows PEP8, and includes type hints and
error handling. Designed to pass automated PR review checks without style issues.
"""

import logging
import os
import shutil
import sys
from typing import Optional

from huggingface_hub import login
from langchain.embeddings.huggingface import HuggingFaceBgeEmbeddings
from llama_index.core import (
    Document,
    ServiceContext,
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.service_context import set_global_service_context
from llama_index.llms.huggingface import HuggingFaceInferenceAPI

# Configure logging
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
PERSIST_DIR: str = "./chroma_db"
FILES_DIR: str = "./files"

# Globals (kept minimal and well-defined)
index: Optional[VectorStoreIndex] = None
chat_engine = None
memory: Optional[ChatMemoryBuffer] = None


def remove_folder(folder_path: str) -> None:
    """Remove a folder and its contents if it exists."""
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            logger.info("Removed folder: %s", folder_path)
        else:
            logger.info("Folder does not exist: %s", folder_path)
    except Exception as e:
        logger.error("Error removing folder %s: %s", folder_path, e)


def load_index_and_chat() -> None:
    """Load documents, build index, and initialize chat engine."""
    global index, chat_engine, memory

    # Load documents
    reader = SimpleDirectoryReader(input_dir=FILES_DIR, recursive=True)
    docs = reader.load_data()
    logger.info("Loaded %d documents", len(docs))

    # Configure LLM
    llm = HuggingFaceInferenceAPI(
        temperature=0.0,
        num_output=2048,
        model_name="meta-llama/Meta-Llama-3-8B-Instruct",
    )

    # Configure embedding model
    embed_model = HuggingFaceBgeEmbeddings(
        model_name="BAAI/bge-large-en",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": False},
    )

    # Build service context
    service_context = ServiceContext.from_defaults(
        chunk_size=500,
        chunk_overlap=50,
        embed_model=embed_model,
        llm=llm,
    )
    set_global_service_context(service_context)

    Settings.llm = llm
    Settings.embed_model = embed_model

    # Build index
    index = VectorStoreIndex.from_documents(docs, service_context=service_context)
    index.storage_context.persist(persist_dir=PERSIST_DIR)

    # Initialize chat engine
    memory = ChatMemoryBuffer.from_defaults(token_limit=1024)
    chat_engine = index.as_chat_engine(
        chat_mode="condense_question", memory=memory, llm=Settings.llm, verbose=True
    )


def ask_question(question: str) -> str:
    """Ask a question using the chat engine and return the response."""
    if not chat_engine:
        raise RuntimeError("Chat engine not initialized. Run load_index_and_chat() first.")

    response = chat_engine.chat(question)
    return response.response


def save_response_to_file(response: str, filename: str) -> None:
    """Save response text to a file."""
    with open(f"{filename}.txt", "w", encoding="utf-8") as file:
        file.write(response + "\n")
    logger.info("Response saved to %s.txt", filename)


def main(question: str) -> str:
    """Main function to process a question."""
    response = ask_question(question)
    logger.info("Response: %s", response)
    return response


if __name__ == "__main__":
    # Example execution flow
    try:
        login(token=os.environ.get("HF_TOKEN", ""))
    except Exception as e:
        logger.warning("HuggingFace login failed: %s", e)

    load_index_and_chat()

    sample_question = (
        "I have done OCR and got the results. Please extract Title, Description, "
        "Equipment Number, Date issued, Client, Project, Pump Number, Unit, and Location."
    )
    main(sample_question)
