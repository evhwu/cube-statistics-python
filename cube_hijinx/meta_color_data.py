from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import requests
from time import sleep
import json
import io
import os
import xlrd

import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import openpyxl

from pathlib import Path
savePath = str(Path().absolute()) + "\\archive\\"
storePath = str(Path().absolute()) + "\\pngs\\"
imagePath = str(Path().absolute()) + "\\mana\\"

def translate_mana_cost(double, manacost):
    split_cost = manacost.replace('{', '').split('}')
    #print(split_cost)
    return_string = ''
    for symbol in split_cost:
        if '/' in symbol:
            if 'W' in symbol:
                return_string += 'W'
            if 'U' in symbol:
                return_string += 'U'
            if 'B' in symbol:
                return_string += 'B'
            if 'R' in symbol:
                return_string += 'R'
            if 'G' in symbol:
                return_string += 'G'
        else:
            if 'W' in symbol:
                return_string += 'WW'
            if 'U' in symbol:
                return_string += 'UU'
            if 'B' in symbol:
                return_string += 'BB'
            if 'R' in symbol:
                return_string += 'RR'
            if 'G' in symbol:
                return_string += 'GG'
            #if 'F' in symbol or 'N' in symbol or 'Q' in symbol or 'Y' in symbol:
            #    return_string += 
    if double:
        return return_string.lower()
    else:
        return return_string

def determine_splash(deck_colors):
    heavy = 15
    light = 5
    splash = 1.75
    splash_string = ''
    
    if deck_colors['W'] >= heavy:
        splash_string += 'WW'
    elif deck_colors['W'] >= light:
        splash_string += 'W'
    elif deck_colors['W'] >= splash:
        splash_string += 'w'
    
    if deck_colors['U'] >= heavy:
        splash_string += 'UU'
    elif deck_colors['U'] >= light:
        splash_string += 'U'
    elif deck_colors['U'] >= splash:
        splash_string += 'u'

    if deck_colors['B'] >= heavy:
        splash_string += 'BB'
    elif deck_colors['B'] >= light:
        splash_string += 'B'
    elif deck_colors['B'] >= splash:
        splash_string += 'b'

    if deck_colors['R'] >= heavy:
        splash_string += 'RR'
    elif deck_colors['R'] >= light:
        splash_string += 'R'
    elif deck_colors['R'] >= splash:
        splash_string += 'r'

    if deck_colors['G'] >= heavy:
        splash_string += 'GG'
    elif deck_colors['G'] >= light:
        splash_string += 'G'
    elif deck_colors['G'] >= splash:
        splash_string += 'g'
    
    return splash_string

