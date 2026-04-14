# NVIDIA PyTorch container with CUDA support
FROM nvcr.io/nvidia/pytorch:26.03-py3

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /workspace

# Copy requirements first (without torch to avoid conflicts)
COPY requirements.txt .

# Remove torch from requirements.txt to avoid reinstallation
RUN grep -v '^torch' requirements.txt > requirements_filtered.txt && \
    mv requirements_filtered.txt requirements.txt

# Install project dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY manage.py .
COPY chatbot_study chatbot_study/
COPY accounts accounts/
COPY templates templates/
COPY .env .

# Expose port 8086
EXPOSE 8086

# Required GPU runtime flags: --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864
# Run migrations and start Django server with GPU support
CMD ["sh", "-c", "python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8086"]