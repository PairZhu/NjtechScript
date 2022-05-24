import requests
from bs4 import BeautifulSoup

login_url="https://i.njtech.edu.cn"

s = requests.Session()
r = s.get(login_url)

soup = BeautifulSoup(r.content,"html.parser")
lt0 = soup.find('input',attrs={'name':'lt'})['value']
execution0 = soup.find('input',attrs={'name':'execution'})['value']

post_data={
    'username': '',#学号
    'password': '',#密码
    'channelshow': '中国移动',#中国移动，中国电信
    'channel': '@cmcc',
    'lt': lt0,
    'execution': execution0,
    '_eventId': 'submit',
    'login': '登录',
}

post_header={
    'Accept': '*/*',
    'Accept-Language': 'zh-cn',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
}

if post_data['channelshow'] == '中国电信':
    channel = '@telecom'

s.post(r.url, data=post_data, headers=post_header)
