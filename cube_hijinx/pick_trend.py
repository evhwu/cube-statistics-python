import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
import os
import csv
import pandas
import xlrd
import numpy as np
archivePath = str(Path().absolute()) + '\\archive\\'


def pack_order(draft_no, pack_no):

    meta_f = ["", "_Alexotl", "_big big big big dumps", "_Nenni", "_shinydog"]
    colors = [mpatches.Patch(color='black', label ='Pack'),
              mpatches.Patch(color='yellow', label ='Average'),
              mpatches.Patch(color='blue', label ='big big big big dumps'),
              mpatches.Patch(color='green', label ='Alexotl'),
              mpatches.Patch(color='purple', label ='Nenni'),
              mpatches.Patch(color='red', label ='shinydog'),]
    wb = xlrd.open_workbook(archivePath + str(draft_no) + '.xlsx')
    draft_sheet = wb.sheet_by_name('Draft')


    starting_row = [1, 17, 33]
    for col in range(5,9):
        x = []
        y = []
        index = []
        
        scatter_color = []
        counter = 0
        start = col -5
        for i in range(0,14):
            if draft_sheet.cell_value(0, start) == 'Alexotl':
                scatter_color.append('green')
            elif draft_sheet.cell_value(0, start) == 'Nenni':
                scatter_color.append('purple')
            elif draft_sheet.cell_value(0, start) == 'shinydog':
                scatter_color.append('red')
            else:
                scatter_color.append('blue')
            if pack_no%2 == 0:
                if start == 3:
                    start = 0
                else:
                    start += 1
            else:
                if start == 0:
                    start = 3
                else:
                    start -=1
                
        
        print(scatter_color)
        
        for row in range(starting_row[pack_no-1], starting_row[pack_no-1] + 15):
            x.append(row%16)
            y.append(row%16)
            index.append(draft_sheet.cell_value(row, col))

        short_index = []
        for i in index:
            if "//" in i:
                short_index.append(i.split(" // ")[0])
            else:
                short_index.append(i)
        plt.plot(x, y, color='black')
        plt.xticks(ticks=x, labels=short_index, fontsize=6)

        for xp, yp, c in zip(x, y, scatter_color):
            plt.scatter([xp],[yp], color=c)
        
        for mf in meta_f:
            curr_col = ""
            if mf == "_Alexotl":
                curr_col = 'green'
            elif mf == "_Nenni":
                curr_col = 'purple'
            elif mf == "_shinydog":
                curr_col = 'red'
            elif mf == "":
                curr_col = 'yellow'
            else:
                curr_col = 'blue'
            print(mf)
            x_copy = x.copy()
            y = []
            for i in index:
                found = False
                with open(str(Path().absolute()) + '\\metadata' + mf + '.csv', newline = '') as csvfile:
                    creader = csv.reader(csvfile)
                    for row in creader:
                        if row[0] == i:
                            found = True
                            y.append(float(row[2]))
                            break
                if not found:
                    x_copy.pop(len(y)-1)
            plt.plot(x_copy,y,color=curr_col)
            
        axes = plt.gca()
        axes.set_ylim([0,15])
        axes.set_xlim([0,15])
        plt.grid()
        plt.legend(handles=colors)
        plt.show()
    

def card_pickrate(card_name):
    files = os.listdir(archivePath)
    x =[]
    y =[]
    for f in files:
        wb = xlrd.open_workbook(archivePath + f)
        draft_sheet = wb.sheet_by_name('Draft')

        found = False
        for row in range(draft_sheet.nrows):
            for col in range(draft_sheet.ncols):
                if card_name == draft_sheet.cell_value(row,col):
                    x.append(int(''.join(i for i in f if i.isdigit())))
                    r= row -1
                    y.append(row%16)
                    found = True
                    break
            if found:
                break

    print(x)
    print(y)

    import seaborn as sns
    data = pandas.DataFrame()
    data['x'] = x
    data['y'] = y
    #data = pandas.DataFrame(list(zip(x,y)))
    #pandas.DataFrame(data, columns=['x','y'])
    sns.regplot(x='x',y='y',data=data, fit_reg=True)
    axes = plt.gca()
    axes.set_ylim([0,15])
    plt.show()

def card_pickrateF(card_name):
    files = os.listdir(archivePath)
    x = []
    y = []
    cluster = []
    color = []
    last_file = ''
    for f in files:
        last_file = f
        wb = xlrd.open_workbook(archivePath + f)
        draft_sheet = wb.sheet_by_name('Draft')

        found = False
        for row in range(draft_sheet.nrows):
            for col in range(draft_sheet.ncols):
                if card_name == draft_sheet.cell_value(row,col):
                    found = True
                    x.append(int(''.join(i for i in f if i.isdigit())))
                    y.append(row%16)
                    if draft_sheet.cell_value(0,col) == 'shinydog':
                        cluster.append('P')
                        color.append('red')
                    elif draft_sheet.cell_value(0,col) == 'Alexotl':
                        cluster.append('^')
                        color.append('green')
                    elif draft_sheet.cell_value(0,col) == 'big big big big dumps':
                        cluster.append('o')
                        color.append('blue')
                    elif draft_sheet.cell_value(0,col) == 'Nenni':
                        cluster.append('s')
                        color.append('purple')
                    break
            if found:
                break

    last_file =''.join(i for i in last_file if i.isdigit())
    
    #cluster = ['^','^','^','s','s']
    print(last_file)
    fig, ax = plt.subplots()

    for xp, yp, m, c in zip(x, y, cluster, color):
        ax.scatter([xp],[yp], marker=m, color =c)
    axes = plt.gca()
    axes.set_ylim([0,15])
    #axes.set_xlim([18, int(last_file)+1])

    plt.show()
