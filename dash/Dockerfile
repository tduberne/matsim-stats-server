FROM python:3.7-alpine

RUN mkdir /app/
WORKDIR /app/

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Volume to mount the code, to allow live update of Dashboard for development and testing
# (not to use in production!)
VOLUME /app/src/

EXPOSE 8050

CMD ["python", "/app/src/app.py"]