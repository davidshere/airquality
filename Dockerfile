FROM python:3.7.3

RUN pip install -r requirements.txt

WORKDIR /app
COPY airquality/ /app/

CMD cd /app && flask run