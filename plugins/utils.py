import asyncio
from time import localtime
import httpx
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from nonebot import on_command, CommandSession, MessageSegment
import requests
import re
import time
from io import BytesIO
import os
from PIL import Image

from config import OSU_API_KEY

SETUAPI = r"https://api.lolicon.app/setu/v2?"
HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}


def getWebImage(url:str, pic_path:str):
    '''
    抓取网站全屏截图
    '''
#chromedriver的路径
    chromedriver = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"
    os.environ["webdriver.chrome.driver"] = chromedriver
#设置chrome开启的模式，headless就是无界面模式
    chrome_options = Options()
    chrome_options.add_argument('headless')
    driver = webdriver.Chrome(chromedriver,chrome_options=chrome_options)
    driver.get(url)
    time.sleep(1)
#用js获取页面的宽高，如果有其他需要用js的部分也可以用这个方法
    width = driver.execute_script("return document.documentElement.scrollWidth")
    height = driver.execute_script("return document.documentElement.scrollHeight")
    print(width,height)
#将浏览器的宽高设置成刚刚获取的宽高
    driver.set_window_size(width, height)
    time.sleep(1)
#截图并关掉浏览器
    driver.save_screenshot(pic_path)
    driver.close()


async def async_request(url, params={}):
    async with httpx.AsyncClient() as client:
        res = await client.get(url, params=params)
    return res

def rmsgToJson(msg: str)->dict:
    if not msg:
        return None
    msg = msg[msg.find('data')+5:]
    i = len(msg)-1
    j = 0
    while msg[i]!= '}':
        i-=1
        j-=1
    msg = msg[:j]
    msg = re.sub('&#44;', ',', msg)
    msg = re.sub(';', ',', msg)
    return json.loads(msg)


def gene_Aa_ReStr(String:str):
    res = ''
    for i in String:
        #print(type(i))
        res = res +'['+ i.lower() + i.upper() + ']'
    return res

def imgsrcToPILobj(imgsrc):
    imgres = requests.get(imgsrc)
    img = Image.open(BytesIO(imgres.content))
    return img

def makeThumbnail(img: Image, base_width, filename):
    '''
    等比例缩放图片
    '''
    height = int(img.size[1] * base_width / float(img.size[0]))
    thumbnail = img.resize((base_width, height), Image.ANTIALIAS)
    thumbnail_path = os.path.join(os.path.dirname(__file__),'temp')
    thumbnail_path = os.path.join(thumbnail_path, filename)
    thumbnail.save(thumbnail_path)
    return thumbnail_path.replace('\\','/')

def MessageLocalImage(path:str):
    '''
    转换为本地文件传输协议的CQ码
    '''
    path = path.replace('\\','/')
    # path.replace('\\','/')
    return '[CQ:image,file=file:///' + path + ']'

def pathRenameByRange(path: str):
    filenames = os.listdir(path)
    siz = len(filenames)
    for i in range(siz):
        file = os.path.join(path, filenames[i])
        filename, filetype = os.path.splitext(file)
        os.rename(file, os.path.join(path,str(i))+str(filetype))

def pidGetPixivurl(pid):
    '''
    用pixivid拼接URL
    '''
    if not pid:
        return None
    return "https://pixiv.net/i/" + str(pid)

def setuMesg(setu_url: str):
    '''
    传入图片url得到可以通过bot.send()发送的MessageSegment
    '''
    # pic
    # imgurl = js['data'][0]['urls']['original'].replace('cat', 're', 1)
    # await session.send("[CQ:image,file=" + imgurl + ",cache=1]")
    print(setu_url)
    return MessageSegment.image(setu_url)
    
