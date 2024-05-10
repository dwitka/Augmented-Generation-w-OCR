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
curl -X POST -H "Content-Type: application/json" -d '{"message":"Who is David Witka?"}' http://localhost:8000/extract
```

HOW DOES THIS APP WORK?
1. load files to minio
2. get file from minio and simulate ocr
3. get embeddings for file
4. upload embeddings to pinecone
5. turn message into embeddings
6. run vector search to generate an answer
