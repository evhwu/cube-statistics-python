from pathlib import Path
import csv
import os
import xlrd
import requests
import json
import io

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import matplotlib.pyplot as plt

archivePath = str(Path().absolute()) + '\\archive\\'

def winrates():
    class Point:
        def __init__(self, winner, loser):
            self.winner = winner
            self.loser = loser
    class Matchup:
        def __init__(self, me, enemy, wins, losses):
            self.me = me
            self.enemy = enemy
            self.wins = wins
            self.losses = losses
            
    class Player:
        def __init__(self, name, points):
            self.name = name
            self.matchups = []
            for p in points:
                won = True
                other_player = ''
                if p.winner == name:
                    other_player = p.loser
                else:
                    won = False
                    other_player = p.winner
                found = False
                for m in self.matchups:
                    if m.enemy == other_player:
                        found = True
                        if won:
                            m.wins += 1
                        else:
                            m.losses += 1
                        break
                if not found:
                    if won:
                        self.matchups.append(Matchup(name,other_player,1,0))
                    else:
                        self.matchups.append(Matchup(name,other_player,0,1))
        def __str__(self):
            to_return = ''
            avg_wr = 0
            for m in self.matchups:
                wr = m.wins / (m.wins + m.losses)
                new_string = '{} - {}, {:.3f} % \n'.format(m.me, m.enemy, wr * 100)
                to_return = to_return + new_string
                avg_wr += wr
            to_return += 'Average Winrate - {:.3f} % \n'.format(avg_wr*33.3333)
            return to_return
                
            
    def create_player(winner, all_points):
        subset = []
        for p in all_points:
            if p.winner == winner or p.loser == winner:
                subset.append(p)
        return Player(winner, subset)

    rankings = {}
    def add_rank(number,player):
        found = False
        for key, value in rankings.items():
            if player == key:
                value.append(number)
                found = True
                break
        if not found:
            rankings[player] = []
            rankings[player].append(number)
        
        
    files = os.listdir(archivePath)
    all_points = []
    for f in files:
        print(f)
        wb = xlrd.open_workbook(archivePath+f)
        results_sheet = wb.sheet_by_name('Results')
        for num in range(1,5):
            add_rank(num, results_sheet.cell_value(num,4))
        for col in range(0,3):
            for row in range(1, results_sheet.nrows):
                winner = results_sheet.cell_value(row, 2)
                loser = ''
                if results_sheet.cell_value(row,0) == winner:
                    loser = results_sheet.cell_value(row,1)
                else:
                    loser = results_sheet.cell_value(row,0)
                all_points.append(Point(winner,loser))

    players_done = []
    players = []
    while True:
        for p in all_points:
            if p.winner not in players_done:
                players.append(create_player(p.winner,all_points))
                players_done.append(p.winner)
        break
    for p in players:
        print(p)

    for key, value in rankings.items():
        print('{}: '.format(key))
        firsts = 0
        secs = 0
        thirs = 0
        fours = 0
        for v in value:
            if v == 1:
                firsts += 1
            elif v == 2:
                secs +=1
            elif v == 3:
                thirs += 1
            elif v == 4:
                fours += 1
        print ('Average Placing: {:.2f}'.format((firsts + secs*2 + thirs*3 + fours*4 )/len(value)))
        print('Firsts: '+ str(firsts))
        print('Seconds: ' + str(secs))
        print('Thirds: ' + str(thirs))
        print('Lasts: ' + str(fours))
        print()
        

                
        

def unique_names():
    files = os.listdir(archivePath)

    name_dict = {}
    for f in files:
        print(f)
        wb = xlrd.open_workbook(archivePath + f)
        draft_sheet = wb.sheet_by_name('Draft')

        for row in range(draft_sheet.nrows):
            for col in range(draft_sheet.ncols):
                if draft_sheet.cell_value(row,col) not in name_dict.items():
                    name_dict[draft_sheet.cell_value(row,col)] = '1'
    params = {'format' : 'json'}
    for key, value in name_dict.items():
        try:
            response = requests.get('https://api.scryfall.com/cards/search?q=' + key, params = params)
            card_dict = response.json()['data']
            found = False
            for card_entry in card_dict:
                if card_entry['name'] == key:
                    found = True
                    break
            if not found:
                print('*********' + key)
        except:
            print('Scryfall unfound')
            print(key)
    print('done')    

def firstpick_pr():
    files = os.listdir(archivePath)
    playerz = {'big big big big dumps' : [0,0],
               'shinydog': [0,0],
               'Alexotl': [0,0],
               'Nenni': [0,0]}
    for f in files:
        wb = xlrd.open_workbook(archivePath + f)
        draft_sheet = wb.sheet_by_name('Draft')
        play_sheet = wb.sheet_by_name('Play')

        for col in range(4):
            found = False
            player_name = draft_sheet.cell_value(0,col)
            card_name = draft_sheet.cell_value(1,col)
            for ccol in range(play_sheet.ncols):
                for row in range(play_sheet.nrows):
                    if card_name == play_sheet.cell_value(row, ccol):
                        found = True
            if found:
                playerz[player_name][0] += 1
            playerz[player_name][1] += 1
            print(playerz)
            

