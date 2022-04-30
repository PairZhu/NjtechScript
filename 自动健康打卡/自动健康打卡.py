# 自动健康打卡，取上次上传数据作为本次打卡数据
import json
import time
import traceback

import csv
import schedule
import time
import requests
from bs4 import BeautifulSoup
import os


def send_message(msg):
    print(msg)
    # 如果需要通知提醒，请在此处添加邮箱、或QQ机器人、微信企业号、微信公众号、pushplus等通知提醒功能的代码


def healthFill(username, password):
    loginUrl = 'https://u.njtech.edu.cn/cas/login?service=http://pdc.njtech.edu.cn/#/dform/genericForm/wbfjIwyK'
    session = requests.Session()
    # 通过i南工进行登录，获取i南工登录页面
    response = session.get(loginUrl)
    soup = BeautifulSoup(response.content, "html.parser")
    lt0 = soup.find('input', attrs={'name': 'lt'})['value']
    if not lt0:
        send_message('登录页面获取失败')
        return
    execution0 = soup.find('input', attrs={'name': 'execution'})['value']
    loginPostUrl = 'https://u.njtech.edu.cn' + \
        soup.select("#fm2")[0].attrs['action']
    loginPostData = {
        'username': username,
        'password': password,
        'channelshow': '校园内网',
        'channel': 'default',
        'lt': lt0,
        'execution': execution0,
        '_eventId': 'submit',
        'login': '登录',
    }

    # 登录并获取登录后的cookie
    response = session.post(
        loginPostUrl, data=loginPostData, allow_redirects=False)
    loginRedirectUrl = response.headers.get('Location')
    if not loginRedirectUrl:
        send_message('❗❗❗\n健康打卡提交失败！\n登录失败！请检查账号密码')
        return
    ticket = loginRedirectUrl.split('?ticket=')[-1].split('#/')[0]
    pageHeaders = {"Content-Type": "application/json"}
    pageHeaders["Referer"] = "http://pdc.njtech.edu.cn/?ticket={}".format(
        ticket)

    # 获取表单内容（好像用不到）
    # response = session.get(loginRedirectUrl, headers=pageHeaders, allow_redirects=False)

    try:
        # 获取token
        response = session.get("http://pdc.njtech.edu.cn/dfi/validateLogin?ticket={}&service=http://pdc.njtech.edu.cn/#/dform/genericForm/wbfjIwyK".format(
            ticket), headers=pageHeaders, allow_redirects=False)
        token = json.loads(response.content)['data']['token']
        pageHeaders["Authentication"] = token
        # 到此处，登录已完成

        # 获取wid
        response = session.get("http://pdc.njtech.edu.cn/dfi/formOpen/loadFormListBySUrl?sUrl=wbfjIwyK",
                               headers=pageHeaders, allow_redirects=False)
        wid = json.loads(response.content)['data'][0]['WID']

        # 获取历史提交记录
        response = session.get("http://pdc.njtech.edu.cn/dfi/formData/loadFormFillHistoryDataList?formWid={}&auditConfigWid=".format(
            wid), headers=pageHeaders, allow_redirects=False)
        # 取最近一次提交数据，数据的结构和提交所需的结构不完全一致，进行修改后作为此次提交数据
        lastData = json.loads(response.content)["data"][0]
        dataMap = {
            "wid": "",
            "RADIO_KWYTQFSU": "本人知情承诺",   # 知情承诺
            "INPUT_KWYTQFSO": lastData['INPUT_KWYTQFSO'],   # 学号
            "INPUT_KWYTQFSP": lastData['INPUT_KWYTQFSP'],   # 姓名
            "SELECT_KX3ZXSAE": lastData['SELECT_KX3ZXSAE'],  # 学院
            "INPUT_KWYTQFSS": lastData['INPUT_KWYTQFSS'],   # 班级
            "INPUT_KX3ZXSAD": lastData['INPUT_KX3ZXSAD'],   # 手机号
            "INPUT_KWYUM2SI": lastData['INPUT_KWYUM2SI'],   # 辅导员
            "RADIO_KWYTQFSZ": lastData['RADIO_KWYTQFSZ'],   # 当前位置
            "RADIO_KWYTQFT0": lastData['RADIO_KWYTQFT0'],
            # 所在省市区
            "CASCADER_KWYTQFT1": lastData['CASCADER_KWYTQFT1'][1:-1].split(', '),
            "RADIO_KWYTQFT2": lastData['RADIO_KWYTQFT2'],   # 身体状况
            # 下面这两行如果报出现异常一般是健康码行程码过期（一般两周左右会过期一次），需要自己重新打卡一次
            # 健康码
            "ONEIMAGEUPLOAD_KWYTQFT3": lastData['ONEIMAGEUPLOAD_KWYTQFT3'][1:-1].split(', '),
            # 行程码
            "ONEIMAGEUPLOAD_KWYTQFT5": lastData['ONEIMAGEUPLOAD_KWYTQFT5'][1:-1].split(', '),
            "LOCATION_KWYTQFT7": lastData['LOCATION_KWYTQFT7'],  # 定位
        }

        # 构建AMID（不知道有啥意义，可能用于迷惑人，就是个时间戳，前面可能会加一个随机数，但是不加也可以）
        AMID = "AM@"+str(int(time.time()*1000))

        # 获取微信api数据（好像用不到）
        # response = session.get("http://pdc.njtech.edu.cn/dfi/weChatApi/loadWeChatJsSdk?formUrl=http://pdc.njtech.edu.cn/",headers=pageHeaders,allow_redirects=False)

        # 数据校验（好像用不到）
        # postData=json.dumps({
        #     "dataMap": {},
        #     "formWid": wid,
        #     "userId": AMID,
        # })
        # response = session.post('http://pdc.njtech.edu.cn/dfi/formOpen/checkFormFieldIsRisk',data=postData,headers=pageHeaders,allow_redirects=False)

        # 发送表单数据
        postData = json.dumps({
            "auditConfigWid": "",
            "commitDate": time.strftime("%Y-%m-%d", time.localtime()),
            "commitMonth": time.strftime("%Y-%m", time.localtime()),
            "dataMap": dataMap,
            "formWid": wid,
            "userId": AMID,
        })
        response = session.post('http://pdc.njtech.edu.cn/dfi/formData/saveFormSubmitData',
                                data=postData.encode("utf-8"), headers=pageHeaders, allow_redirects=False)
        if json.loads(response.content)["message"] == "请求成功":
            response = session.get("http://pdc.njtech.edu.cn/dfi/formData/loadFormFillHistoryDataList?formWid={}&auditConfigWid=".format(
                wid), headers=pageHeaders, allow_redirects=False)
            send_message("健康打卡提交成功！\n此次提交的数据内容如下：\n"+json.dumps(json.loads(response.content)
                                                                ["data"][0], indent=0, separators=(', ', ': '), ensure_ascii=False)[2:-1])
        else:
            send_message("❗❗❗\n健康打卡提交失败！\n数据提交失败，服务器未响应")
    except Exception as e:
        # 统一处理代码运行抛出的异常，通过通知提醒错误内容
        send_message("❗❗❗\n健康打卡提交失败！\n报错信息如下：\n"+traceback.format_exc())
    print("\n\n\n")

def job():
    csv_reader = csv.reader(open("./账号.csv"))
    send_message("开始进行打卡")

    for line in csv_reader:
        send_message("学号：" + line[0])
        healthFill(line[0],line[1])
    send_message("打卡完成")

if __name__ == "__main__":
    # 程序运行时打卡一次，然后每 12 小时打卡一次
    job()
    enable_cron = os.getenv('enable_cron')
    if enable_cron:
        schedule.every(12).hours.do(job)
        while True:
            schedule.run_pending()
            time.sleep(1)
