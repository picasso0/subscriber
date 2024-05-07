FROM python:3.9
RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app

# CMD ["tail","-f","/dev/null"]

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80" ,"--workers","4"]
#CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]