from re import M
import discord
from discord import client
from discord import embeds
from discord import user
from discord.colour import Color
from discord.ext import commands
import json
import os
import random

os.chdir("C:\\Users\\maxsk\\OneDrive\\เดสก์ท็อป\\Project")

client = commands.Bot(command_prefix='e!')

@client.event
async def on_ready() :
    print("Bot Started!")

@client.command()
async def balance(mackngo): #เช็กยอดคงเหลือ
    await open_account(mackngo.author)
    user = mackngo.author
    users = await databank()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"] 

    em = discord.Embed(title = f"{mackngo.author.name}'s balance", color = discord.Color.dark_gold())
    em.add_field(name="Wallet balance", value=wallet_amt)
    em.add_field(name="Bank balance", value=bank_amt)
    await mackngo.send(embed = em)

@client.command()
async def send(ctx, member:discord.Member, amount = None): #โอนเงิน
    await open_account(ctx.author)
    await open_account(member)

    if amount == None:
        await ctx.send("Please enter the amount.")
        return
    
    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("You don't have enough money;)")
        return
    if amount < 0:
        await ctx.send("Amount must more than zero.")
        return

    await update_bank(ctx.author, -amount, "bank")
    await update_bank(member, amount, "bank")

    await ctx.send(f"You gave {member} {amount} coins!")

@client.command()
async def withdraw(mackngo, amount = None): #ถอนเงิน
    await open_account(mackngo.author)

    if amount == None:
        await mackngo.send("Please enter the amount.")
        return
    
    bal = await update_bank(mackngo.author)

    amount = int(amount)
    if amount > bal[1]:
        await mackngo.send("You don't have enough money;)")
        return
    if amount < 0:
        await mackngo.send("Amount must more than zero.")
        return

    await update_bank(mackngo.author, amount)
    await update_bank(mackngo.author, -amount, "bank")

    await mackngo.send(f"You withdrew {amount} coins!")

@client.command()
async def deposit(mackngo, amount = None): #ฝากเงิน
    await open_account(mackngo.author)

    if amount == None:
        await mackngo.send("Please enter the amount.")
        return
    
    bal = await update_bank(mackngo.author)

    amount = int(amount)
    if amount > bal[0]:
        await mackngo.send("You don't have enough money;)")
        return
    if amount < 0:
        await mackngo.send("Amount must more than zero.")
        return

    await update_bank(mackngo.author, -amount)
    await update_bank(mackngo.author, amount, "bank")

    await mackngo.send(f"You deposited {amount} coins!")

@client.command()
async def bet(mackngo): #เสี่ยงดวง
    await open_account(mackngo.author)

    users = await databank()
    user = mackngo.author
    earnings = random.randrange(1,11)
    losemoney = random.randrange(1, 1001)
    if  earnings <= 6:
        losemoney = -losemoney
        await mackngo.send(f"Oops! You lose {abs(losemoney)} coins!")
    elif earnings > 6 and earnings < 10:
        await mackngo.send(f"You recieve {losemoney} coins!")
    else:
        losemoney = 0
        await mackngo.send(f"Go Find a job!!")

    users[str(user.id)]["wallet"] += losemoney
    
    with open("bank.json", "w") as f:
        json.dump(users, f)


@client.command()
async def guess(mackngo): #เสี่ยงดวง
    await open_account(mackngo.author)
    users = await databank()
    user = mackngo.author
    await mackngo.send("ต้องการลงเดิมพันเท่าไหร่")
    bet = await client.wait_for("message")
    if int(bet.content) > users[str(user.id)]["wallet"]:
        await mackngo.send("ยอดเงินคุณไม่เพียงพอที่จะลงเดิมพัน")
    else:
        tbet = int(bet.content)
        users[str(user.id)]["wallet"] -= tbet
        number = random.randint(0, 100)
        em = discord.Embed(title = f"สวัสดีดีคุณ {mackngo.author.name} ยินดีที่คุณมาเล่นเกมส์กับเรา",\
            description = "ในห้องเกมทายใจของเราๆจะสุ่มตัวเลขขึ้นมา 1 ตัวและให้คุณทาย ถ้าคุณทายถูกรับ ไปเลย เงิน 2 เท่า จากเงินเดิมพัน เอาล่ะถ้าพร้อมแล้วพิมพ์เลขลงมาเลย!!", color = discord.Color.dark_gold())
        await mackngo.send(embed = em)
        for i in range(5):
            respone = await client.wait_for("message")
            num = int(respone.content)
            if num > number:
                await mackngo.send('มากไป')
                if 5 - (i+1) == 0:
                    await mackngo.send("เสียใจด้วยและคำตอบที่ถูกต้องก็คืออออ %d!!!" %number)
            elif num < number:
                await mackngo.send('น้อยไป')
                if 5 - (i+1) == 0:
                    await mackngo.send("เสียใจด้วยและคำตอบที่ถูกต้องก็คืออออ %d!!!" %number)
            else:
                await mackngo.send('ยินดีด้วย!!คุณได้รับเงินเป็นจำนวน %d Coin!!' %(tbet*2))
                users[str(user.id)]["wallet"] += tbet * 2
                break
        with open("bank.json", "w") as f:
            json.dump(users, f)
    gak = discord.Embed(title = f"ตอนนี้คุณ {mackngo.author.name}'s", color = discord.Color.dark_gold())
    gak.add_field(name= "มีเงินทั้งหมด", value= users[str(user.id)]["wallet"])
    await mackngo.send(embed = gak)

async def open_account(user): #เปิดบัญชี

    users = await databank()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open("bank.json", "w") as f:
        json.dump(users, f)
    return True

async def databank():
    with open("bank.json", "r") as f:
        users = json.load(f)

    return users
@client.command()
async def rank(ctx):
    users = await databank()
    mylist = []
    with open("bank.json", "r") as f:
        user = json.load(f)
    j = 0
    for i in user:
        bal = [users[str(i)]["wallet"], users[str(i)]["bank"]]
        bals = bal[0] + bal[1]
        mylist.append([bals, str(i)])
        bal.clear()
    mylist.sort(reverse=True)
    for i in mylist:
        usersort = await client.fetch_user(i[1])
        j += 1
        await ctx.send(("อันดับที่ %d  " %j) + str(usersort) + "           " + str(i[0]) + " Coins")

async def update_bank(user, change=0, mode="wallet"):
    users = await databank()

    users[str(user.id)][mode] += change

    with open("bank.json", "w") as f:
        json.dump(users, f)

    bal = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"]]
    return bal

client.run('OTA5NDE2OTc1MzI1ODc2Mjk3.YZD-jw.MBGOqNzbwbq2Vi398CEF_d1dQdc')
