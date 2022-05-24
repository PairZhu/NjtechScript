# 图书馆预约
import json
import time
import random
import traceback
import datetime
import requests
from bs4 import BeautifulSoup

def sendMessage(msg):
    print(msg)
    # 如果需要通知提醒，请在此处添加邮箱、或QQ机器人、微信企业号、微信公众号、pushplus等通知提醒功能的代码

def appointmentLibrary(username, password):
    try:
        baseUrl = 'https://ehall.njtech.edu.cn'
        session = requests.Session()
        response = session.get(baseUrl)
        loginUrl = response.url
        soup = BeautifulSoup(response.content, "html.parser")
        lt0 = soup.find('input', attrs={'name': 'lt'})['value']
        execution0 = soup.find('input', attrs={'name': 'execution'})['value']

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
        response = session.post(loginUrl, data=loginPostData, allow_redirects=False)
        response = session.get(response.headers['Location'])

        entryUrl = baseUrl+'/infoplus/form/TSGXY/start'
        response = session.get(entryUrl)

        soup = BeautifulSoup(response.content, "html.parser")
        csrfToken = soup.find('meta', attrs={'itemscope': 'csrfToken'})['content']
        idc = soup.find('input', attrs={'id': 'idc'})['value']
        release = soup.find('input', attrs={'id': 'release'})['value']

        response = session.post(entryUrl, data={
            "idc": idc,
            "release": release,
            "csrfToken": csrfToken,
            "formData": json.dumps({
                '_VAR_URL': entryUrl,
                '_VAR_URL_Attr': None,
            }),
        })
        formUrl = response.url
        stepId = formUrl.split('form/')[1].split('/')[0]

        response = session.post(baseUrl+'/infoplus/interface/render',
                                headers={'referer': formUrl},
                                data={
                                    "stepId": stepId,
                                    "instanceId": "",
                                    "admin": "false",
                                    "rand": random.random()*999,
                                    "width": "1550",
                                    "lang": "zh",
                                    "csrfToken": csrfToken,
                                })
        formData=json.loads(response.text)['entities'][0]['data']
        formData['_VAR_ENTRY_NAME'] = "图书馆预约申请"
        formData['_VAR_ENTRY_TAGS'] = "预约服务"
        formData['fieldXq_Name'] = "逸夫图书馆" # 逸夫图书馆 或 浦江图书馆
        formData['fieldXq'] = "1" # 1（逸夫） 或 2（浦江）
        formData['_VAR_URL'] = formUrl
        formData['fieldSFLG'] = ""

        targetDay = datetime.date.today()

        targetTimeStamp = str(int(time.mktime((targetDay.year, targetDay.month, targetDay.day, 0, 0, 0, 0, 0, 0))))
        formData['fieldJzzt'] = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'][targetDay.weekday()]
        formData['fieldDateTo'] = targetTimeStamp
        formData['fieldDateFrom'] = targetTimeStamp
        formData['fieldYyy'] = "0" # 已预约人数
        formData['fieldKyy'] = "1000" # 可预约人数
        formData['fieldYyzt'] = "1"

        postData = {
            "stepId": stepId,
            "actionId": 1,
            "formData": json.dumps(formData),
            "timestamp": int(time.time()),
            "boundFields": "fieldDateFrom,fieldDateTo,fieldSFLG,fieldJzzt,fieldJzr,fieldSfz,fieldGh,fieldKyy,fieldLxfs,fieldXq,fieldYyy,fieldYyzt",
            "csrfToken": csrfToken,
            "lang": "zh",
            "nextUsers": "{}"
        }
        response = session.post(baseUrl+'/infoplus/interface/listNextStepsUsers',data={**postData,"rand": random.random()*999})
        response = session.post(baseUrl+'/infoplus/interface/doAction',data={**postData,"rand": random.random()*999})
        result = json.loads(response.content)
        try:
            if result['entities'][0]['name']=='申请人确认':
                sendMessage("图书馆预约成功！\n请手动进入办事大厅进行申请人确认\n数据如下：\n"+json.dumps(result, indent=0, separators=(', ', ': '), ensure_ascii=False)[2:-1])

                # 申请人确认，不用抢名额，可以手动确认
                # try:
                #     time.sleep(2)
                #     postData["actionId"] = 2
                #     response = session.post(baseUrl+'/infoplus/interface/listNextStepsUsers',data={**postData,"rand": random.random()*999})
                #     response = session.post(baseUrl+'/infoplus/interface/doAction',data={**postData,"rand": random.random()*999})
                #     print("申请人确认成功！")
                # except Exception as e:
                #     print("申请人确认失败！\n报错信息如下：\n"+traceback.format_exc())

                return True

            else:
                sendMessage("❗❗❗\n图书馆预约失败！\n数据如下：\n"+json.dumps(result, indent=0, separators=(', ', ': '), ensure_ascii=False)[2:-1])
                return False
        except Exception as e:
            sendMessage("❗❗❗\n图书馆预约失败！\n数据如下：\n"+json.dumps(result, indent=0, separators=(', ', ': '), ensure_ascii=False)[2:-1])
            return False

    except Exception as e:
        sendMessage("❗❗❗\图书馆预约失败！\n报错信息如下：\n"+traceback.format_exc())
        return False


# 自动重试
def retryAppointment(username, password, maxRetryTimes=3):
    for i in range(maxRetryTimes+1):
        i and sendMessage("图书馆预约第"+str(i)+"次重试...")
        if appointmentLibrary(username, password):
            return True
        time.sleep(random.randint(1,2))
    sendMessage("图书馆预约失败！已超过最大重试次数")
    return False


retryAppointment('你的学号', 'i南工的登录密码')

