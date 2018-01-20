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
		self.settings_path = "data/edt/settings.json"
		self.settings = dataIO.load_json(self.settings_path)

	#@commands.group(aliases=["uapv-edt"], no_pm=False, pass_context=True)
	@commands.command(name="edt", aliases=["uapv-edt"], no_pm=False, pass_context=True)
	async def edt(self, ctx, *text):
		"""Parses edt.
		Use .edt for today's edt
		or .edt 12 for the 12th planning"""
		# await self.bot.say("Fetching edt ...")
		if len(text) > 0:
			if text[0].isnumeric():
				await inputp(self=self, ctx=ctx, raw=text)
		else:
			await fetch(self=self, ctx=ctx, sDt="20"+time.strftime("%y%m%d"))
	
	@commands.command(name="edtuid", aliases=["uapv-edt.uapv", "edtuapv"], no_pm=True, pass_context=True)
	@checks.mod_or_permissions(administrator=True)
	async def edtuid(self, ctx, rid : str, *text):
		"""Get the edt for a given uid.
		Parsed from <accueil-ent2.univ-avignon.fr/edt/exportAgendaUrl?tdOptions=> so it have to be 4-digits group id
		"""
		if len(rid) > 0 and rid.isdigit():
			if len(text) > 0:
				if text[0].isnumeric():
					await inputp(self=self, ctx=ctx, raw=text, uid=int(rid))
			else:
				await fetch(self=self, ctx=ctx, sDt="20"+time.strftime("%y%m%d"), uid=int(rid))
		
	#https://accueil-ent2.univ-avignon.fr/edt/exportAgendaUrl?uidnumber=1701795
	
	#@edt.command(name ="set", pass_context=True)
	@commands.command(name="edtset", aliases=["uapv-edt.set"], no_pm=True, pass_context=True)
	@checks.mod_or_permissions(administrator=True)
	async def edtset(self, ctx, rid : str, channel : discord.Channel=None):
		"""Set edt sources.
		Parsed from <accueil-ent2.univ-avignon.fr/edt/exportAgendaUrl?tdOptions=> so it have to be 4-digits group id
		"""
		server = ctx.message.server
		if not rid.isdigit():
			await self.bot.say(":x: Invalid id. Please input a **4-digit** id.")
			return
		if channel is None:
			channel = ctx.message.channel
			#channel = ctx.message.server.default_channel
		if server.id not in self.settings:
			self.settings[server.id] = {}
		sserver = self.settings[server.id]
		#if channel.id not in self.settings[server.id]:
		self.settings[server.id][channel.id] = "https://accueil-ent2.univ-avignon.fr/edt/exportAgendaUrl?tdOptions={}".format(rid)
		fileIO(self.settings_path, "save", self.settings)
		#await self.bot.say(self.settings[server.id][channel.id])
		await self.bot.send_message(channel, ":white_check_mark: Group set to `{}`".format(rid))

async def inputp(self, ctx, raw : list=[], uid=0):
	m=0
	for i in raw:
		try:
			m=int(i)
			if int(i)<10: i="0"+i
			if int(i)<=31:
				if uid != 0:
					await fetch(self=self, ctx=ctx, sDt= "20"+time.strftime("%y%m")+i, uid=uid)
				else:
					await fetch(self=self, ctx=ctx, sDt= "20"+time.strftime("%y%m")+i)
			else:
				await self.bot.say(":x: This isn't a valid **day number**.")
		except:
			await self.bot.say(":grey_exclamation: Please insert a valid **day number**")
		
		# await self.bot.say("Sorry no result ¯\_(ツ)_/¯")
		
def parse(self, ctx, raw, Dt, uid=0):
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
		if self.settings["solstice"]:
			DtStart=str(int(SRaw[:2])+1)+"h"+SRaw[2:4]
		else:
			DtStart=SRaw[:2]+"h"+SRaw[2:4]
		
		ERaw = event[6].split(":")[1].split("T")[1]
		#[15:]
		if self.settings["solstice"]:
			DtEnd=str(int(ERaw[:2])+1)+"h"+ERaw[2:4]
		else:
			DtEnd=ERaw[:2]+"h"+ERaw[2:4]
		
		NRaw=event[7].split(":")[1].split("- ")
		#print(NRaw[-1:])
		#print(NRaw)
		if uid != 0:
			Name = NRaw[1].title()
		else:
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
				Name = ":construction_worker:"+Name
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

	
async def fetch(self, ctx, sDt, uid=0):
	""" Fetch EDT """
	event = []
	server = ctx.message.server
	channel = ctx.message.channel
	
	url = self.settings["url"]
	if (server.id in self.settings) and (channel.id in self.settings[server.id]):
		url = self.settings[server.id][channel.id]
	if uid != 0:
		url = self.settings["uid"]+str(uid)
	#await self.bot.send_message(channel, url)
	
	async with aiohttp.get(url) as r:
		raw = await r.text()
	await self.bot.say(":date: "+toDay(sDt));
	for line in raw.split("BEGIN"):
		#parse(line, sDt)
		if line.startswith(":VEVENT"):
			for	l in line.split("\n"):
				if l.startswith("DTSTART:"+sDt):
					if uid != 0:
						event = parse(self=self, ctx=ctx, raw=line, Dt=sDt, uid=uid)
					else:
						event = parse(self=self, ctx=ctx, raw=line, Dt=sDt)
					try:
						embed=discord.Embed(title=event[2], description=event[3], color=event[4])
						embed.set_footer(text=event[0]+"-"+event[1])
						await self.bot.say(embed=embed)
					except:
						await self.bot.send_message(ctx.message.channel,"```{}-{} {} {}```".format(event[0],event[1],event[2],event[3]))
	if event == []:
		await self.bot.say("Sorry **no result** ¯\_(ツ)_/¯");
def check_folder():
	if not os.path.exists("data/edt"):
		print("Creating data/edt folder...")
		os.makedirs("data/edt")

def check_files():
	settings = {"url":"https://accueil-ent2.univ-avignon.fr/edt/exportAgendaUrl?tdOptions=3143","uid":"https://accueil-ent2.univ-avignon.fr/edt/exportAgendaUrl?uidnumber="}
	if not fileIO("data/edt/settings.json", "check"):
		print("Creating default edt settings.json...")
		fileIO("data/edt/settings.json", "save", settings)
		
def setup(bot):
	check_folder()
	check_files()
	bot.add_cog(EDT(bot))
