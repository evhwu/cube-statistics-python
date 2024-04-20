import os
import pandas as pd
import requests



save_path = os.getcwd() + "\\cube_hijinx\\archive\\"
store_path = os.getcwd() + "\\cube_hijinx\\pngs\\"
mana_symbol_path = os.getcwd() + "\\cube_hijinx\\mana\\"

def color_profile():
    files = os.listdir(save_path)
    players = {}
    params = {'format : json'}

    for f in files:
        print(f)
        #winning
        player_rank = {}
        win_df = pd.read_excel(save_path + f, sheet_name="Results")
        results = win_df["Ranking"]
        for x in range(4):
            player_rank[results[x]] = x

        df = pd.read_excel(save_path + f, sheet_name="Play")
        for series_name, series in df.items():
            print(series_name)
            deck_symbols = ''
            if series_name not in players:
                players[series_name] =  {'W':0,'U':0,'B':0,'R':0,'G':0, 'color_profs':[]}
            for card in series:
                if not isinstance(card,str):
                    continue
                response = requests.get('https://api.scryfall.com/cards/search?q=' + card)
                card_dict = response.json()['data']
                for card_entry in card_dict:
                    manacost = ''
                    if 'card_faces' in card_entry:
                        print(card)
                        #for face_num in range(len(card_entry['card_faces'])):
                        #    manacost += card_entry['card_faces'][face_num]['mana_cost']
                        #    print(card)
                        #    print(manacost)
                    



    
        


if __name__ == '__main__':
    color_profile()
