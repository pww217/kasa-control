FROM python:3.11.5-slim

COPY . /app/

WORKDIR /app

RUN python -m pip install --upgrade pip \
&& pip install -r requirements.txt

CMD ["python", "controller.py"]