FROM python:3.12
WORKDIR /app
COPY requirements.txt .
COPY runserver.sh .
RUN pip install --no-cache-dir -r requirements.txt
COPY testing_service .
EXPOSE 8000
RUN ["chmod", "+x", "/app/runserver.sh"]
ENTRYPOINT ["sh", "/app/runserver.sh"]