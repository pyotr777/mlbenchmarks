#!/bin/bash
# Start Docker container with installed tensorboard.
# Start Tensorboard inside container with: tensorboard --logdir=/host/runs/<logdir> --port=8888
nvidia-docker run -ti -p 8888:8888 -v $(pwd):/host --rm tensorflow/tensorflow:latest-gpu /bin/bash
