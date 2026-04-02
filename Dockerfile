FROM scitrera/dgx-spark-vllm:0.17.0-t5

# Install ffmpeg for audio transcription (Whisper)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Install all project dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# DO NOT upgrade transformers - vLLM 0.17.0 was built against a specific version
# Upgrading breaks internal imports (ALLOWED_ATTENTION_LAYER_TYPES, Gemma3Config, etc.)
# If Qwen3.5 MoE support is needed, use a newer vLLM base image instead

# Set working directory
WORKDIR /workspace



# Expose port 8086
EXPOSE 8086

# Default command - run Django server on port 8086
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8086"]
