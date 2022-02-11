from email import message
import aiocqhttp
from nonebot import CommandSession, MessageSegment
import nonebot
import re
import json
from plugins.utils import *

APIKEY = 'f2cddb0d913ab5135c6f848e1fe0b8c1a2a61ded'

SAUCEURL = 'https://saucenao.com/search.php?\
api_key=f2cddb0d913ab5135c6f848e1fe0b8c1a2a61ded\
&output_type=2&\
testmode=1&\
dbmaski=32768&\
db=5&\
numres=5&\
url='

'''
https://saucenao.com/search.php?apikey=f2cddb0d913ab5135c6f848e1fe0b8c1a2a61ded&output_type=2&testmode=1&dbmaski=32768&db=5&numres=5&url=https://gchat.qpic.cn/gchatpic_new/1320265781/3967125332-3219453593-6C581F8F95E9E20AD31D2CB632FA08C7/0?term=3,subType=0
'''

bot = nonebot.get_bot()

@bot.on_message()
async def _(event):
    info = await bot.get_login_info()
    id = info['user_id']
    if ('[CQ:at,qq=' + str(id) +']' in event['raw_message'] or event['message_type'] == 'private')\
         and '[CQ:image' in event['raw_message']:

        await bot.send(event, message='正在搜索。。。')
        CQimg = getCQimgInMesg(str(event['message']))
        url = getImgUrlInCQ(CQimg)
        imginfo = saucenaoSearch(url, SAUCEURL)
        for iter in imginfo:
            simp = iter['similarity']
            thum = iter['thumbnail']
            if iter['type'] == 'doujin':
                eng_name = iter['eng_name']
                jp_name = iter['jp_name']
                creator = str(iter['creator'])[1:-1].strip()
                print(creator)
                ans = '作者：' + creator
                if jp_name:
                    ans += '\n 本子名称：' + jp_name.strip()
                else:
                    ans += '\n 本子名称：' + eng_name.strip()
                ans += '\n' + "[CQ:image,file=" + thum + ",cache=1]"
                await bot.send(event, ans)
            elif iter['type'] == 'pic':
                continue
                pid = iter['pid']
                author = iter['author']
                img = setuMesg(iter['url'])
                ans = '作者：' + author + '\npixiv id：' + pid + '\n相似度：' + simp + '\n'
                await bot.send(event, ans)
                await bot.send(event, img)