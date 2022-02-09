from nonebot import on_command, CommandSession

@on_command('喵一个', aliases=['nya~','nya'])
async def _(session: CommandSession):
    await session.send('喵~')