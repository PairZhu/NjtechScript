# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import time
import re
import random
import openai

# chatgpt最多尝试次数
max_try = 5
# 必须包含字段“PHPSESSID”
cookie = '考试系统的cookie'
# 考试页面url参数（必须是已经开始考试的页面），根据考试科目的不同，自行调整（当前值为防诈骗答题的参数）
urlParams = 'ksmk=10000004601&aa=bb'
# OpenAI官网的API_KEY
openai.api_key = '你的API KEY'
# 调教对话，用于让chatgpt按照设定的格式回答问题，根据考试的不同，自行调整（尤其是第一行，考试的科目要改）
message = [
    {"role": "system", "content": "下面请你完成一个中国大学生防诈骗的试题，题目类型为单选或者多选题。我每次会给你一个问题，你只要给出正确答案的序号，如果是多选则用英文逗号隔开序号，此外不要输出其他的内容。"},
    {"role": "user",
     "content": "(单项选择)出小明接到一个陌生电话，对方称小明的朋友用小明的身份做担保，向他的公司借了30000块，现在他的朋友联系不上，小明如果不还钱，他会到学校来闹事。为防止打击报复，小明应该迅速筹钱，帮朋友还债。\n62256. 错\n62255. 对"},
    {"role": "assistant", "content": "62256"},
    {"role": "user", "content": "(多项选择)下列说法正确的是：\n62094. 凡是通过网络发送“逮捕令、通缉令”等法律文书，冒充“公检法”要求配合调查、自证清白的，都是诈骗；\n62093. 未知链接不点击，不明电话不轻信，个人信息不透露，转账汇款多核实；\n62096. 凡是自称是公安机关人员的电话都值得被相信，我们应当积极配合。\n62095. 凡是要求通过网络媒介做笔录、做资金审查的，都是诈骗；"},
    {"role": "assistant", "content": "62094,62093,62095"},
]
# 国内的代理地址，如果挂了，自行改代码走网络代理来代替
openai.api_base = 'https://chat-gpt.aurorax.cloud/v1'

rightAnswer = {}
wrongAnswer = {}

# 从配置文件中读取题库
try:
    with open('questions.json', 'r') as f:
        rightAnswer = json.load(f)
except:
    print('题库文件不存在，跳过')

try:
    with open('wrong.json', 'r', encoding='utf-8') as f:
        wrongAnswer = json.load(f)
except:
    print('错题库文件不存在，跳过')

def aiAnswer(question,qId):
    prompt = f"({question['type']}){question['title']}"
    for optionId,val in question['options'].items():
        prompt += f"\n{optionId}. {val}"
    # 优先从题库中查找答案
    if qId in rightAnswer:
        print('题库中找到答案')
        return rightAnswer[qId]
    answer = ''
    for i in range(max_try):
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[*message, {"role": "user", "content": prompt}],
                timeout=10,
            )
            answer = completion.choices[0].message['content']
            # 保证多选题答案的一致性
            answer = re.findall(r"\d+", answer)
            answer.sort()
            answer = ','.join(answer)
            if qId in wrongAnswer:
                if answer in wrongAnswer[qId]['options']:
                    print('AI回答错误，自动随机选择')
                    answer = random.choice(list(question['options'].keys()))
                    
            return answer
        except:
            print('OpenAI API调用失败，正在重试')
            time.sleep(3)
            continue
    # 超过重试次数后仍失败则随机选择
    print('OpenAI API超过重试次数，自动随机选择')
    answer = random.choice(list(question['options'].keys()))
    return answer

def getJSVar(var,str):
    resStr=re.findall(r"var +{} *= *([^;\n]*)".format(var),str)[0]
    return eval(resStr)

def finishExam():
    examUrl = 'http://exam.njtech.edu.cn'
    examHeaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Cookie': cookie
    }
    pageUrl = examUrl + f"/Home/Zxks/index?{urlParams}"
    response = requests.get(pageUrl,headers=examHeaders)
    soup = BeautifulSoup(response.content,"html.parser")
    jsCode=''
    questions=[]
    questionDict={}
    ksmk=''
    try:
        jsCode = soup.select('body > script:nth-child(9)')[0].string
        questions=getJSVar('questions',jsCode)
        paper_id=getJSVar('paper_id',jsCode)
        ksmk=getJSVar('ksmk',jsCode)
    except:
        print('试卷题目获取失败')

    answer = []
    index = 0
    for question in questions:
        index += 1
        print(f'正在回答第{index}题：')
        options = {}
        for option in question['optAry']:
            options[option['id']] = option['discription']
        qId = question['id']
        question = {
            'title':question['title'],
            'type':question['type_info'],
            'options': options
        }
        answer_str = aiAnswer(question, qId)
        questionDict[qId]={
            'question': question,
            'answer': answer_str
        }
        answer.append({'id': qId, 'option':answer_str})
        print(f'答案：{answer_str}')

    qIdArr = list(map(lambda question: question['id'],questions))
    examPostData= {
        'qIdAry': json.dumps(qIdArr),
        'type': '2',
        'paper_id': paper_id,
        'ksmk': ksmk,
        'data': json.dumps(answer),
    }
    response = requests.post(examUrl+'/Home/Question/addUserAnswers1',headers=examHeaders,data=examPostData)
    res = json.loads(response.text)
    try:
        score=res['info']['score']
    except:
        return {'msg':'答案提交失败','score': 0,'success': False,'response':res}
    questionList = res['info']['question']
    for qRes in questionList:
        questionDict[qRes['id']]['correct'] = qRes['correct'] == 0
    return {'msg':'答案提交成功','score': score,'success': True,'data':questionDict,'response':res}


print('开始答题。。。')
res = finishExam()
if not res['success']:
    print(res['msg'])
    exit()

print(f"答题成功，得分：{res['score']}")
print('保存正确答案和错误中。。。')

questionDict = res['data']

for qId in questionDict:
    question = questionDict[qId]
    if question['correct']:
        rightAnswer[qId] = question['answer']
    else:
        newValue = wrongAnswer.get(qId,{'question':question['question'],'options':[]})
        newValue['options'].append(question['answer'])
        wrongAnswer[qId] = newValue


with open('questions.json','w',encoding='utf-8') as f:
    f.write(json.dumps(rightAnswer,indent=4,ensure_ascii=False))

with open('wrong.json','w',encoding='utf-8') as f:
    f.write(json.dumps(wrongAnswer,indent=4,ensure_ascii=False))

print('保存成功')
