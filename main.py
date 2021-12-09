import asyncio
from re import A, M, T
import discord
from discord import client
from discord import embeds
from discord import user
from discord import colour
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
async def rps(mackngo):
    await open_account(mackngo.author)
    users = await databank()
    user = mackngo.author
    await mackngo.send("ต้องการลงเดิมพันเท่าไหร่")
    bet = await client.wait_for("message")
    lostmoney = int(bet.content) *2
    if int(bet.content) > users[str(user.id)]["wallet"]:
        await mackngo.send("ยอดเงินคุณไม่เพียงพอที่จะลงเดิมพัน")
    else:
        while True:
            message = await mackngo.send("เป่า ยิ้ง ฉุบบ")
            await message.add_reaction("🔨")
            await message.add_reaction("✂️")
            await message.add_reaction("📄")
            number = random.randint(0,3)
            ans = ["Rock", "Paper", "Scissors", "My Love"]
            check = lambda r, u: u == mackngo.author and str(r.emoji) in "🔨✂️📄"
            try:
                reaction, user = await client.wait_for("reaction_add", check= check, timeout=60)
            except asyncio.TimeoutError:
                await mackngo.send("ช้าไปป่าวน้องง")
            if str(reaction.emoji) == "🔨":
                await mackngo.send("ฉันจะออกอะไรดีน้าาาา")
                if ans[number] == "Rock":
                    await mackngo.send("ฉันจะออก", file=discord.File("Rock.png"))
                    await mackngo.send("เสมอจ้าเอาใหม่อีกครั้งนะ")
                elif ans[number] == "Paper":
                    await mackngo.send("ฉันจะออก", file=discord.File("paper.png"))
                    await mackngo.send("ยินดีด้วยคุณได้รับเงิน %d Coins" %lostmoney)
                    users[str(user.id)]["wallet"] += lostmoney
                    break
                elif ans[number] == "My Love":
                    await mackngo.send("เสียใจด้วยนะแต่ความรักของฉันจะชนะทุกอย่าง", file=discord.File("Mylove.png"))
                    users[str(user.id)]["wallet"] -= lostmoney / 2
                    break
                else:
                    await mackngo.send("ฉันจะออก", file=discord.File("scissors.png"))
                    await mackngo.send("ยินดีด้วยคุณเสียเงิน %d Coins" %lostmoney)
                    users[str(user.id)]["wallet"] -= lostmoney / 2
                    break
            elif str(reaction.emoji) == "✂️":
                await mackngo.send("ฉันจะออกอะไรดีน้าาาา")
                if ans[number] == "Rock":
                    await mackngo.send("ฉันจะออก", file=discord.File("Rock.png"))
                    await mackngo.send("ยินดีด้วยคุณได้เสียเงิน %d Coins" %lostmoney)
                    users[str(user.id)]["wallet"] -= lostmoney
                    break
                elif ans[number] == "Paper":
                    await mackngo.send("ฉันจะออก", file=discord.File("paper.png"))
                    await mackngo.send("ยินดีด้วยคุณได้รับเงิน %d Coins" %lostmoney)
                    users[str(user.id)]["wallet"] += lostmoney / 2
                    break
                elif ans[number] == "My Love":
                    await mackngo.send("เสียใจด้วยนะแต่ความรักของเราจะชนะทุกอย่าง", file=discord.File("Mylove.png"))
                    users[str(user.id)]["wallet"] -= lostmoney / 2
                    break
                else:
                    await mackngo.send("ฉันจะออก", file=discord.File("scissors.png"))
                    await mackngo.send("เสมอจ้าเอาใหม่อีกครั้งนะ")
            else:
                await mackngo.send("ฉันจะออกอะไรดีน้าาาา")
                if ans[number] == "Rock":
                    await mackngo.send("ฉันจะออก", file=discord.File("Rock.png"))
                    await mackngo.send("ยินดีด้วยคุณได้เสียเงิน %d Coins" %lostmoney)
                    users[str(user.id)]["wallet"] -= lostmoney / 2
                    break
                elif ans[number] == "Paper":
                    await mackngo.send("ฉันจะออก", file=discord.File("paper.png"))
                    await mackngo.send("เสมอจ้าเอาใหม่อีกครั้งนะ")
                elif ans[number] == "My Love":
                    await mackngo.send("เสียใจด้วยนะแต่ความรักของเราจะชนะทุกอย่าง", file=discord.File("Mylove.png"))
                    users[str(user.id)]["wallet"] -= lostmoney / 2
                    break
                else:
                    await mackngo.send("ฉันจะออก", file=discord.File("scissors.png"))
                    await mackngo.send("ยินดีด้วยคุณได้รับเงิน %d Coins" %lostmoney)
                    users[str(user.id)]["wallet"] += lostmoney
                    break
    with open("bank.json", "w") as f:
        json.dump(users, f)
    gak = discord.Embed(title = f"ตอนนี้คุณ {mackngo.author.name}'s", color = discord.Color.dark_gold())
    gak.add_field(name= "มีเงินทั้งหมด", value= users[str(user.id)]["wallet"])
    await mackngo.send(embed = gak)

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
async def test(ctx):
    embed = discord.Embed(color=0x00ff00) #creates embed
    embed.set_image(url="https://lh3.googleusercontent.com/HBrh0QUd2MjeFDiEi_epX4Pq5ChH3kgpqxIbr-BxaiX5PYSHnZmqvrAY2ArBaoJ3IM2aeg=s85")
    await ctx.send(embed=embed)

