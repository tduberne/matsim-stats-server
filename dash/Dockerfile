FROM python:3.7

RUN mkdir /app/
WORKDIR /app/

COPY requirements.txt ./
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

# Volume to mount the code, to allow live update of Dashboard for development and testing
# (not to use in production!)
VOLUME /app/src/

EXPOSE 8050

CMD ["gunicorn", "-w", "1", "--pythonpath" , "/app/src/" , "-b" , ":8050" , "--access-logfile" , "-" , "--log-level" , "debug" , "app:app.server"]
