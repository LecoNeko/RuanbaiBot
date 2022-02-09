from nonebot import on_command, CommandSession

@on_command('weather', aliases=['天气','查天气'])
async def weather(session: CommandSession):
    city = session.get('city', prompt='你想查哪个城市呢？')
    date = session.get('date', prompt='你想查哪一天呢？')
    await session.send('你查询的城市是' + city)
    await session.send('你查询的日期是' + date)

@weather.args_parser
async def _(session: CommandSession):
    if session.is_first_run:
        return
    
    if session.current_key == 'date':
        if len(session.current_arg_text)!=8 and session.current_arg_text.isdigit():
            session.pause('格式错误惹，请重新输入')

