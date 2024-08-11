# import random
# import asyncio
# import json
# from datetime import datetime # 後續要用時間判定所要撈的攻略資料內容
# import requests # 是否需要改成http訪問
# from pprint import pprint

'''
#添加身分組
@clientBot.event
async def on_raw_reaction_add(payload):
    if str(payload.message_id) == rolemessageid:
        guild = clientBot.get_guild(int(guildid))
        result = service.spreadsheets().values().get(
        spreadsheetId=SpreadsheetId, range=reactRange).execute()
        values = result.get('values', [])
        if not values:
            return
        for row in values:
            if payload.emoji.name == row[0]:
                role = discord.utils.get(guild.roles, name=row[1])
                if not role == None:
                    await payload.member.add_roles(role)

#移除身分組
@clientBot.event
async def on_raw_reaction_remove(payload):
    if str(payload.message_id) == rolemessageid:
        guild = clientBot.get_guild(int(guildid))
        result = service.spreadsheets().values().get(
        spreadsheetId=SpreadsheetId, range=reactRange).execute()
        values = result.get('values', [])
        if not values:
            return
        for row in values:
            if payload.emoji.name == row[0]:
                role = discord.utils.get(guild.roles, name=row[1])
                member = discord.utils.get(guild.members, id=payload.user_id)
                if not role == None:
                    await member.remove_roles(role)

'''
"""
# 收到訊息時呼叫
@clientBot.event
async def on_message(message):
    
    # 送信者為Bot時無視
    if message.author.bot:
        return
    await clientBot.process_commands(message) # 用來確認是否符合command形式
    
    #私訊
    if message.guild == None:
        return

    result = service.spreadsheets().values().get(
    spreadsheetId=SpreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    if not values:
        return
    else:
        for row in values:
            if (message.channel.name == row[0] or row[0] == ''):
                keywords = row[1].split()
                check = True
                for keyword in keywords:
                    if not keyword in message.content:
                        check = False
                        break
                if check:
                    if message.author.nick == None:
                        username = message.author.name
                    else:
                            username = message.author.nick
                    if '<ban>' in row[2]:
                        await message.author.ban()
                    else:
                        if '<kick>' in row[2]:
                            await message.author.kick()
                        if '<delete>' in row[2]:
                            await message.delete()
                        else:
                            if '<reply>' in row[2]:
                                await message.reply(row[3].replace('<username>',username))
                            if '<replyrandom>' in row[2]:
                                msgs = row[3].split('|')
                                if len(msgs) != 0:
                                    index = random.randint(0, len(msgs)-1)
                                    await message.reply(msgs[index].replace('<username>',username))
                    if '<send>' in row[2]:
                        await message.channel.send(row[3].replace('<username>',username))
                    if '<sendrandom>' in row[2]:
                        msgs = row[3].split('|')
                        if len(msgs) != 0:
                            index = random.randint(0, len(msgs)-1)
                            await message.channel.send(msgs[index].replace('<username>',username))
                    return
"""