def color_profile():
    files = os.listdir(savePath)
    players = {}
    params = {'format' : 'json'}
    
    for f in files:
        wb = xlrd.open_workbook(savePath + f)
                
        play_sheet = wb.sheet_by_name('Play')
        for col in range(play_sheet.ncols):
            player_name = play_sheet.cell_value(0 , col)
            deck_symbols = ''
            if player_name not in players:
                players[player_name] = {'W':0,'U':0,'B':0,'R':0,'G':0, 'color_profs':[]}
            def determine_points():
                win_sheet = wb.sheet_by_name('Results')
                for row in range(win_sheet.nrows):
                    if win_sheet.cell_value(row, 4) == '':
                        break
                    if win_sheet.cell_value(row, 4) == player_name:
                        if row == 1:
                            return 'F'
                        if row == 2:
                            return 'N'
                        if row == 3:
                            return 'Q'
                        if row == 4:
                            return 'Y'
                return 'Y'
            
            for row in range(1, play_sheet.nrows):
                curr_card = play_sheet.cell_value(row,col)
                if curr_card is None or curr_card == '':
                    break
                
                response = requests.get('https://api.scryfall.com/cards/search?q=' + curr_card, params = params)
                card_dict = response.json()['data']
                for card_entry in card_dict:
                    if card_entry['name'] == curr_card:
                        manacost  = ''
                        if 'card_faces' in card_entry:
                            for face_no in range(len(card_entry['card_faces'])):
                                manacost += card_entry['card_faces'][face_no]['mana_cost']
                            manacost = translate_mana_cost(True, manacost)
                        else:
                            manacost = card_entry['mana_cost']
                            manacost = translate_mana_cost(False, manacost)
                        #print(manacost)
                        print(card_entry['name'])
                        deck_symbols += manacost
            
            deck_colors = {'W':0,'U':0,'B':0,'R':0,'G':0}
            for symbol in deck_symbols:
                if symbol == 'W':
                    deck_colors['W'] += .5
                elif symbol == 'w':
                    deck_colors['U'] += .25
                elif symbol == 'U':
                    deck_colors['U'] += .5
                elif symbol == 'u':
                    deck_colors['U'] += .25
                elif symbol == 'B':
                    deck_colors['B'] += .5
                elif symbol == 'b':
                    deck_colors['B'] += .25
                elif symbol == 'R':
                    deck_colors['R'] += .5
                elif symbol == 'r':
                    deck_colors['R'] += .25
                elif symbol == 'G':
                    deck_colors['G'] += .5
                elif symbol == 'g':
                    deck_colors['G'] += .25
            print(deck_colors['W'])
            print(deck_colors['U'])
            print(deck_colors['B'])
            print(deck_colors['R'])
            print(deck_colors['G'])
            players[player_name]['W'] += deck_colors['W']
            players[player_name]['U'] += deck_colors['U']
            players[player_name]['B'] += deck_colors['B']
            players[player_name]['R'] += deck_colors['R']
            players[player_name]['G'] += deck_colors['G']

            #
            players[player_name]['color_profs'].append(determine_splash(deck_colors) + determine_points())
    color_image(players)

def color_pie(key, value):
    super_total = value['W'] + value['U'] + value['B'] + value['R'] + value['G']
    total = [value['W'],value['U'],value['B'],value['R'],value['G']]
    labels = ["W600", "U600", "B600", "R600", "G600"] #percent?
    percent = [ '{:.2f}%'.format(value['W']/super_total),
                '{:.2f}%'.format(value['U']/super_total),
                '{:.2f}%'.format(value['B']/super_total),
                '{:.2f}%'.format(value['R']/super_total),
                '{:.2f}%'.format(value['G']/super_total)]
    
    plt.title(key)
    plt.gca().axis("equal")
    wedges, texts = plt.pie(total, startangle=90, labels=percent,
                        wedgeprops = { 'linewidth': 2, "edgecolor" :"k","fill":False,  })

    def img_to_pie( fn, wedge, xy, zoom=1, ax = None):
        if ax==None: ax=plt.gca()
        im = plt.imread(fn, format='png')
        path = wedge.get_path()
        patch = PathPatch(path, facecolor='none')
        ax.add_patch(patch)
        imagebox = OffsetImage(im, zoom=zoom, clip_path=patch, zorder=-10)
        ab = AnnotationBbox(imagebox, xy, xycoords='data', pad=0, frameon=False)
        ax.add_artist(ab)

    positions = [(0,0),(0,0),(0,0),(0,0),(0,0)]
    zooms = [0.4,0.4,0.4,0.4,0.4]

    for i in range(5):
        fn = "{}{}.png".format(imagePath,labels[i].lower())
        img_to_pie(fn, wedges[i], xy=positions[i], zoom=zooms[i] )
        wedges[i].set_zorder(10)

    plt.show()

def filter_profile(prof):
    new_prof = ''
    last_symbol = ''
    for symbol in prof:
        if symbol.isupper() and symbol is not last_symbol:
            new_prof += symbol
        last_symbol = symbol
    return new_prof[:-1]

