# Use an official Python base image
FROM python:3.12-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/miniforge/bin:$PATH"
ENV PORT=10000

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
RUN /bin/bash -c "source /opt/miniforge/etc/profile.d/conda.sh && conda activate goats-dev && pip install ."

# Expose port for Render
EXPOSE $PORT

# Start Redis and GOATS
CMD /bin/bash -c "redis-server --bind 0.0.0.0 --port 6379 --daemonize yes && source /opt/miniforge/etc/profile.d/conda.sh && conda activate goats-dev && goats install --ci && goats run --addrport 0.0.0.0:$PORT"
