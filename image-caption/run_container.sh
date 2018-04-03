#!/bin/bash
# Start docker container
comm="nvidia-docker run -t --rm --shm-size 8G -v $(pwd):/workspace/image_caption -w /workspace/image_caption image-caption /workspace/image_caption/init_container.sh && $@"
echo "NV_GPU=$NV_GPU"
echo "Runnning command $comm"
cont=$(nvidia-docker run -t --rm --shm-size 8G -v $(pwd):/workspace/image_caption -w /workspace/image_caption image-caption /workspace/image_caption/init_container.sh $@)
echo "Container $cont stopped"
docker logs $cont