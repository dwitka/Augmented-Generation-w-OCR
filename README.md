# Retrieval-Augmented Generation (RAG) with Optical Character Recoginition (OCR)
## you will need an openai api key and a pinecone api key to run the code

Docker inatallation instructions are for Ubuntu 20.04. For other OS go to https://docs.docker.com/engine/install

### OVERVIEW
1. install docker
2. login to Docker Hub
3. build docker image from Docker Hub
4. get docker container running
5. upload one or more files to remote Minio blob bucket
6. simulate ocr and upload embeddings to Pinecone vector database
7. query the database with a semantic question

### update the package index on your system
```
$ sudo apt update
```

### install the required dependencies
```
$ sudo apt install apt-transport-https ca-certificates curl software-properties-common
```

### add Docker GPG Key
```
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

### add Docker Repository for Ubuntu 20.04 (Focal Fossa)
```
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
```

### update the package index once more to include the Docker packages from the newly added repository
```
$ sudo apt update
```

### install Docker Engine
```
$ sudo apt install docker-ce docker-ce-cli containerd.io
```

### verify Installation
```
$ sudo docker --version
```

### manage Docker as a Non-root User
```
$ sudo usermod -aG docker $USER
```

### activate the changes in your current shell session
```
$ newgrp docker
```

### login to Docker Hub
```
$ docker login
```

### build docker image from Docker Hub
```
$ docker build -t davidwitka/my-image .
```

### get docker container running
```
$ docker run -d -p 8000:80 --name my-app -e OPENAI_API_KEY=your-openai-key -e PINECONE_API_KEY=your-pinecone-key davidwitka/my-image
```

### upload one or more files to remote Minio blob bucket
```
$ curl -X POST -F "files=@test/resume.pdf" http://localhost:8000/upload

$ curl -X POST -F "files=@test/resume.pdf" -F "files=@test/SoftDocs.pdf" http://localhost:8000/upload
```

## ***\*\*enter the returned url into the next code block\*\****

### simulate ocr and upload embeddings to Pinecone vector database
```
$ curl -X POST -H "Content-Type: application/json" -d '{"url":"http://127.0.0.1:9000/first/acd9af0e-2708-4909-b81c-2eeb2009888a?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minioadmin%2F20240512%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240512T000021Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=2cd3409b453a17f74205282b70dff1dc411fbf35a532bce47008a686431ab0e9"}' http://localhost:8000/ocr
```

### extract attributes: query the database with a semantic search
```
$ curl -X POST -H "Content-Type: application/json" -d '{"message":"How much money does User2 want for the bag?"}' http://localhost:8000/extract
```
