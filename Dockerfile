# Use an official Python base image
FROM python:3.12-slim

# Use bash for all RUN commands (needed for 'source')
SHELL ["/bin/bash", "-c"]

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/miniforge/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Install Miniforge (lightweight Conda)
RUN curl -fsSL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -o /tmp/miniforge.sh \
    && bash /tmp/miniforge.sh -b -p /opt/miniforge \
    && rm /tmp/miniforge.sh

# Copy your code into the container
WORKDIR /app
COPY . /app

# Create Conda environment from environment.yaml
RUN source /opt/miniforge/etc/profile.d/conda.sh \
    && conda env create -f ci_environment.yaml \
    && conda clean -afy

# Activate environment and install GOATS
RUN echo "source /opt/miniforge/etc/profile.d/conda.sh && conda activate goats-dev" > ~/.bashrc
RUN /bin/bash -c "source /opt/miniforge/etc/profile.d/conda.sh && conda activate goats-dev && pip install . && goats install --ci"

# Expose port for Render
EXPOSE $PORT

# Start GOATS with internal Redis and single HTTP worker
# Use $PORT injected by Render
CMD /bin/bash -c "\
    source /opt/miniforge/etc/profile.d/conda.sh && \
    conda activate goats-dev && \
    echo 'GOATS starting on Render port: '$PORT && \
    goats run -w 1 --addrport 0.0.0.0:$PORT \
"
