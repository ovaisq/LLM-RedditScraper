# Build package, then build docker image, push the docker image
#  to private image registry running accessible on a local 
#  network only
# Assumes that image reposity url is:
#	docker-registry:50000

#!/bin/bash

echo "Building"
./build.sh

export srvc_ver=$(<ver.txt)
cd builds/BE_${srvc_ver}

echo "Configuring Build"
scp localhost:/apps/rollama/setup.config .

echo "Creating Docker image"
./build_docker.py

echo "Pushing Docker Image to Registry"
docker tag rollama:${srvc_ver} docker-registry:5000/rollama:${srvc_ver}
docker push dockeri-registry:5000/rollama:${srvc_ver}

echo "Clean up orphaned images"
# List orphaned images (those with the <none> tag)
orphaned_images=$(docker image ls --filter "dangling=true" -q)

# Check if there are any orphaned images
if [ -n "$orphaned_images" ]; then
    echo "Removing orphaned docker images"
    # Remove orphaned images
    docker image rm $orphaned_images
    echo "Cleaning up local docker images"
    # Remove specific local images
    docker image rm rollama:${srvc_ver}
    docker image rm rollama:latest
else
    echo "No orphaned docker images found"
    echo "Cleaning up local docker images"
    # Remove specific local images
    docker image rm rollama:${srvc_ver}
    docker image rm rollama:latest
fi
