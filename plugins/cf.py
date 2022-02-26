import asyncio
from nonebot import on_command, CommandSession, Message
from plugins.utils import *


HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}

fk = '命令不合法'

@on_command(name='cf', patterns=gene_Aa_ReStr('codeforces'), privileged = True)
async def _(session: CommandSession):
    cur_text = session.current_arg_text.strip().split()
    Method = cur_text[0]
    #print('\n\n\n')
    #print(Method)
    #print(User)
    if re.fullmatch(gene_Aa_ReStr('info'), Method):
        User = cur_text[1]
        Info = await CodeforcesInfo(User)
        if not Info or Info == '网络错误':
            await session.send(Info)
        ans = ''
        ans += Info['titlePhoto'] + '\n'
        ans += 'Name: ' + Info['name'] + '\n'
        if Info['country']:
            ans += 'Country: ' + Info['country'] + '\n'
        ans += 'Rating: ' + str(Info['rating']) + ' ' + Info['rank'] + '\n'
        ans += 'MAXRating: ' +  str(Info['maxRating']) + ' ' + Info['maxRank']
        await session.send(ans)
    elif re.fullmatch(gene_Aa_ReStr('rtcg'), Method):
        User = cur_text[1]
        cnt = 1
        if len(cur_text) > 3:
            await session.send(fk)
        if len(cur_text)== 3:
            cnt = int(cur_text[2])
        ans = await CodeforcesRating(User, cnt)
        await session.send(ans)
    elif re.fullmatch(gene_Aa_ReStr('lastsb'), Method):
        User = cur_text[1]
        ans = await CodeforcesLastSubmission(User)
        await session.send(ans)
    elif re.fullmatch(gene_Aa_ReStr('status'), Method):
        User = cur_text[1]
        ans = await CodeforcesStatus(User)
        await session.send(ans)