@client.command()
async def quiz(ctx):
    with open("allquestion.json", "r") as f:
        ask = json.load(f)
    question = random.choice(list(ask.keys()))
    ans = ask[question][2]
    await ctx.send('%s\n1) %s\n2) %s' %(question, ask[question][0], ask[question][1]))
    ansuser = await client.wait_for("message")
    if ansuser.content == '1':
        answer = ask[question][0]
    if ansuser.content == '2':
        answer = ask[question][1]
    if ans == answer:
        await ctx.send("ถูกต้องนะคร้าบบบบบ")
    else:
        await ctx.send("ทำไมโง่อ่า ตอบ %s ตะหาก" %(ans))
    
    

@client.command()
async def addquiz(ctx):
    await ctx.send("ระบุคำถาม")
    quiz = await client.wait_for("message")
    await ctx.send("ระบุตัวเลือกที่ 1")
    ch1 = await client.wait_for("message")
    await ctx.send("ระบุตัวเลือกที่ 2")
    ch2 = await client.wait_for("message")
    await ctx.send("ระบุคำตอบ")
    ans = await client.wait_for("message")
    with open("allquestion.json", "r") as f:
        allquiz = json.load(f)
    allquiz.update({quiz.content: [ch1.content, ch2.content, ans.content]})
    json.dump(allquiz, open("allquestion.json", "w"))


    
@client.command()
async def rank(ctx):
    users = await databank()
    mylist = []
    with open("bank.json", "r") as f:
        user = json.load(f)
    
    for i in user:
        bal = [users[str(i)]["wallet"], users[str(i)]["bank"]]
        bals = bal[0] + bal[1]
        mylist.append([bals, str(i)])
        bal.clear()
    mylist.sort(reverse=True)
    gak = discord.Embed(title = "Rank", color = discord.Color.magenta())
    usersort = await client.fetch_user(mylist[0][1])
    usersort2 = await client.fetch_user(mylist[1][1])
    usersort3 = await client.fetch_user(mylist[2][1])
    gak.add_field(name="อันดับ", value = "1\n2\n3")
    gak.add_field(name="user", value = "%s\n%s\n%s" %(str(usersort)[:-5],str(usersort2)[:-5],str(usersort3)[:-5]))
    gak.add_field(name="Coins", value= "%s\n%s\n%s" %(mylist[0][0],mylist[1][0],mylist[2][0]))
    await ctx.send(embed = gak)
async def update_bank(user, change=0, mode="wallet"):
    users = await databank()

    users[str(user.id)][mode] += change

    with open("bank.json", "w") as f:
        json.dump(users, f)

    bal = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"]]
    return bal

client.run('OTE2NzA4NDk4ODg3MzAzMjA5.YauFUQ.5B9kZLdnrYqrlwROJR9_Ev6hz_g')
