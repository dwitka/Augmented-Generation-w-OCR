# Retrieval-Augmented Generation (RAG) with Optical Character Recoginition (OCR)

Instructions are for Debian/Ubuntu systems:

### OVERVIEW
1. initiate local git repository
2. clone repository from github
3. get minio setup
4. get a pinecone api_key from https://pinecone.io
5. you will need a openai api_key https://platform.openai.com/
6. add your api_keys to config.py
7. set up your virtual environment
8. install dependencies
9. start minio server
10. start fastapi server
11. test upload endpoint with curl, confirm results
12. test ocr endpoint with curl, confirm results
13. test extract endpoint with curl, confirm results

### initiate local git repository
```
$ git init .
```

### clone repository from github, replace <pat> with your personal access token
```
$ git clone https://<pat>@github.com/dwitka/Augmented-Generation-w-OCR.git
```

### get the minio package and install, create a minio directory
```
$ wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20240507064125.0.0_amd64.deb -O minio.deb
$ sudo dpkg -i minio.deb
$ mkdir ./minio
```

### get your api_keys
        - get a pinecone api_key from https://pinecone.io
        - you will need a openai api_key https://platform.openai.com/

### set up your virtual environment in the same folder as your git repository, activate
```
$ python3 -m venv venv
$ source venv/bin/activate
```

### install your dependencies
```
$ pip install -r requirements.txt
```

### open a second terminal window and run the minio server
```
$ minio server ./minio --console-address :9001
```

### open the minio portal in your web browser localhost:9001
        - enter credentials given from minio server
        - create a bucket named 'first'

### open a third terminal window and start the fastapi server
```
fastapi dev main.py
```

### test upload endpoint: upload one or more files to minio server
```
$ curl -X POST -F "files=@media/resume.pdf" http://localhost:8000/upload

$ curl -X POST -F "files=@media/resume.pdf" -F "files=@media/SoftDocs.pdf" http://localhost:8000/upload
```

### confrim that your bucket received the file(s) and it can be downloaded

### test ocr endpoint: ocr and embeddings test
```
curl -X POST -H "Content-Type: application/json" -d '{"url":"http://127.0.0.1:9000/first/acd9af0e-2708-4909-b81c-2eeb2009888a?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minioadmin%2F20240512%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240512T000021Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=2cd3409b453a17f74205282b70dff1dc411fbf35a532bce47008a686431ab0e9"}' http://localhost:8000/ocr
```

### test extract endpoint: extract attributes
```
$ curl -X POST -H "Content-Type: application/json" -d '{"message":"How much money does User2 want for the bag?"}' http://localhost:8000/extract
```

# HOW DOES THIS APP WORK?
1. load files to minio
2. get file from minio and simulate ocr
3. get embeddings for file
4. upload embeddings to pinecone
5. turn message into embeddings
6. run vector search to generate an answer
