# 自动健康打卡

## 使用说明

- ### 直接运行

1. 把需要打卡的学号和密码写入“账号.csv”，可以写入多个，一行一个
2. `pip3 -r requirements.txt`
3. `python3 自动健康打卡.py`（只运行一次） 或 `enable_cron=1 python3 自动健康打卡.py`（启用定时任务）

- ### 容器中运行（推荐用于服务器）

1. 把需要打卡的学号和密码写入“账号.csv”，可以写入多个，一行一个
2. `docker pull dingyang666/punchin`
3. `docker run --name punchin -d -v /path/账号.csv:/workdir/账号.csv dingyang666/punchin`
4. 可以通过 `docker logs -f punchin` 查看日志