def winning_colors(wc_dict):
    listify = []
    class ColorPlace():
        def __init__(self,name, times, placing):
            self.name = name
            self.times = times
            self.placing = placing
        def __lt__(self, other):
            return self.times > other.times
    
        
    for key, value in wc_dict.items():
        listify.append(ColorPlace(key, value[0], value[1]))

    listify.sort()

    for cp in listify:
        print( '{} - {} , {}'.format(cp.name, cp.times, cp.placing/cp.times))

    image_name = storePath + 'winning_colors' +'.png'
    myFont = ImageFont.truetype('888_MRG.ttf', 52)

    canvas_x = 1080 #3
    canvas_y = len(listify) * 310 + 200

    new_image = Image.new('RGB', (canvas_x,canvas_y))
    draw = ImageDraw.Draw(new_image)   

    placeholder_x = 20
    curr_x = 0
    curr_y = 0
    symbol_png = { 'W' : 'W240.png',
                   'U' : 'U240.png',
                   'B' : 'B240.png',
                   'R' : 'R240.png',
                   'G' : 'G240.png',
                   'w' : 'W120.png',
                   'u' : 'U120.png',
                   'b' : 'B120.png',
                   'r' : 'R120.png',
                   'g' : 'G120.png' }

    for entry in listify:
        curr_x = placeholder_x
        
        for symbol in entry.name:
            temp_image = Image.open(imagePath + symbol_png[symbol])
            new_image.paste(temp_image, (curr_x, curr_y))
            curr_x += 140
        draw.text((placeholder_x, curr_y+140), 'Times Drafted: {}'.format(entry.times), (255,255,255), font=myFont)
        draw.text((placeholder_x, curr_y+200), 'Average Placing: {:.3f}'.format(entry.placing/entry.times), (255,255,255), font=myFont)
        curr_y += 310

    new_image = new_image.resize((round(new_image.size[0]), round(new_image.size[1])))
    new_image.save(image_name)

def color_image(players):

    image_name = storePath +'color_prof'+'.png'
    files = os.listdir(savePath)
    myFont = ImageFont.truetype('888_MRG.ttf', 64)

    wc_dict = {}

    canvas_x = 3920
    canvas_y = 140 * len(files) + 500
    new_image = Image.new('RGB', (canvas_x,canvas_y))
    draw = ImageDraw.Draw(new_image)

    placeholder_x = 0
    curr_x = 0
    curr_y = 0
    fnqy = {'F' : 1,
            'N' : 2,
            'Q' : 3,
            'Y' : 4}

    symbol_png = { 'W' : 'W240.png',
                   'U' : 'U240.png',
                   'B' : 'B240.png',
                   'R' : 'R240.png',
                   'G' : 'G240.png',
                   'w' : 'W120.png',
                   'u' : 'U120.png',
                   'b' : 'B120.png',
                   'r' : 'R120.png',
                   'g' : 'G120.png' }
    
    for key, value in players.items():
        
        color_pie(key, value)
        
        curr_x = placeholder_x
        draw.text((curr_x, curr_y), key, (255,255,255), font=myFont)
        curr_y += 140
        
        for prof in value['color_profs']:
            for symbol in prof:
                
                if symbol == 'F' or symbol == 'N' or symbol == 'Q' or symbol == 'Y':
                    new_prof = filter_profile(prof)
                    try:
                        wc_dict[new_prof][0] += 1
                        wc_dict[new_prof][1] += int(fnqy[symbol])
                    except:
                        wc_dict[new_prof] = [1,fnqy[symbol]]
                else:
                    temp_image = Image.open(imagePath + symbol_png[symbol])
                    new_image.paste(temp_image, (curr_x, curr_y))
                    curr_x += 140
            curr_y += 140
            curr_x = placeholder_x
        curr_y = 0
        placeholder_x += 980
        
        
    new_image = new_image.resize((round(new_image.size[0]), round(new_image.size[1])))
    new_image.save(image_name)

    winning_colors(wc_dict)
    


    
