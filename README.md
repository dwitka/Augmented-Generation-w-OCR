# Retrieval-Augmented Generation (RAG) with Optical Character Recoginition (OCR)
## you will need an openai api key and a pinecone api key to run the code

Docker inatallation instructions are for Ubuntu 20.04. For other OS go to https://docs.docker.com/engine/install

### OVERVIEW
1. install docker
2. login to Docker Hub
3. start docker service
4. build docker image from Docker Hub
5. get docker container running
6. upload one or more files to remote Minio blob bucket
7. simulate ocr and upload embeddings to Pinecone vector database
8. query the database with a semantic question

### update the package index on your system
```
sudo apt update
```

### install the required dependencies
```
sudo apt install apt-transport-https ca-certificates curl software-properties-common
```

### add Docker GPG Key
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

### add Docker Repository for Ubuntu 20.04 (Focal Fossa)
```
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
```

### update the package index once more to include the Docker packages from the newly added repository
```
sudo apt update
```

### install Docker Engine
```
sudo apt install docker-ce docker-ce-cli containerd.io
```

### verify Installation
```
sudo docker --version
```

### manage Docker as a Non-root User
```
sudo usermod -aG docker $USER
```

### activate the changes in your current shell session
```
newgrp docker
```

### login to Docker Hub
```
docker login
```
### start docker service
```
sudo service docker restart
```

### build docker image from Docker Hub
```
docker pull davidwitka/my-image:latest
```

### get docker container running
```
docker run --network="host" -d --name my-app -e OPENAI_API_KEY=your-openai-key -e PINECONE_API_KEY=your-pinecone-key davidwitka/my-image
```

### upload one or more files to remote Minio blob bucket
```
docker exec <container-id> curl -X POST -F "files=@/app/test/resume.pdf" http://localhost:80/upload

docker exec <container-id> curl -X POST -F "files=@/app/test/resume.pdf" -F "files=@/app/test/SoftDocs.pdf" http://localhost:80/upload
```

## ***\*\*enter the returned url into the next code block\*\****

### simulate ocr and upload embeddings to Pinecone vector database
```
docker exec 1bf0a8150f65 curl -X POST -H "Content-Type: application/json" -d '{"url":"https://play.minio.io:9000/first/7aeebedd-0b51-490f-b500-00a88dcb8169?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minioadmin%2F20240517%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20240517T201644Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=4e3fa61222807e1b695a32bf045227121a23b7e29091920fb9f633a6012a2ca3"}' http://localhost:80/ocr
```

### extract attributes: query the database with a semantic search
```
docker exec 1bf0a8150f65 curl -X POST -H "Content-Type: application/json" -d '{"message":"who is david witka?"}' http://localhost:80/extract
docker exec 1bf0a8150f65 curl -X POST -H "Content-Type: application/json" -d '{"message":"Give me a short, one paragraph summary of Software Documentation."}' http://localhost:80/extract

```
