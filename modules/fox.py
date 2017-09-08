import io
import os.path
import aiohttp
import discord
from discord.ext import commands

class Fox:
	"""Shows cutes foxes"""

	def __init__(self, bot):
		self.bot = bot
		
	@commands.command(pass_context=True, no_pm=True, name="fox")
	async def _fox(self, ctx: commands.Context):
		"""Shows a random fox."""

		await self.bot.type()
		url = "http://wohlsoft.ru/images/foxybot/randomfox.php"
		async with aiohttp.get(url) as response:
			img_url = (await response.json())["file"]
			await self.bot.say(":fox: {}".format(img_url))
			# filename = os.path.basename(img_url)
			# async with aiohttp.get(img_url) as image:
				# await self.bot.upload(
					# io.BytesIO(await image.read()), filename=filename)

	@commands.command(pass_context=True, no_pm=True, name="cat")
	async def _cat(self, ctx: commands.Context):
		"""Shows a random cat."""

		await self.bot.type()
		url = "http://random.cat/meow"
		async with aiohttp.get(url) as response:
			img_url = (await response.json())["file"]
			await self.bot.say(":cat: {}".format(img_url))
			# filename = os.path.basename(img_url)
			# async with aiohttp.get(img_url) as image:
				# await self.bot.upload(
					# io.BytesIO(await image.read()), filename=filename)

	@commands.command(pass_context=True, no_pm=True, name="dog")
	async def _dog(self, ctx: commands.Context):
		"""Shows a random dog."""

		await self.bot.type()
		url = "http://random.dog/"
		async with aiohttp.get(url + "woof") as response:
			filename = await response.text()
			await self.bot.say(":dog: {}".format(url + filename))
			# async with aiohttp.get(url + filename) as image:
				# await self.bot.upload(
					# io.BytesIO(await image.read()), filename=filename)

	@commands.command(pass_context=True, no_pm=True, name="bird")
	async def _bird(self, ctx: commands.Context):
		"""Shows a random bird."""

		await self.bot.type()
		url = "http://shibe.online/api/birds?count=1"
		async with aiohttp.get(url) as response:
			img_url = (await response.json())[0]
			await self.bot.say(":bird: {}".format(img_url))
			# filename = os.path.basename(img_url)
			# async with aiohttp.get(img_url) as image:
				# await self.bot.upload(
					# io.BytesIO(await image.read()), filename=filename)
					
def setup(bot):
	bot.add_cog(Fox(bot))
