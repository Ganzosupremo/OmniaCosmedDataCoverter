FROM python:3.12-slim
WORKDIR /app
COPY ../../requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY ../../ /app
CMD ["streamlit", "run", "services/web/app.py", "--server.address=0.0.0.0"]
