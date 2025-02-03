FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV NAME World

ENV MY_VAR=value

# CMD ["python", "app.py"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]