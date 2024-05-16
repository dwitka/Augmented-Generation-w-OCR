"""

A Python-based backend API using FastAPI. The API features endpoints for file
uploads, a mock OCR function, and an attribute extraction mechanism powered by RAG.

!!!! DON'T FORGET TO TEST ENDPOINTS WITH POSTMAN !!!!

pip install -U langchain-pinecone
pip install -U langchain-openai

"""
import os
import json
import logging
import uuid
from io import BytesIO
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import JSONLoader
from langchain_pinecone import Pinecone as PC
from langchain_openai import OpenAI, OpenAIEmbeddings
from keys import PINECONE_API_KEY, OPENAI_API_KEY
from pinecone import Pinecone, ServerlessSpec
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from minio import Minio


# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

app = FastAPI()

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

INDEX = "embed-project"
if INDEX not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX,
        dimension=1536,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
            )
        )
idx = pc.Index(INDEX)

# Initialize Minio client
minio_client = Minio(
    endpoint = "play.minio.io:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=True
)

# Accepts one or more file uploads (limited to pdf, tiff, png,jpeg formats).
ACCEPTED_FORMATS = ["pdf", "tiff", "png", "jpeg"]


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Saves the processed file to a cloud storage solution, returning one or
    more unique file identifiers or signed URLs for the upload. You can use
    tools like Minio to mimic blob storage."""
    logging.info('Endpoint /upload called')
    uploaded_files_urls = []

    for afile in files:
        file_extension = afile.filename.split(".")[-1].lower()
        if file_extension not in ACCEPTED_FORMATS:
            logging.error("Unsupported file format: %s", file_extension)
            raise HTTPException(status_code=400, \
                                    detail=f"Unsupported file format: {file_extension}")

        # Read the file content
        filepath = 'test/' + afile.filename
        with open(filepath, 'rb') as f:
            contents = f.read()

        # Generate a unique file identifier
        file_id = str(uuid.uuid4())

        # Save the file to Minio
        # Minio server should be running
        try:
            minio_client.put_object(
                "first",  # Bucket name
                file_id,    # Object name
                BytesIO(contents),
                len(contents)
            )
            logging.info("Uploaded file %s to Minio", file_id)
        except Exception as e:
            logging.error("Failed to upload file: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}") from e

        # Get signed URL for the uploaded file
        url = minio_client.presigned_get_object("first", file_id)
        uploaded_files_urls.append({"file_id": file_id, "url": url})

    logging.info('All files uploaded successfully')

    return uploaded_files_urls


@app.post("/ocr")
async def ocr_and_upload_embeddings(request: Request):
    """Simulates running an OCR service on a file for a given a signed url.
    Process OCR results with OpenAI's embedding models, then upload the
    embeddings to a vector database (e.g, Pinecone) for future searches."""
    logging.info('Endpoint /ocr called')
    payload = await request.json()

    # Retrieve signed url from payload
    try:
        url = payload["url"]
        logging.info('Received URL: %s', url)
    except Exception as e:
        logging.error("No URL provided: %s", str(e))
        raise HTTPException(status_code=400, detail=f"No url provided: {str(e)}") from e

    # Simulate running OCR service on the file from signed URL
    try:
        loader = JSONLoader(file_path="./ocr/test.json", jq_schema=".", text_content=False)
        data = loader.load()
        # split into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
        texts = text_splitter.split_documents(data)
        logging.info('OCR performed successfully')
    except Exception as e:
        logging.error("Failed to perform OCR: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to perform OCR: {str(e)}") from e

    # Process OCR results with OpenAI's embedding models
    try:
        openai_key = OPENAI_API_KEY
        embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
        logging.info('Embeddings generated successfully')
    except Exception as e:
        logging.error("Failed to generate embeddings: %s", str(e))
        raise HTTPException(status_code=500, \
                                detail=f"Failed to generate embeddings: {str(e)}") from e

    # Upload embeddings to Pinecone vector database
    try:
        # upload embeddings to Pinecone
        index_name = 'embed-project' # replace with your index name
        os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY
        # upload to our pinecone index
        PC.from_texts([t.page_content for t in texts], embeddings, index_name=index_name)
        logging.info('Embeddings uploaded to Pinecone successfully')
    except Exception as e:
        logging.error("Failed to upload embeddings to Pinecone: %s", str(e))
        raise HTTPException(status_code=500, \
                                detail=f"Failed to upload embeddings to Pinecone: {str(e)}") from e

    return "Embeddings uploaded to Pinecone successfully"


@app.post('/extract')
async def create_chat(request: Request):
    """Takes a query text and file_id as input, performs a vector search and
    returns matching attributes based on the embeddings. The vector search
    will help in identifying the relevant part(s) of the file and you may
    need to call openAI chat completion to generate the answer from the
    search result."""
    logging.info('Endpoint /extract called')
    payload = await request.json()

    try:
        query = payload["message"]
        logging.info("Received message: %s", query)
    except Exception as e:
        logging.error("No message provided: %s", str(e))
        raise HTTPException(status_code=400, detail=f"No message provided: {str(e)}") from e

    try:
        openai_key = OPENAI_API_KEY
        embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
        logging.info('Embeddings generated successfully')
    except Exception as e:
        logging.error("Failed to generate embeddings: %s", str(e))
        raise HTTPException(status_code=500, \
                                detail=f"Failed to generate embeddings: {str(e)}") from e

    index_name = "embed-project"
    os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY
    docsearch = PC.from_existing_index(index_name=index_name, embedding=embeddings)

    llm = OpenAI(temperature=0, openai_api_key=openai_key)
    chain = load_qa_chain(llm, chain_type="stuff")

    logging.info('Retrieving documents from Pinecone')
    docs = docsearch.similarity_search(query)
    logging.info('Retrieved %d documents', len(docs))

    logging.info('Executing QA chain')
    response = chain.run(input_documents=docs, question=query)

    logging.info('Generated response')
    logging.info(response)

    return json.dumps(response)

# test ci again
