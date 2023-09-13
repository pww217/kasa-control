FROM python:3.11.5-slim

COPY . .

RUN python -m pip install --upgrade pip \
&& pip install -r requirements.txt \
&& rm webhook.py presents.yaml

CMD ["python", "controller.py"]