def find_card(card_name, technical):
    files = os.listdir(archivePath)

    for f in files:
        wb = xlrd.open_workbook(archivePath + f)
        draft_sheet = wb.sheet_by_name('Draft')

        for row in range(draft_sheet.nrows):
            for col in range(draft_sheet.ncols):
                if card_name == draft_sheet.cell_value(row,col):
                    if technical:
                        print('{} - {}, {}'.format(f, row, col))
                    else:
                        if col < 5:
                            print('Draft {} - {}, Pack {} Pick {}'.format(f, draft_sheet.cell_value(0, col), (row//17)+1, (row%17)+1))


def graphify_wr_pr():
    x = []
    y = []
    z = []
    
    with open(str(Path().absolute()) + '\\metadata.csv', newline='') as csvfile:
        creader = csv.reader(csvfile)
        for row in creader:
            if row[5] == 'Winrate':
                continue
            if row[5] == 'n/a':
                continue
            x.append(float(row[2]))
            y.append(float(row[5]))
            z.append(row[0])
    plt.scatter(x,y)
    for word_no in range(len(z)):
        plt.annotate(z[word_no], (x[word_no], y[word_no]))
    plt.show()

def determine_position(card_count):
    x = 0
    y = 0
    if card_count > 4:
        if card_count > 9:
            y = 1800
        else:
            y = 900
    if card_count%5 == 1:
        x = 500
    elif card_count%5 == 2:
        x = 1000
    elif card_count%5 == 3:
        x = 1500
    elif card_count%5 == 4:
        x = 2000
    return x,y

def multicolor_pr_wr():
            
    multicards= ['Reflector Mage','Teferi, Time Raveler','Fractured Identity','Teferi, Hero of Dominaria','Baleful Strix','Master of Death','Psychatog','The Scarab God','Rakdos Headliner','Daretti, Ingenious Iconoclast',
    'Judith, the Scourge Diva','Kolaghan\'s Command','Wrenn and Six','Bloodbraid Elf','Sarkhan Vol','Dragonlord Atarka','Qasali Pridemage','Voice of Resurgence','Knight of Autumn','Mirari\'s Wake',
    'Vanishing Verse','Lingering Souls','Vindicate','Kaya, Ghost Assassin','Sprite Dragon','Dack Fayden','Prismari Command','Saheeli, the Gifted','Assassin\'s Trophy','Grist, the Hunger Tide',
    'Maelstrom Pulse','Pernicious Deed','Boros Charm','Rip Apart','Tajic, Legion\'s Edge','Ajani Vengeant','Hydroid Krasis','Edric, Spymaster of Trest','Oko, Thief of Crowns',
    'Uro, Titan of Nature\'s Wrath','Hostage Taker','Dreadbore','Lightning Helix','Garruk, Cursed Hunstman','Sorin, Lord of Innistrad','Ral Zarek','Izzet Charm','Dream Trawler''Tezzeret, Agent of Bolas']
    storePath = str(Path().absolute())
    stored_cards = []
    with open('C:\\Users\\Evan Wu\\Desktop\\cube_hijinx\\metadata.csv', 'r', newline ='') as bigfile:
        bigreader = csv.DictReader(bigfile)
        for row in bigreader:
            if row['Card Name'] in multicards:
                stored_cards.append(row)
        stored_cards.sort(key = lambda x: float(x['Avg. Pick Number']), reverse = True)
        canvas_x = 2500
        canvas_y = 2700
        new_image = Image.new('RGB', (canvas_x,canvas_y))
        draw = ImageDraw.Draw(new_image)
        image_name = storePath + '\\multicolor.png'
        params = {'format' : 'json'}
        myFont = ImageFont.truetype('888_MRG.ttf', 38)
        
        for i in range(15):
                
            response = requests.get('https://api.scryfall.com/cards/search?q=' + stored_cards[i]['Card Name'], params = params)
            card_dict = response.json()['data']
            for card_entry in card_dict:
                if card_entry['name'] == stored_cards[i]['Card Name']:
                    print(stored_cards[i]['Card Name'])
                    try:
                        temp_image_url = card_entry['image_uris']['normal']
                    except:
                        temp_image_url = card_entry['card_faces'][0]['image_uris']['normal']
                    temp_image = Image.open(io.BytesIO(requests.get(temp_image_url).content))
                    new_image.paste(temp_image, determine_position(i))
                    break
            curr_x, curr_y = determine_position(i)
            curr_y += 700
            draw.text((curr_x, curr_y), 'Avg Pick: {}'.format(stored_cards[i]['Avg. Pick Number']), (255,255,255), font=myFont)
            curr_y += 60
            draw.text((curr_x, curr_y), 'Winrate: {}'.format(float(stored_cards[i]['Winrate'])), (255,255,255), font=myFont)
        new_image = new_image.resize((round(new_image.size[0]* 0.75), round(new_image.size[1] *0.75)))
        new_image.save(image_name)

def most_coveted(n):
    storePath = str(Path().absolute())
    with open('C:\\Users\\Evan Wu\\Desktop\\cube_hijinx\\metadata.csv', 'r', newline ='') as bigfile:
        bigreader = csv.DictReader(bigfile)
             
        with open('C:\\Users\\Evan Wu\\Desktop\\cube_hijinx\\metadata_{}.csv'.format(n), 'r', newline ='') as csvfile:
            listocards = []
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                temp_row = row
                for big_row in bigreader:
                    if big_row['Card Name'] == temp_row['Card Name']:
                        temp_row['diff'] = float(big_row['Avg. Pick Number']) - float(temp_row['Avg. Pick Number'])
                        temp_row['diff_draft'] = big_row['Times Drafted']
                        break
                if temp_row['Times Drafted'] == '1' or 'diff' not in temp_row:
                    temp_row['diff'] = 0
                    temp_row['diff_draft'] = 0
                print(temp_row['diff'])
                listocards.append(temp_row)
            listocards.sort(key = lambda x : x['diff'], reverse=True)

            canvas_x = 2500
            canvas_y = 2700
            new_image = Image.new('RGB', (canvas_x,canvas_y))
            draw = ImageDraw.Draw(new_image)
            image_name = storePath + '\\most covetous {}.png'.format(n)
            params = {'format' : 'json'}
            myFont = ImageFont.truetype('888_MRG.ttf', 38)

            for i in range(15):
                
                response = requests.get('https://api.scryfall.com/cards/search?q=' + listocards[i]['Card Name'], params = params)
                card_dict = response.json()['data']
                for card_entry in card_dict:
                    if card_entry['name'] == listocards[i]['Card Name']:
                        print(listocards[i]['Card Name'])
                        try:
                            temp_image_url = card_entry['image_uris']['normal']
                        except:
                            temp_image_url = card_entry['card_faces'][0]['image_uris']['normal']
                        temp_image = Image.open(io.BytesIO(requests.get(temp_image_url).content))
                        new_image.paste(temp_image, determine_position(i))
                        break
                curr_x, curr_y = determine_position(i)
                curr_y += 700
                draw.text((curr_x, curr_y), 'Avg Pick: {}'.format(listocards[i]['Avg. Pick Number']), (255,255,255), font=myFont)
                curr_y += 60
                draw.text((curr_x, curr_y), 'Global Avg Pick: {}'.format(float(listocards[i]['Avg. Pick Number']) + listocards[i]['diff']), (255,255,255), font=myFont)
                curr_y += 60
                draw.text((curr_x, curr_y), 'Times Drafted: {}/{}'.format(listocards[i]['Times Drafted'],listocards[i]['diff_draft']), (255,255,255), font=myFont)
            new_image = new_image.resize((round(new_image.size[0]* 0.75), round(new_image.size[1] *0.75)))
            new_image.save(image_name)
            

def most_played():
    storePath = str(Path().absolute())
    names = ['big big big big dumps', 'Alexotl', 'shinydog', 'Nenni']
    for n in names:
        with open('C:\\Users\\Evan Wu\\Desktop\\cube_hijinx\\metadata_{}.csv'.format(n), 'r', newline ='') as csvfile:
            listocards = []
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                listocards.append(row)
            listocards.sort(key = lambda x : float(x['Times Played']), reverse=True)

            canvas_x = 2500
            canvas_y = 2700
            new_image = Image.new('RGB', (canvas_x,canvas_y))
            draw = ImageDraw.Draw(new_image)
            image_name = storePath + '\\most played {}.png'.format(n)
            params = {'format' : 'json'}
            myFont = ImageFont.truetype('888_MRG.ttf', 50)

            for i in range(15):
                
                response = requests.get('https://api.scryfall.com/cards/search?q=' + listocards[i]['Card Name'], params = params)
                card_dict = response.json()['data']
                for card_entry in card_dict:
                    if card_entry['name'] == listocards[i]['Card Name']:
                        print(listocards[i]['Card Name'])
                        try:
                            temp_image_url = card_entry['image_uris']['normal']
                        except:
                            temp_image_url = card_entry['card_faces'][0]['image_uris']['normal']
                        temp_image = Image.open(io.BytesIO(requests.get(temp_image_url).content))
                        new_image.paste(temp_image, determine_position(i))
                        break
                curr_x, curr_y = determine_position(i)
                curr_y += 700
                draw.text((curr_x, curr_y), 'Times Played: {}'.format(listocards[i]['Times Played']), (255,255,255), font=myFont)
                curr_y += 60
                draw.text((curr_x, curr_y), 'Matches: {}'.format(listocards[i]['Matches Played']), (255,255,255), font=myFont)
                curr_y += 60
                draw.text((curr_x, curr_y), 'Winrate: {}%'.format(listocards[i]['Winrate']), (255,255,255), font=myFont)
            new_image = new_image.resize((round(new_image.size[0]* 0.75), round(new_image.size[1] *0.75)))
            new_image.save(image_name)

