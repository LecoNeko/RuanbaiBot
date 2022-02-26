import aiocqhttp
import nonebot
import config

bot = nonebot.get_bot()
group_stat = {}

@nonebot.on_websocket_connect
async def _(event: aiocqhttp.Event):
    await bot.send_private_msg(user_id = config.SUPERUSERS, message = '软白上线惹≥w≤')

@bot.on_message()
async def grouprepeat(event):
    if event['message_type'] != 'group':
        return
    group_id = str(event['group_id'])
    msg = event['message']
    if not group_stat.get(group_id) or msg != group_stat.get(group_id)[0]:
        group_stat[group_id] = [msg, 0]
    group_stat[group_id][1] += 1
    if group_stat[group_id][1] == config.REPEAT_TIME:
        await bot.send(event, msg)