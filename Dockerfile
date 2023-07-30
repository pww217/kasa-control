FROM python:3.12.0b4-bookworm

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]