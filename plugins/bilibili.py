import nonebot
from plugins.utils import *

bot = nonebot.get_bot()


VIEWAPI = 'https://api.bilibili.com/x/web-interface/view?bvid='

@bot.on_message()
async def _(event):
    msg = event['raw_message']
    BV = re.findall('[Bb][Vv][0-9a-zA-Z]+', msg)
    if BV:
        BV = BV[0]
        if BV[-1]=='?':
            BV = BV[:-1]
        url = VIEWAPI + str(BV)
        
        res = await async_request(url)
        res = res.json()
       # print('\n\n\n')
        #print(url)
       # print(res)
        res = res['data']
        
        title = res['title']
        upz = res['owner']['name']
        try:
            pic = MessageLocalImage(makeThumbnail(imgsrcToPILobj(res['pic']), 300, 'bilibili_temp.png'))
        except:
            pic = ''
        stat = res['stat']
        view = stat['view']
        danmaku = stat['danmaku']
        reply = stat['reply']
        like = stat['like']
        coin = stat['coin']
        favorite = stat['favorite'] # 收藏
        share = stat['share']
        
        ans = pic + '\n'
        ans += title + '\n'
        ans += 'up主：' + str(upz) + '\n'
        ans += '播放：' + str(view) + ' '
        ans += '弹幕：' + str(danmaku) + '\n'
        ans += '点赞：' + str(like) + ' '
        ans += '投币：' + str(coin) + ' '
        ans += '收藏：' + str(favorite) + '\n'
        ans += '链接：' + 'https://www.bilibili.com/video/' + str(BV) 
        await bot.send(event, ans)





