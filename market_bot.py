from discord.ext import commands
import discord
import settings

logger = settings.logging.getLogger("market_bot_log")
    
def run():
    intents = discord.Intents.all()
    intents.message_content = True
    prefix = '/'
    bot = commands.Bot(command_prefix=prefix, intents=intents)
    @bot.event
    async def on_ready():
        channel = bot.get_channel(settings.SECRET_MARKET_CHANNEL_ID)
        print(settings.SLASH_CMDS_DIR)
        for slashcmd_file in settings.SLASH_CMDS_DIR.glob("*.py"):
            if slashcmd_file.name != "__init__.py":
                await bot.load_extension(f"slashcmds.{slashcmd_file.name[:-3]}")
        bot.tree.copy_global_to(guild=settings.SECRET_GUILD_ID)
        await bot.tree.sync(guild=settings.SECRET_GUILD_ID)
        print("_"*50)    
        logger.info(f"\nMarket Bot is ready\nUser: {bot.user} (ID: {bot.user.id})")
        logger.info(f"\nGuild ID: {bot.guilds[0].id}")
        print("_"*50)    

    class NotOwner(commands.CheckFailure):
        ...
    
    def is_owner():
        async def predicate(ctx):
            if ctx.author.id != ctx.guild.owner_id:
                raise NotOwner("You are not the owner of this server.")
            return True
        return commands.check(predicate)

    @bot.tree.command(
        name="reload", 
        description="Reloads a specified slash_cmds subfile <plural groupname>"
    )
    @is_owner()
    async def reload(interaction: discord.Interaction, slash_cmd : str):
        slash_cmd_name = f"slash_cmds.{slash_cmd.lower}"
        try:
            await bot.reload_extension(slash_cmd_name)
            logger.info(f"Cog {slash_cmd_name} reloaded successfully.")
            await interaction.response.send_message(f"Cog {slash_cmd_name} reloaded successfully.")
        except commands.ExtensionNotLoaded:
            await bot.load_extension(slash_cmd_name)
            logger.info(f"Cog {slash_cmd_name} loaded successfully.")
            await interaction.response.send_message(f"Cog {slash_cmd_name} loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to reload cog {slash_cmd_name}: {e}")
            await interaction.response.send_message(f"Failed to reload cog {slash_cmd_name}: {e}")        
    
    @bot.tree.command(
        name="load",
        description="Loads a specified slash_cmds subfile <plural groupname>"
    )
    @is_owner()
    async def load(interaction: discord.Interaction, slash_cmd : str):
        slash_cmd_name = f"slash_cmds.{slash_cmd.lower}"
        try:
            await bot.load_extension(slash_cmd_name)
            logger.info(f"Cog {slash_cmd_name} loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load cog {slash_cmd_name}: {e}")       
    
    @bot.tree.command(
        name= "unload",
        description="Unloads a specified slash_cmds subfile <plural groupname>"
    )
    @is_owner()
    async def unload(interaction: discord.Interaction, slash_cmd : str):
        slash_cmd_name = f"slash_cmds.{slash_cmd.lower}"
        try:
            await bot.unload_extension(slash_cmd_name)
            logger.info(f"Cog {slash_cmd_name} unloaded successfully.")
        except Exception as e:
            logger.error(f"Failed to unload cog {slash_cmd_name}: {e}")       

    bot.run(settings.SECRET_BOT_TOKEN, root_logger=True)

if __name__ == "__main__":
    run()