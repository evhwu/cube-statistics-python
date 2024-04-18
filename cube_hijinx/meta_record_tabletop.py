import xlsxwriter
import requests
from time import sleep
import json

playerFile = open('C:\\Users\\Evan\\Desktop\\Project Code\\cube_stuffs 210821\\cube_hijinx\\player_results.txt', 'r', encoding = 'utf-8')
packsFile = open('C:\\Users\\Evan\\Desktop\\Project Code\\cube_stuffs 210821\\cube_hijinx\\packs_results.txt', 'r', encoding = 'utf-8')

#playerFile = open('C:\\Users\\Evan\\Desktop\\cube_stuffs 210821\\cube_hijinx\\player_results.txt', 'r')
#packsFile = open('C:\\Users\\Evan\\Desktop\\cube_stuffs 210821\\cube_hijinx\\packs_results.txt', 'r')
player_text_lines = playerFile.read().split('\n')
packs_text_lines = packsFile.read().split('\n')

#xlresults = xlsxwriter.Workbook('C:\\Users\\Evan\\Desktop\\cube_stuffs 210821\\cube_hijinx\\draft_results.xlsx')
xlresults = xlsxwriter.Workbook('C:\\Users\\Evan\\Desktop\\Project Code\\cube_stuffs 210821\\cube_hijinx\\draft_results.xlsx')

formats = {}
formats['Green'] = xlresults.add_format({'font_size' : 12, 'font_name': 'Cambria', 'align' : 'center', 'valign' : 'vcenter', 'bg_color' : '#78D05C'})
formats['Red'] = xlresults.add_format({'font_size' : 12, 'font_name': 'Cambria', 'align' : 'center', 'valign' : 'vcenter', 'bg_color' : '#EA6F6F'})
formats['Blue'] = xlresults.add_format({'font_size' : 12, 'font_name': 'Cambria', 'align' : 'center', 'valign' : 'vcenter', 'bg_color' : '#6FBBEA'})
formats['Purple'] = xlresults.add_format({'font_size' : 12, 'font_name': 'Cambria', 'align' : 'center', 'valign' : 'vcenter', 'bg_color' : '#AE6FEA'})
formats['Orange'] = xlresults.add_format({'font_size' : 12, 'font_name': 'Cambria', 'align' : 'center', 'valign' : 'vcenter', 'bg_color' : '#EC9130'})
formats['Yellow'] = xlresults.add_format({'font_size' : 12, 'font_name': 'Cambria', 'align' : 'center', 'valign' : 'vcenter', 'bg_color' : '#F0DC07'})
formats['Default'] = xlresults.add_format({'font_size' : 12, 'font_name': 'Cambria', 'align' : 'center', 'valign' : 'vcenter'})

draftSheet = xlresults.add_worksheet('Draft')

player_packs = []
class Player:
    def __init__(self, line_dump):
        self.name, self.color = line_dump.pop(0).split('-#-')
        self.packs = [[]]

        for line in line_dump:
            if len(self.packs[len(self.packs)-1]) == 15:
                self.packs.append([])
            self.packs[len(self.packs)-1].append(line)
    def __lt__(self, other):
        return(self.color < other.color)

line_dump = []
for line in player_text_lines:
    if '#413' in line:
        player_packs.append(Player(line_dump))
        line_dump = []
    else:
        line_dump.append(line)

player_packs = sorted(player_packs)
curr_row = 0
curr_col = 0
for player in player_packs:
    draftSheet.write(curr_row,curr_col, player.name, formats[player.color])
    for pack in player.packs:
        for card in pack:
            curr_row += 1
            draftSheet.write(curr_row,curr_col, card, formats[player.color])
        curr_row += 1
    curr_col += 1
    curr_row = 0

########################################

class DraftCard:
    def __init__(self, name, pick_no, color, player_no):
        self.name = name
        self.pick_no = pick_no
        self.color = color
        self.player_no = player_no
    def __lt__(self, other):
        return(self.pick_no < other.pick_no)

def find_card_player(card_name):
    for player_no in range(len(player_packs)):
        for pack in player_packs[player_no].packs:
            for card_no in range(len(pack)):
                if pack[card_no] == card_name:
                    return(DraftCard(card_name, card_no, player_packs[player_no].color, player_no))
    print(card_name)
    return None

