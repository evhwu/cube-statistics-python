import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from pathlib import Path
import cube_helper
import xlsxtopng
savePath = str(Path().absolute()) + "\\archive\\"
intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='pack', help = 'Generates the pick order of a single pack. Format is !pack {draft ID} {steam ID} {pack #}.')
async def s_pack(ctx, draftID :str, steamID: str, pack_no: int):
    file_path = savePath + draftID + '.xlsx'
    if os.path.isfile(file_path):
        await ctx.send('File exists...')        
        if cube_helper.check_player(file_path, steamID, 'Draft'):
            await ctx.send('Player exists...')
            if pack_no < 1 or pack_no > 3:
                await ctx.send('Incorrect pack number')
            else:
                draft_col = cube_helper.find_player_col(file_path, steamID, 'Draft')
                if draft_col == -1:
                    await ctx.send('Column with steam ID not found')
                    return
                draft_col += 6
                output_name = f'{draftID}-{steamID}-{str(pack_no)}'
                cube_helper.clear_pngs()
                cube_helper.make_pack(file_path, pack_no, draft_col , output_name)
                files = os.listdir(str(Path().absolute()) + '\\pngs\\')
                for f in files:
                    if output_name in f:
                        file_b = str(Path().absolute()) + '\\pngs\\' + f
                        with open(file_b, 'rb') as fi:
                            await ctx.send(file=discord.File(fi, file_b))   
        else:
            await ctx.send('Draft ' + draftID + ' has no player named ' + steamID)
    else:
        await ctx.send('No draft with that ID!')    

@bot.command(name='records', help = 'Responds with the number of drafts recorded and the most recent one. /a for all IDs')
async def records(ctx, *args):
    flag_all = False
    for a in args:
        if a =='/a':
            flag_all = True
    records = os.listdir( str(Path().absolute()) + '\\archive\\')
    ctime = []
    response = str(len(records)) + ' drafts have been recorded.'
    for record in records:
        if flag_all:
            response += f"\n{record.replace('.xlsx', '')}"
        else:
            fname = Path(str(Path().absolute()) + '\\archive\\'+ record)
            ctime.append(fname.stat().st_ctime)
    if not flag_all:
        big_idx = 0
        for idx in range(len(ctime)):
            if ctime[idx] > ctime[big_idx]:
                big_idx = idx
        response += f" The most recent ID is: {records[big_idx].replace('.xlsx', '')}"
    
    await ctx.send(response)

@bot.command(name ='draft_file', help = 'Returns the .xlsx draft file given a specific Draft ID.')
async def draft_xlsx(ctx, draftID : str):
    file_path = savePath + draftID + '.xlsx'
    if os.path.isfile(file_path):
        with open(file_path,'rb') as fi:
            await ctx.send(file=discord.File(fi, file_path))
    else:
        await ctx.send('No draft with that ID!')
        

@bot.command(name ='decklist', help = 'Generates the decklists for a specific draft. Format is !decklist {draft ID} {steam ID}. \nNo steam ID defaults to all decklists.')
async def decklists(ctx, draftID : str, steamID : str=None):
    try:
        to_send_file = savePath + draftID + '.xlsx'
        
        if os.path.isfile(to_send_file):
            await ctx.send('File exists...')
        else:
            await ctx.send('No Draft with that ID found.')
            return
        
        if steamID != None:
            if cube_helper.check_player(to_send_file, steamID, 'Play'):
                await ctx.send('Player exists...')
            else:
                await ctx.send('No Player with that ID found.')
                return
        await ctx.send('Generating...')

        cube_helper.clear_pngs()
        xlsxtopng.main(to_send_file, steamID)
    except Exception as e:
        await ctx.send('FAILURE')
        print(e)
        return
    files = os.listdir(str(Path().absolute()) + '\\pngs\\')
    for f in files:
        if not steamID or steamID in f:
            file_b = str(Path().absolute()) + '\\pngs\\' + f
            with open(file_b, 'rb') as fi:
                await ctx.send(file=discord.File(fi, file_b))

##@bot.command(name='color_profile', help = 'Generates color profile for each player over all drafts. Format is !color_profile.')
##async def color_prof(ctx):


    
bot.run(TOKEN)
