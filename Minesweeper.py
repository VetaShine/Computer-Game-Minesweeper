import tkinter as tk
import time
from threading import Thread
from random import shuffle
from tkinter.messagebox import showinfo, showerror

colors = {1: 'blue', 2: 'green', 3: 'red', 4: 'navy', 5: 'darkred', 6: 'magenta', 7: 'purple', 8: 'gold',}

class MyButton(tk.Button):

    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, font='Calibri 15 bold', width=3, *args, **kwargs)
        self.x, self.y, self.number, self.count_bomb = x, y, number, 0
        self.is_mine, self.is_open = False, False

    def __repr__(self):
        return f'MyButton {self.x}{self.y} {self.number} {self.is_mine}'

class MineSweeper:
    window = tk.Tk()
    window.title("MineSweeper")
    row, column, mines, flags, clock, kol = 8, 8, 10, 0, 0, 0
    c_m = mines
    indexes_mines, indexes_flags = list(), list()
    is_game_over, is_victory, is_first_click, running = False, False, True, True

    def __init__(self):
        self.buttons = []
        for i in range(MineSweeper.row + 2):
            temp = []
            for j in range(MineSweeper.column + 2):
                btn = MyButton(MineSweeper.window, x=i, y=j)
                btn.config(command=lambda button=btn: self.click(button))
                btn.bind("<Button-3>", self.right_click)
                temp.append(btn)
            self.buttons.append(temp)
        self.flags_remain = tk.Label(MineSweeper.window, text='Осталось флагов: ' + str(MineSweeper.c_m))
        self.flags_remain.grid(row=MineSweeper.row + 2, column=1, columnspan=4, padx=10, pady=10)
        self.time = tk.Label(MineSweeper.window, text='0')
        self.time.grid(row=MineSweeper.row + 2, column=MineSweeper.column - 1, columnspan=2, padx=10, pady=10)

    def right_click(self, event):
        if MineSweeper.is_game_over: return
        cur_btn = event.widget
        if cur_btn['state'] == 'normal':
            cur_btn['state'] = 'disabled'
            cur_btn['text'] = '🚩'
            MineSweeper.flags += 1
            MineSweeper.kol += 1
            MineSweeper.indexes_flags.append(cur_btn.number)
            MineSweeper.c_m -= 1
            self.flags_remain.config(text='Осталось флагов: ' + str(MineSweeper.c_m))
            if MineSweeper.flags == MineSweeper.mines and MineSweeper.kol == MineSweeper.column * MineSweeper.row:
                MineSweeper.indexes_mines.sort()
                print(MineSweeper.indexes_mines)
                MineSweeper.indexes_flags.sort()
                print(MineSweeper.indexes_flags)
                if MineSweeper.indexes_mines == MineSweeper.indexes_flags:
                    MineSweeper.is_victory, MineSweeper.running = True, False
                    showinfo('Victory', 'Вы выиграли!')
        elif cur_btn['text'] == '🚩':
            cur_btn['text'] = ''
            cur_btn['state'] = 'normal'
            MineSweeper.flags -= 1
            MineSweeper.kol -= 1
            MineSweeper.indexes_flags.remove(cur_btn.number)
            MineSweeper.c_m += 1
            self.flags_remain.config(text='Осталось флагов: ' + str(MineSweeper.c_m))

    def click(self, clicked_button: MyButton):
        if MineSweeper.is_game_over: return
        if MineSweeper.is_victory: return
        MineSweeper.kol += 1
        if MineSweeper.is_first_click == True:
            MineSweeper.is_first_click = False
            self.insert_mines(clicked_button.number)
            self.count_mines_in_buttons()
            self.print_buttons()
            Thread(target=self.autoc).start()
        color = colors.get(clicked_button.count_bomb, 'black')
        if clicked_button.is_mine:
            clicked_button.config(text="💣", background='red', disabledforeground='black')
            clicked_button.is_open, MineSweeper.is_game_over, MineSweeper.running = True, True, False
            showinfo('Game over', 'Вы проиграли!')
            for i in range(1, MineSweeper.row + 1):
                for j in range(1, MineSweeper.column + 1):
                    btn = self.buttons[i][j]
                    if btn.is_mine: btn['text'] = '💣'
        elif clicked_button.count_bomb:
            clicked_button.config(text=clicked_button.count_bomb, disabledforeground=color)
            clicked_button.is_open = True
        else:
            clicked_button.config(text='', disabledforeground=color)
            clicked_button.is_open = True
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    btn = self.buttons[clicked_button.x + i][clicked_button.y + j]
                    if not btn.is_open and btn.number != 0:
                        self.click(btn)
        if MineSweeper.flags == MineSweeper.mines and MineSweeper.kol == MineSweeper.column * MineSweeper.row:
            MineSweeper.indexes_mines.sort()
            print(MineSweeper.indexes_mines)
            MineSweeper.indexes_flags.sort()
            print(MineSweeper.indexes_flags)
            if MineSweeper.indexes_mines == MineSweeper.indexes_flags:
                MineSweeper.is_victory, MineSweeper.running = True, False
                showinfo('Victory', 'Вы выиграли!')
        clicked_button.config(state='disable')
        clicked_button.config(relief='sunken')

    def reload(self):
        [child.destroy() for child in self.window.winfo_children()]
        MineSweeper.c_m = MineSweeper.mines
        MineSweeper.is_first_click = True
        MineSweeper.indexes_mines, MineSweeper.indexes_flags = list(), list()
        MineSweeper.is_victory, MineSweeper.is_game_over, MineSweeper.running = False, False, True
        MineSweeper.clock, MineSweeper.flags, MineSweeper.kol = 0, 0, 0
        self.__init__()
        self.create_widgets()

    def create_setting_win(self):
        win_setting = tk.Toplevel(self.window)
        win_setting.wm_title('Настройки')
        tk.Label(win_setting, text='Новичок (8x8-10 мин)').grid(row=0, column=0, padx=20, pady=20)
        nov_btn = tk.Button(win_setting, text="Применить",
                             command=lambda: self.nov())
        nov_btn.grid(row=0, column=1, columnspan=2, padx=20, pady=20)
        tk.Label(win_setting, text='Любитель (16x16-40 мин)').grid(row=1, column=0, padx=20, pady=20)
        lub_btn = tk.Button(win_setting, text="Применить",
                            command=lambda: self.lub())
        lub_btn.grid(row=1, column=1, columnspan=2, padx=20, pady=20)
        tk.Label(win_setting, text='Профессионал (30x16-99 мин)').grid(row=2, column=0, padx=20, pady=20)
        pro_btn = tk.Button(win_setting, text="Применить",
                            command=lambda: self.pro())
        pro_btn.grid(row=2, column=1, columnspan=2, padx=20, pady=20)
        tk.Label(win_setting, text='Особые настройки:').grid(row=3, column=0, padx=20, pady=20)
        tk.Label(win_setting, text='Количество строк:').grid(row=4, column=0)
        tk.Label(win_setting, text='Количество колонок:').grid(row=5, column=0)
        tk.Label(win_setting, text='Количество мин:').grid(row=6, column=0)
        row_entry = tk.Entry(win_setting)
        row_entry.insert(0, MineSweeper.row)
        row_entry.grid(row=4, column=1, padx=20, pady=20)
        column_entry = tk.Entry(win_setting)
        column_entry.insert(0, MineSweeper.column)
        column_entry.grid(row=5, column=1, padx=20, pady=20)
        mines_entry = tk.Entry(win_setting)
        mines_entry.insert(0, MineSweeper.mines)
        mines_entry.grid(row=6, column=1, padx=20, pady=20)
        save_btn = tk.Button(win_setting, text="Применить",
                             command=lambda: self.change_settings(row_entry, column_entry, mines_entry))
        save_btn.grid(row=7, column=0, columnspan=2, padx=20, pady=20)

    def change_settings(self, row: tk.Entry, column: tk.Entry, mines: tk.Entry):
        try:
            int(row.get()), int(column.get()), int(mines.get())
        except ValueError:
            showerror('Ошибка', 'Вы ввели неправильное значение!')
            return
        MineSweeper.row, MineSweeper.column, MineSweeper.mines = int(row.get()), int(column.get()), int(mines.get())
        self.reload()

    def nov(self):
        MineSweeper.row, MineSweeper.column, MineSweeper.mines = 8, 8, 10
        self.reload()

    def lub(self):
        MineSweeper.row, MineSweeper.column, MineSweeper.mines = 16, 16, 40
        self.reload()

    def pro(self):
        MineSweeper.row, MineSweeper.column, MineSweeper.mines = 30, 16, 99
        self.reload()

    def create_widgets(self):
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label='Новая игра', command=self.reload)
        settings_menu.add_command(label='Настройки', command=self.create_setting_win)
        settings_menu.add_command(label='Выход', command=self.window.destroy)
        menubar.add_cascade(label='Меню', menu=settings_menu)
        count = 1
        for i in range(1, MineSweeper.row + 1):
            for j in range(1, MineSweeper.column + 1):
                btn = self.buttons[i][j]
                btn.number = count
                btn.grid(row=i, column=j, sticky='NWES')
                count += 1
        for i in range(1, MineSweeper.row + 1):
            tk.Grid.rowconfigure(self.window, i, weight=1)
        for j in range(1, MineSweeper.column + 1):
            tk.Grid.columnconfigure(self.window, i, weight=1)

    def open_all_buttons(self):
        for i in range(MineSweeper.row + 2):
            for j in range(MineSweeper.column + 2):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    btn.config(text="💣", background='red', disabledforeground='black')
                elif btn.count_bomb in colors:
                    color = colors.get(btn.count_bomb, 'black')
                    btn.config(text=btn.count_bomb, fg=color)

    def print_buttons(self):
        for i in range(1, MineSweeper.row + 1):
            for j in range(1, MineSweeper.column + 1):
                btn = self.buttons[i][j]
                if btn.is_mine:
                    print('B')
                else:
                    print(btn.count_bomb)

    def insert_mines(self, number: int):
        index_mines = self.get_mines_places(number)
        print(index_mines)
        for i in range(1, MineSweeper.row + 1):
            for j in range(1, MineSweeper.column + 1):
                btn = self.buttons[i][j]
                if btn.number in index_mines:
                    btn.is_mine = True

    def count_mines_in_buttons(self):
        for i in range(1, MineSweeper.row + 1):
            for j in range(1, MineSweeper.column + 1):
                btn = self.buttons[i][j]
                count_bomb = 0
                if not btn.is_mine:
                    for row_dx in [-1, 0, 1]:
                        for col_dx in [-1, 0, 1]:
                            neighbour = self.buttons[i + row_dx][j + col_dx]
                            if neighbour.is_mine:
                                count_bomb += 1
                btn.count_bomb = count_bomb

    def get_mines_places(self, exclude_number: int):
        indexes = list(range(1, MineSweeper.column * MineSweeper.row + 1))
        indexes.remove(exclude_number)
        shuffle(indexes)
        MineSweeper.indexes_mines = indexes[:MineSweeper.mines]
        return indexes[:MineSweeper.mines]

    def start(self):
        self.create_widgets()
        MineSweeper.window.mainloop()

    def autoc(self):
        while MineSweeper.running:
            time.sleep(1)
            MineSweeper.clock += 1
            self.time.config(text=int(MineSweeper.clock))

game = MineSweeper()
game.start()
