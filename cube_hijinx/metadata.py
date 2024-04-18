from pathlib import Path
import csv
import os
import xlrd
archivePath = str(Path().absolute()) + '\\archive\\'


class Player:
    def __init__(self, p_name, p_aggr_po, p_pick=1, p_deck=0, p_win=0,p_total=0):
        self.p_name = p_name
        self.p_aggr_po = p_aggr_po
        self.p_pick = p_pick
        self.p_deck = p_deck
        self.p_win =  p_win
        self.p_total =p_total
class Card:
    def __init__(self, name, aggr_pick_order, player_name, pick_times=1,
                 deck_times=0, win_games=0, total_games=0):
        self.name = name
        self.aggr_pick_order = aggr_pick_order
        self.pick_times = pick_times
        self.deck_times = deck_times
        self.win_games = win_games
        self.total_games = total_games
        self.players = []
        self.players.append(Player(player_name, aggr_pick_order))
    def __lt__(self, other):
        return self.aggr_pick_order / self.pick_times < other.aggr_pick_order / other.pick_times
    def to_row(self):
        winrate = 'n/a'
        avg_pick = '{:.2f}'.format(self.aggr_pick_order / self.pick_times)
        try:
            winrate = '{:.2f}'.format(self.win_games / self.total_games)
        except:
            pass
        return [self.name, self.pick_times, avg_pick, self.deck_times, self.total_games, winrate]
    def to_player_row(self, player_name):
        winrate = 'n/a'
        for p in self.players:
            if p.p_name == player_name:
                avg_pick = '{:.2f}'.format(p.p_aggr_po / p.p_pick)
                try:
                    winrate = '{:.2f}'.format(p.p_win / p.p_total)
                except Exception as e:
                    print(e)
                    pass
                return [ self.name, p.p_pick, avg_pick, p.p_deck, p.p_total, winrate]
        return None
        
    def add_player(self, player_name, pick):
        found_player = False
        for p in self.players:
            if p.p_name == player_name:
                p.p_pick += 1
                p.p_aggr_po += pick
                found_player = True
                break
        if not found_player:
            self.players.append(Player(player_name, pick))
    def update_play_player(self, player_name, player_results):
        for p in self.players:
            if p.p_name == player_name:
                p.p_deck += 1
                p.p_win += player_results[player_name][0]
                p.p_total += player_results[player_name][1]
                break
def find_card_index(card_name, all_cards):
    for card_no in range(len(all_cards)):
        if card_name == all_cards[card_no].name:
            return card_no
    return -1
            
    

def generate_metadata():

    all_cards = []
    draft_min_row = 1
    draft_max_row = 48
    draft_max_col = 4
     
    files = os.listdir(archivePath)

    for f in files:
        print(f)
        wb = xlrd.open_workbook(archivePath + f)
        draft = wb.sheet_by_name('Draft')
        counter = 0
        for row in range(draft_min_row, draft_max_row):
            for col in range( draft_max_col):
                #
                player_name = draft.cell_value(0,col)
                curr_card = draft.cell_value(row,col)
                
                if curr_card is None or curr_card == '':
                    continue
                counter+= 1
                card_index = find_card_index(curr_card, all_cards)
                if card_index == -1:
                    all_cards.append(Card(curr_card, row%16, player_name))
                else:
                    all_cards[card_index].pick_times += 1
                    all_cards[card_index].aggr_pick_order += row%16
                    all_cards[card_index].add_player(player_name, row%16)
        
        play = wb.sheet_by_name('Play')
        results = wb.sheet_by_name('Results')
        print(counter)
        player_results = {}
        def update_results(player, player_results, won):
            if won:
                if player not in player_results.keys():
                    player_results[player] = [1,1]
                else:
                    player_results[player][0] += 1
                    player_results[player][1] += 1
            else:
                if player not in player_results.keys():
                    player_results[player] = [0,1]
                else:
                    player_results[player][1] += 1
        for row in range(1, results.nrows):
            p1 = results.cell_value(row, 0)
            p2 = results.cell_value(row, 1)
            w1 = results.cell_value(row, 2)
            update_results(w1, player_results, True)
            if p1 != w1:
                update_results(p1, player_results, False)
            else:
                update_results(p2, player_results, False)

        print(player_results)
        
        for col in range(play.ncols):
            curr_player = play.cell_value(0, col)
            for row in range(1, play.nrows):
                curr_card = play.cell_value(row,col)
                if curr_card is None or curr_card == '':
                    break
                curr_index = find_card_index(curr_card, all_cards)
                if curr_index == -1:
                    continue
                all_cards[curr_index].deck_times += 1
                all_cards[curr_index].win_games += player_results[curr_player][0]
                all_cards[curr_index].total_games += player_results[curr_player][1]
                all_cards[curr_index].update_play_player(curr_player, player_results)

    header = ['Card Name', 'Times Drafted', 'Avg. Pick Number', 'Times Played', 'Matches Played', 'Winrate']
    with open('C:\\Users\\Evan Wu\\Desktop\\cube_stuffs 210821\\metadata.csv', 'w', newline ='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)
        for card in all_cards:
            csvwriter.writerow(card.to_row())
    print('yayuz')
    playerz = ['big big big big dumps', 'shinydog', 'Alexotl', 'Nenni']
    for p in playerz:
        with open('C:\\Users\\Evan Wu\\Desktop\\cube_stuffs 210821\\metadata_{}.csv'.format(p), 'w', newline ='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(header)
            for card in all_cards:
                if card.to_player_row(p) is None:
                    continue
                csvwriter.writerow(card.to_player_row(p))

def main():
    generate_metadata()

if __name__ == '__main__':
    main()
            
