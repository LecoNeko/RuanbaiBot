import aiocqhttp
import nonebot
import config

@nonebot.on_websocket_connect
async def _(event: aiocqhttp.Event):
    bot = nonebot.get_bot()
    await bot.send_private_msg(user_id = config.SUPERUSERS, message = '软白上线惹≥w≤')

