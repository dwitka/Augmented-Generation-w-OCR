# https://min.io/docs/minio/linux/index.html

for Debian/Ubuntu systems:
run commands from terminal

# get the minio package and install
```
$ wget https://dl.min.io/server/minio/release/linux-amd64/archive/minio_20240507064125.0.0_amd64.deb -O minio.deb
$ sudo dpkg -i minio.deb
```

# make a minio directory and then run the server
```
$ mkdir ./minio
$ minio server ./minio --console-address :9001
```

# install minio interface for python
```
$ pip3 install minio
```

# test functionality of two endpoints
```
$ python3
>>> import main
>>> import asyncio
>>> x = asyncio.run(main.upload_files(["ocr/test.json"]))
>>> y = asyncio.run(main.ocr_and_upload_embeddings(x[0]['url']))
```

# extract attributes
```
$ curl -X POST -H "Content-Type: application/json" -d '{"message":"Who is David Witka?"}' http://localhost:8000/extract
```

# upload one or more files to minio server
```
$ curl -X POST -F "files=@media/resume.pdf" http://localhost:8000/upload

$ curl -X POST -F "files=@media/resume.pdf" -F "files=@media/SoftDocs.pdf" http://localhost:8000/upload
```

# ocr and embeddings test
```
curl -X POST -H "Content-Type: application/json" -d '{"url":"http://127.0.0.1:9000/first/0c1e44cb-bdd3-4f47-bffb-22d9db8ed421?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minioadmin%2F20240511%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240511T030230Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=84e5fc6a3f12199d93f78c170085fc83955bd086a58b80492fc11d1c56228443"}' http://localhost:8000/ocr
```

HOW DOES THIS APP WORK?
1. load files to minio
2. get file from minio and simulate ocr
3. get embeddings for file
4. upload embeddings to pinecone
5. turn message into embeddings
6. run vector search to generate an answer
