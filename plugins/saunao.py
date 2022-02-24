import nonebot
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
        imginfo = await saucenaoSearch(url, SAUCEURL)
        #print(imginfo)
        if not imginfo :
            await bot.send(event, "没有找到QAQ")
            return
        for iter in imginfo:
            simp = iter['similarity']
            thum = iter['thumbnail']
            creator = str(iter['creator'])
            if creator[0] == '[':
                creator = str(creator)[1:-1].strip()
            ans = '作者：' + creator + "\n相似度：" + simp
            if iter['type'] == 'doujin':
                eng_name = iter['eng_name']
                jp_name = iter['jp_name']
                print(creator)
                if jp_name:
                    ans += '\n本子名称：' + jp_name.strip()
                else:
                    ans += '\n本子名称：' + eng_name.strip()
                ans += '\n' + "[CQ:image,file=" + thum + ",cache=1]"
                await bot.send(event, ans)
            elif iter['type'] == 'pic':
                pixiv_url = iter['pixiv_url']
                ans += '\n链接：'+ pixiv_url + "\n[CQ:image,file=" + thum + ",cache=1]"
                await bot.send(event, ans)