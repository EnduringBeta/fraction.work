#!/bin/bash

if [ -z "$1" ]; then
  echo "Open AI API key required"
  exit 1
fi

OPENAI_API_KEY="$1"

IMAGE_NAME=fraction.work

echo "Building new Docker image (if repo changed, is it pushed and CACHEBUST updated?)..."
echo

docker build -t $IMAGE_NAME .

echo
echo "Building new Docker container from image..."
echo

docker run -d -p 3306:3306 -p 5000:5000 -p 3000:3000 -e OPENAI_API_KEY=$OPENAI_API_KEY $IMAGE_NAME

echo
echo "Redocking complete!"
