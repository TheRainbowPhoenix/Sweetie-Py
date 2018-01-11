from discord.ext import commands
import datetime
from .utils.chat_formatting import box
from .utils.dataIO import dataIO
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import user_allowed, send_cmd_help
from copy import deepcopy
import os
import time
import discord
import aiohttp
import functools
import asyncio
import re
import json


class EDT:
	"""Sweetie's EDT Parser"""

	def __init__(self, bot):
		self.bot = bot
		self.settings = fileIO("data/edt/settings.json", "load")

	@commands.group(name="edt", no_pm=False, pass_context=True)
	#@commands.command(name="edt", no_pm=False, pass_context=True)
	async def _edt(self, ctx, *text):
		"""Parses edt.
		Use .edt for today's edt
		or .edt 12 for the 12th planning"""
		# await self.bot.say("Fetching edt ...")
		if len(text) > 0:
			await inputp(self=self, ctx=ctx, raw=text)
		else:
			await fetch(self=self, ctx=ctx, sDt="20"+time.strftime("%y%m%d"))

async def inputp(self, ctx, raw : list=[]):
	m=0
	for i in raw:
		try:
			m=int(i)
			if int(i)<10: i="0"+i
			if int(i)<=31:
				await fetch(self=self, ctx=ctx, sDt= "20"+time.strftime("%y%m")+i)
			else:
				await self.bot.say("This isn't a valid day number.")
		except:
			await self.bot.say("Please insert a valid day number")
		
		# await self.bot.say("Sorry no result ¯\_(ツ)_/¯")
		
def parse(self, ctx, raw, Dt):
	server = ctx.message.server
	
	DtStart = "0"
	DtEnd = "1"
	Name = ""
	Loca = ""
	Desc = "Useless"
	#Color = 0x282b30
	Color = 0x202225
	try:
		event = raw.split("\n")
		#print(raw)
		SRaw = event[5].split(":")[1].split("T")[1]
		#[17:]
		DtStart=SRaw[:2]+"h"+SRaw[2:4]
		
		ERaw = event[6].split(":")[1].split("T")[1]
		#[15:]
		DtEnd=ERaw[:2]+"h"+ERaw[2:4]
		
		NRaw=event[7].split(":")[1].split("- ")
		#print(NRaw[-1:])	
		Name = NRaw[0].title()
		for i in NRaw:
			if i.startswith("Evaluation"):
				Color = 0xf04747
				Name = ":writing_hand: "+Name
				# print("[E] ",end="")
			if i.startswith("TP"):
				Color = 0x3498db
				Name = ":desktop: "+Name
			if i.startswith("TD"):
				Color = 0x71368a
				Name = ":scroll: "+Name
			if i.startswith("CM"):
				Color = 0x202225
				Name = ":blue_book: "+Name
			if i.startswith("UEO"):
				Color = 0x1f8b4c
				Name = ":microscope: "+Name
			if i.startswith("Rattrapage"):
				Color = 0xa84300
			# print(i.title())
		
		DRaw=event[8].split(":")[1].splitlines()[0].split("\,")
		for i in DRaw:
			Loca += i.split("=")[0]
		
		if Loca == "": Loca = "Somewhere"
		if Name == "": Name = "MissingName"
		#print(raw)
		
		# print(DtStart, "-",DtEnd, "\t", Name, "\t", Loca, "\t", Color)
		return DtStart,DtEnd,Name,Loca,Color
		
		# embed=discord.Embed(title=Name, description=Loca, color=Color)
		# embed.set_footer(text=DtStart+"-"+DtEnd)
		#await self.bot.send_message(ctx.message.channel,"```{}-{} {} {}```".format(DtStart,DtEnd,Name,Loca))
		# await self.bot.say(embed=embed)
		
	except:
		# print(raw)
		# print("Invalid Line !")
		return [0,0,":warning: Warning","Invalid Lesson",0xffcc4d]
	
def toDay(Dt):
	FrDays = ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi","Dimanche"]
	FrMonth = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
	y=int(Dt[:4])
	m=int(Dt[4:6].lstrip("0"))	
	d=int(Dt[6:8].lstrip("0"))
	w=datetime.datetime(y,m,d).weekday()
	return FrDays[w]+" "+str(d)+" "+FrMonth[m-1]+" "+str(y)

	
async def fetch(self, ctx, sDt):
	""" Fetch EDT """
	event = []
	url = "https://accueil-ent2.univ-avignon.fr/edt/exportAgendaUrl?tdOptions=3143"

	async with aiohttp.get(url) as r:
		raw = await r.text()
	await self.bot.say(":date: "+toDay(sDt));
	for line in raw.split("BEGIN"):
		#parse(line, sDt)
		if line.startswith(":VEVENT"):
			for	l in line.split("\n"):
				if l.startswith("DTSTART:"+sDt):
					event = parse(self=self, ctx=ctx, raw=line, Dt=sDt)
					try:
						embed=discord.Embed(title=event[2], description=event[3], color=event[4])
						embed.set_footer(text=event[0]+"-"+event[1])
						await self.bot.say(embed=embed)
					except:
						await self.bot.send_message(ctx.message.channel,"```{}-{} {} {}```".format(event[0],event[1],event[2],event[3]))
	if event == []:
		await self.bot.say("Sorry no result ¯\_(ツ)_/¯");
def check_folder():
	if not os.path.exists("data/edt"):
		print("Creating data/edt folder...")
		os.makedirs("data/edt")

def check_files():
	settings = {"url":"https://accueil-ent2.univ-avignon.fr/edt/exportAgendaUrl?tdOptions=3143"}
	if not fileIO("data/edt/settings.json", "check"):
		print("Creating default edt settings.json...")
		fileIO("data/edt/settings.json", "save", settings)
		
def setup(bot):
	check_folder()
	check_files()
	bot.add_cog(EDT(bot))
