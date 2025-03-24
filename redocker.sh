#!/bin/bash

IMAGE_NAME=fraction.work

echo "Building new Docker image (if repo changed, is it pushed and CACHEBUST updated?)..."
echo

docker build -t $IMAGE_NAME .

echo
echo "Building new Docker container from image..."
echo

docker run -d -p 3306:3306 -p 5000:5000 -p 3000:3000 -e REACT_APP_OPENAI_API_KEY=<addMe> $IMAGE_NAME

echo
echo "Redocking complete!"
