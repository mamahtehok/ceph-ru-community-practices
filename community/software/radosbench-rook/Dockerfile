# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install required packages
RUN apt-get update && \
    apt-get install -y \
    ceph-common \
    vim \
		python3 \
    python3-yaml \
    python3-lxml \
    && rm -rf /var/lib/apt/lists/*

ADD cbt-rook/ /cbt-rook

# Reset the frontend to the default
ENV DEBIAN_FRONTEND=

# Default command to run when the container starts
CMD ["bash"]
