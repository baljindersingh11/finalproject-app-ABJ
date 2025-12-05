FROM public.ecr.aws/docker/library/python:3.9-slim

WORKDIR /app


RUN mkdir -p /app/static


RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 81


CMD ["python3", "app.py"]
