FROM python:3.11.4-slim

COPY . .

RUN python -m pip install --upgrade pip \
&& pip install -r requirements.txt

CMD ["python", "controller.py"]