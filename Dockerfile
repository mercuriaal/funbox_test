FROM python:latest

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . /app
CMD ["flask", "run", "--host", "0.0.0.0"]