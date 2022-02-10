from email import message
import aiocqhttp
from nonebot import CommandSession, MessageSegment
import nonebot
import re
from plugins.utils import *

bot = nonebot.get_bot()

@bot.on_message()
async def _(event):
    info = await bot.get_login_info()
    id = info['user_id']
    if '[CQ:at,qq=' + str(id) +']' in event['raw_message'] and '[CQ:image' in event['raw_message']:
        await bot.send(event, message='正在搜索。。。')
        CQimg = getCQimgInMesg(str(event['message']))
        url = getImgUrlInCQ(CQimg)
        imginfo = saucenaoSearch(url)
        for iter in imginfo:
            simp = iter['simp']
            pid = iter['pid']
            author = iter['author']
            img = setuMesg(iter['url'])
            ans = '作者：' + author + 'pixiv id：' + pid + '相似度：' +simp
            await bot.send(event, ans)
            await bot.send(event, img)
