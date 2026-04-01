FROM scitrera/dgx-spark-pytorch-runtime:2.10.0-v2-cu131

# Install ffmpeg for audio transcription (Whisper)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Install all project dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Set working directory
WORKDIR /workspace

# Expose port 8086
EXPOSE 8086

# Default command - run Django server on port 8086 (can be overridden)
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8086"]
