#!/bin/bash

# Repository name
REPO="ghcr.io/pilamrocky/vr_score_keeper"

# Function to display usage instructions
usage() {
  echo "Usage: $0 <version_number>"
  echo "Example: $0 1.3"
  exit 1
}

# Check if a version number was provided
if [ -z "$1" ]; then
  usage
fi

VERSION=$1
VERSION_TAG="${REPO}:${VERSION}"
LATEST_TAG="${REPO}:latest"

# Build the Docker image with both the version tag and the "latest" tag
echo "Building Docker image with tags: ${VERSION_TAG} and ${LATEST_TAG}"
docker build -t "${VERSION_TAG}" -t "${LATEST_TAG}" .

# Check if the build was successful
if [ $? -ne 0 ]; then
  echo "Docker build failed. Exiting."
  exit 1
fi

# Push the newly created version tag
echo "Pushing version tag: ${VERSION_TAG}"
docker push "${VERSION_TAG}"

# Check if the push was successful
if [ $? -ne 0 ]; then
  echo "Docker push of version tag failed. Exiting."
  exit 1
fi

# Push the newly created latest tag
echo "Pushing latest tag: ${LATEST_TAG}"
docker push "${LATEST_TAG}"

# Check if the push was successful
if [ $? -ne 0 ]; then
  echo "Docker push of latest tag failed. Exiting."
  exit 1
fi

echo "Image successfully built and pushed with tags: ${VERSION} and latest."
