from nonebot import on_command, CommandSession
from sympy import false

@on_command('喵一个', aliases=['nya~','nya'], only_to_me = False)
async def _(session: CommandSession):
    await session.send('喵~')