import nonebot
from plugins.utils import *

APIKEY = 'f2cddb0d913ab5135c6f848e1fe0b8c1a2a61ded'

SAUCEURL = 'https://saucenao.com/search.php?\
api_key=fa214bae1efdc7940cf1e7f44d6fac90d3841a1c\
&output_type=2&\
testmode=1&\
dbmaski=32768&\
db=5&\
numres=5&\
url='

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


def getCQimgInMesg(mesg: str):
    '''
    把原始消息中所有图片的CQ码分离出来

    返回CQ码的list
    '''
    mesg = ''.join(mesg.strip().split(' '))
    CQimg = re.findall('\[CQ:image[^\]]*', mesg)
    return CQimg

def getImgUrlInCQ(CQ: list):
    '''
        需要满足
        [CQ:image,
        file=xxxx,
        url=xxxx,subType=x]
        这种格式

        返回url=后面除去]的所有内容
    '''
    ans = []
    for mesg in CQ:
        url = mesg[mesg.find('url') + 4:]
        ans.append(url)
    return ans

def dealNone(dic: dict):
    for key, value in dic.items():
        if not value:
            dic[key] = 'None'
    return dic

async def saucenaoSearch(urllist: list, SAUCEURL: str):
    '''
    传入图片list及SAUCE已经拼接好参数的url进行图片检索
    返回图片检索得到的一些基本信息list
    index_id表：https://saucenao.com/tools/examples/api/index_details.txt
    可以查搜索得到的type，没写
    '''
    info = []
    for img in urllist:
        print("\n\n\n")
        try:
            data = await async_request(url= SAUCEURL + img)
            #data = requests.get(SAUCEURL + img, headers=HEADER).json()
            data = data.json()
            #print(data)
            #print(data["results"])
        except BaseException as e:
            print(e)
            return None
        res = data.get("results", "result")
        first_search_res = 0
        for i in range(3):
            data = res[i]
            #print("\n\n\n")
            #print(data)
            similarity = data["header"]["similarity"]
            thumbnail = data["header"]["thumbnail"] # 缩略图 : url

            if float(similarity) >= 70 or first_search_res == 0:
                first_search_res = 1
                tmp = {}
                tmp["similarity"] = similarity
                tmp["thumbnail"] = thumbnail
                tmp["index_name"] = data["header"]["index_name"]
                tmp["url"] = data["data"].get("ext_urls")
                tmp["creator"] = data["data"].get('creator')
                tmp['title'] = data['data'].get('title')
                tmp['pixiv_url'] = pidGetPixivurl(data['data'].get('pixiv_id'))
                tmp["eng_name"] = data["data"].get('eng_name')
                tmp["jp_name"] = data["data"].get('jp_name')
                tmp["type"] = "pic"
                if tmp["eng_name"] or tmp["jp_name"]:
                    tmp["type"] = "doujin" 
                tmp = dealNone(tmp)
                info.append(tmp)
    #print("\n\n\n")
    #print(info)
    #print("\n\n\n")
    return info