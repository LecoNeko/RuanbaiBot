import asyncio
from nonebot import on_command, CommandSession, Message
import nonebot
from plugins.utils import *
import config
import random

HELP_INFO_ALL =\
'''一只软白写的软白~~~~~
功能列表：
    * setu：no res
    * saucenao搜图：@软白 + 你要搜的图片
    * osu：osu玩家信息、recentplayed之类的
    * cf：codeforces Info, states, last submission, rating change, etc...
    * b站：暂时只有你发BV号窝发视频信息(
    * feed：用!feed []给写代码的软白发消息
'''

HELP_SETU =\
'''send a random taged Setu to sender. R18 only can be applied at WHITEGROUPLIST
* eg:'[bot nickname] + 来张 + (r18) + [tag1 & tag2 | tag3 |tag4]  + 涩图'
* 软白来张涩图
* 软白来3张涩图
* 软白来三张涩图
* 软白来两张白丝&萝莉涩图
'''

HELP_OSU =\
'''施工中
> !o info [userid] [mode]
> !o re [userid]
'''

HELP_CF=\
'''Stared with '!cf' to apply it
* info: 查询一些例如rating, rank, maxRating, maxRank的基本信息
	* eg: '!cf info [cfId]'
	* !cf info tourist

* rtcg: 最近比赛的rating变化
	* eg:'!cf rtcg [cfId] ([cnt])'
	* !cf rtcg tourist 5
	* !cf rtcg tourist

* lastsb: 上一次提交
	* eg:'!cf lastsb [cfId]'
	* !cf lastsb tourist

* statues: 最近的5次提交
	* eg:'!cf statues [cfId]'
	* !cf statues tourist

* contest: 展示在contest的未开始的比赛
	* eg:'!cf rect'

* pb: 看看CF某道题在洛谷的题面
	* eg:'!cf pb CF1641C'
'''

@on_command(name='帮助', patterns=gene_Aa_ReStr('help'), privileged = True, only_to_me=True)
async def _(session: CommandSession):
    cur_text = session.current_arg_text.replace('help','').strip().split()
    #print(cur_text)
    if(len(cur_text) == 0):
        #print(1)
        await session.send(HELP_INFO_ALL)
        return 
    Method = cur_text[0]
    if re.fullmatch(gene_Aa_ReStr('setu'), Method):
        await session.send(HELP_SETU)
    elif re.fullmatch(gene_Aa_ReStr('osu'), Method):
        await session.send(HELP_OSU)
    elif re.fullmatch(gene_Aa_ReStr('cf'), Method):
        await session.send(HELP_CF)
    else:
        await session.send('软白还没写这个帮助呢~~~')

    return


@on_command(name='回执', patterns=gene_Aa_ReStr('feed'), only_to_me=True)
async def _(session: CommandSession):
    cur_text = session.current_arg_text.strip().replace('feed ','')
    cur_text = 'Sender({},{})：\n'.format(session.event['sender']['user_id'],session.event['sender']['nickname'])+cur_text
    bot = nonebot.get_bot()
    await bot.send_private_msg(user_id = config.SUPERUSERS, message = cur_text)
