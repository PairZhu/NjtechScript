FROM python

WORKDIR /workdir
COPY . .

RUN pip3 install -r requirements.txt

ENV enable_cron=1

CMD [ "python3","-u","自动健康打卡.py"]