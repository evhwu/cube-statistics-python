import os
import pandas as pd

save_path = os.getcwd() + "\\cube_hijinx\\test_archive\\"

def winrates():
    class Player:
        def __init__(self, name):
            self.name = name
            self.matchups = {}
            self.rankings = [0] * 4
        def update_matchup(self, enemy, won):
            if enemy in self.matchups:
                


        class Matchup():
            def __init__(self, enemy, won):
                self.enemy = enemy
                if won:
                    self.wins, self.losses = 1, 0
                else:
                    self.wins, self.losses = 0, 1
    
    files = os.listdir(save_path)
    players = {}
    for f in files:
        df = pd.read_excel(save_path + f, sheet_name = "Results")
        winners = df["Winner"]
        p1 = df["Player 1"]
        p2 = df["Player 2"]
        
        def check_players(name):
            if name not in players:
                players[name] = Player()
        for row in df.index:
            winner, loser = p2[row], p1[row]
            if p1[row] == winners[row]:
                winner, loser = p1[row], p2[row]
            check_players(winner)
            check_players(loser)

            
        



if __name__ == '__main__':
    winrates()