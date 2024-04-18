from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import requests
from time import sleep
import json
import io
import xlrd
import cube_helper
from pathlib import Path
savePath = str(Path().absolute()) + "\\archive\\"
storePath = str(Path().absolute()) + "\\pngs\\"

def all_the_work(sheet, col):
    image_name = storePath + sheet.cell_value(0, col) + '.png'
    curr_row = 1
    curr_cmc = 0
    curr_curve = [[]]
    params = {'format' : 'json'}
    for row in range(sheet.nrows):
        try:
            curr_card = sheet.cell_value(curr_row, col)
        except:
            break
        if curr_card == '':
            break
        response = requests.get('https://api.scryfall.com/cards/search?q=' + curr_card, params = params)
        card_dict = response.json()['data']
        for card_entry in card_dict:
            if card_entry['name'] == curr_card:
                temp_cmc = card_entry['cmc']
                print(curr_card)
                try:
                    temp_image_url = card_entry['image_uris']['normal']
                except:
                    temp_image_url = card_entry['card_faces'][0]['image_uris']['normal']
                temp_image = Image.open(io.BytesIO(requests.get(temp_image_url).content))
                if curr_cmc != temp_cmc:
                    curr_curve.append([])
                    curr_cmc = temp_cmc
                curr_curve[len(curr_curve)-1].append(temp_image)
                break
        curr_row +=1
        sleep(0.08)
    largest_x = len(curr_curve) * 488 + 110
    largest_y = 0
    for drop in curr_curve:
        if len(drop) > largest_y:
            largest_y = len(drop)
    largest_y = largest_y * 100 + 680
    new_image = Image.new('RGB', (largest_x, largest_y))

    curr_x = 0
    curr_y = 0
    for drop in curr_curve:
        for card in drop:
            new_image.paste(card, (curr_x, curr_y))
            curr_y += 100
        curr_x += 488
        curr_y = 0

    myFont = ImageFont.truetype('888_MRG.ttf', 116)
    draw = ImageDraw.Draw(new_image)
    w, h = draw.textsize( sheet.cell_value(0,col), font=myFont)
    draw.text((largest_x - w, largest_y - h), sheet.cell_value(0,col), (255,255,255), font = myFont)
    new_image.save(image_name)

def main(file_name, steam_name=None):
    wb = xlrd.open_workbook(file_name)
    sheet = wb.sheet_by_name('Play')
    if not steam_name:
        for col in range(sheet.ncols):
            all_the_work(sheet, col)
    else:
        all_the_work(sheet, cube_helper.find_player_col(file_name, steam_name, 'Play'))

if __name__ == '__main__':
    file_name = input('Enter file name: ')
    main( savePath + file_name)