def find_player_col(pack, player_packs):
    for playerCol in range(len(player_packs)):
        if pack[0].color == player_packs[playerCol].color:
            return(playerCol + 5)
    return(-1)
    
curr_row = 1
counter = 0
temp_pack = []

for line in packs_text_lines:
    if '#413' in line:
        temp_pack = sorted(temp_pack)
        curr_col = find_player_col(temp_pack, player_packs)
        for card in temp_pack:
            draftSheet.write(curr_row + card.pick_no, curr_col, card.name, formats[card.color])
        temp_pack = []
        if counter == 3:
            counter = 0
            curr_row += 16
        else:
            counter += 1
    else:
        temp_card = find_card_player(line)
        if temp_card is None:
            print('rar')
        else:
            temp_pack.append(temp_card)

#####################################

deckSheet = xlresults.add_worksheet('Play')
deckFile = open('C:\\Users\\Evan\\Desktop\\Project Code\\cube_stuffs 210821\\cube_hijinx\\deck_results.txt', 'r', encoding = 'utf-8')
deck_text_lines = deckFile.read().split('\n')

class DeckCard:
    def __init__(self, name, cmc, qty):
        self.name = name
        self.cmc = cmc
        self.qty = qty
    def __lt__(self, other):
        if self.cmc != other.cmc:
            return self.cmc < other.cmc
        else:
            return self.name < other.name

def write_deck(curr_deck, curr_col):
    cards = []
    curr_row = 0
    curr_format = formats['Default']
    for player in player_packs:
        if player.name == curr_deck[0]:
            curr_format = formats[player.color]
    deckSheet.write(curr_row, curr_col, curr_deck.pop(0), curr_format)
    curr_row += 1
    params = {'format' : 'json'}
    for line in curr_deck:
        found = False
        for c in cards:
            if c.name == line:
                c.qty += 1
                found = True
                break
        if found:
            continue
        print(line)
        request_string = 'https://api.scryfall.com/cards/search?q=' + line
        response = requests.get(request_string, params=params)

        scryfall_card_list = response.json()
        card_dict = response.json()['data']
        for card_entry in card_dict:
            if card_entry['name'] == line:
                temp_cmc = card_entry['cmc']
                cards.append(DeckCard(line, temp_cmc, 1))
                break
        sleep(.2)
        cards = sorted(cards)
    for c in cards:
        for q in range(c.qty):
            deckSheet.write(curr_row, curr_col, c.name, curr_format)
            curr_row += 1

curr_col = 0
curr_deck = []
for line in deck_text_lines:
    if '#413' in line:
        write_deck(curr_deck, curr_col)
        curr_deck = []
        curr_col += 1
    else:
        curr_deck.append(line)

#######################################

resSheet = xlresults.add_worksheet('Results')
player_index = []
header = ['Player 1', 'Player 2', 'Winner', '', 'Ranking']
resSheet.write_row(0,0,header,formats['Default'])
curr_row = 1

wins = []
for player in player_packs:
    player_index.append(player)
    wins.append(0)
for idx in range(len(player_index)):
    print(f'{idx}) {player_index[idx].name}')
while curr_row < 7:
    p1 = int(input('Enter player 1 number: '))
    p2 = int(input('Enter player 2 number: '))
    w1 = int(input('Enter the winner number: '))
    resSheet.write(curr_row, 0, player_index[p1].name, formats[player_index[p1].color])
    resSheet.write(curr_row, 1, player_index[p2].name, formats[player_index[p2].color])
    resSheet.write(curr_row, 2, player_index[w1].name, formats[player_index[w1].color])
    wins[w1] += 1
    curr_row += 1
for idx in range(len(player_index)):
    if wins[idx] == 0:
        resSheet.write(4,4, player_index[idx].name, formats[player_index[idx].color])
    elif wins[idx] == 1:
        resSheet.write(3,4, player_index[idx].name, formats[player_index[idx].color])
    elif wins[idx] == 2:
        resSheet.write(2,4, player_index[idx].name, formats[player_index[idx].color])
    else:
        resSheet.write(1,4, player_index[idx].name, formats[player_index[idx].color])

packsFile.close()
playerFile.close()
xlresults.close()
print('Done')
        
