import os
import sys
import tkinter as tk
from time import sleep
from tkinter import messagebox
from PIL import Image, ImageTk
from random import randint, choices, shuffle


class SlotMachine:
    def __init__(self):
        self.total_cash, self.bet_size = 0, 0.2
        self.bet_sizes = [0.2, 0.25, 0.5, 1.0, 2.0, 2.5, 5.0, 10.0, 20.0, 25.0, 50.0, 100.0, 200.0, 250.0, 500.0,
                          1000.0, 2000.0, 2500.0, 5000.0, 10000.0]
        self.win_amount, self.coefficient, self.card_index = 0, 1, 0
        self.auto, self.stop, self.gamble_mode, self.claim_pot = False, False, False, False
        self.red, self.black, self.bet_button, self.spin_button = False, False, None, None
        self.window = tk.Tk()
        self.window.title("Blazing Haze")
        self.window.configure(bg="#171616")
        self.window.minsize(1000, 450)
        self.window.maxsize(1000, 450)
        self.window.iconphoto(True, tk.PhotoImage(file=self.resource_path('activated_symbols/seven.png')))
        self.window.pack_propagate(False)
        self.cards = self.get_images(
            [self.resource_path('cards\AC.png'), self.resource_path('cards\AS.png'), self.resource_path('cards\AH.png'),
             self.resource_path('cards\AD.png')])
        self.symbols = self.get_images(
            [self.resource_path('symbols\cherry.png'), self.resource_path(r'symbols\lemon.png'),
             self.resource_path('symbols\orange.png'), self.resource_path(r'symbols\banana.png'),
             self.resource_path('symbols\watermelon.png'), self.resource_path(r'symbols\grape.png'),
             self.resource_path('symbols\star.png'), self.resource_path('symbols\seven.png')], width=90,
            height=90)
        self.active_symbols = self.get_images(
            [self.resource_path(r'activated_symbols\cherry.png'), self.resource_path(r'activated_symbols\lemon.png'),
             self.resource_path(r'activated_symbols\orange.png'),
             self.resource_path(r'activated_symbols\banana.png'),
             self.resource_path(r'activated_symbols\watermelon.png'),
             self.resource_path(r'activated_symbols\grape.png'),
             self.resource_path(r'activated_symbols\star.png'),
             self.resource_path(r'activated_symbols\seven.png')], width=90,
            height=90)
        self.item_probabilities = {
            self.symbols[0]: [0.2525, [1.6, 4.0, 16.0]],
            self.symbols[1]: [0.2525, [1.6, 4.0, 16.0]],
            self.symbols[2]: [0.135, [2.0, 5.0, 20.0]],
            self.symbols[3]: [0.135, [2.0, 5.0, 20.0]],
            self.symbols[4]: [0.075, [4.0, 16.0, 40.0]],
            self.symbols[5]: [0.075, [4.0, 16.0, 40.0]],
            self.symbols[6]: [0.05, [0.8, 4.0, 20.0]],
            self.symbols[7]: [0.025, [8.0, 80.0, 400.0]]
        }
        self.back_card = self.get_images([self.resource_path('cards\BCK.png')])[0]
        self.card_labels, self.cards_in_labels, self.reels = [], [], []
        self.option_window, self.option_message = None, None
        self.slot_frame = tk.Frame(self.window, bg="#333031", border=10)
        self.slot_frame.pack()
        self.create_slots()
        self.add_buttons()
        self.window.bind("<space>", lambda event: self.spin())
        self.window.bind('<Left>', lambda event: self.bet())
        self.window.bind('<Right>', lambda event: self.max_bet())
        self.window.bind('<Return>', lambda event: self.cash_out())
        self.total_cash_label = tk.Label(self.window, text="Cash: $" + str(self.total_cash), fg="white", bg="#080102",
                                         font=("Arial", 20), borderwidth=2, relief=tk.SUNKEN, highlightthickness=0)
        self.total_cash_label.pack(side=tk.LEFT, anchor=tk.NW, padx=10, pady=8)
        self.bet_size_label = tk.Label(self.window, text="Bet : $" + str(self.bet_size), fg="white", bg="#080102",
                                       font=("Arial", 20), borderwidth=2, relief=tk.SUNKEN, highlightthickness=0)
        self.bet_size_label.pack(side=tk.RIGHT, anchor=tk.NE, padx=10, pady=8)
        self.label = tk.Label(self.window, text="             ", fg="#708fff", bg="#171616", font=("Arial", 24),
                              width=50)
        self.label.place(x=300, y=380, relwidth=0.4, relheight=0.1)
        self.entry, self.cash_in_button = None, None
        self.show_input()

    def insert(self):
        try:
            self.total_cash += int(self.entry.get())
            self.update_cash()
            self.entry.destroy()
            self.cash_in_button.destroy()
            self.entry, self.cash_in_button = None, None
        except ValueError:
            pass

    @staticmethod
    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            # For PyInstaller one-file executable
            base_path = sys._MEIPASS
        else:
            # For running as a script
            base_path = os.path.abspath(os.path.dirname(sys.argv[0]))

        return os.path.join(base_path, relative_path)

    def create_slots(self):
        self.reels = self.distribute()[1]
        for row, reel in enumerate(self.reels):
            for col, symbol in enumerate(reel):
                slot_label = tk.Label(self.slot_frame, image=symbol, width=90, height=90, relief=tk.RAISED, bg="white",
                                      fg="black", font=("Arial", 16))
                slot_label.image = symbol
                slot_label.grid(row=row, column=col, padx=5, pady=5)

    def add_buttons(self):
        self.spin_button = tk.Button(self.window, text="Spin", command=lambda: self.spin(False), bg="#63020a",
                                     fg="white",
                                     font=("Arial", 14), width=10, height=3, relief=tk.RAISED, borderwidth=5,
                                     highlightthickness=1, activebackground='#ff6f00', activeforeground='#ccc8b8')
        self.bet_button = tk.Button(self.window, text="Bet", command=self.bet, bg="#a5ad00", fg="black",
                                    font=("Arial", 14),
                                    width=10, height=3, relief=tk.RAISED, borderwidth=5, highlightthickness=1,
                                    activebackground='#ddff00', activeforeground='#ccc8b8')
        cash_out_button = tk.Button(self.window, text="Cash Out", command=self.cash_out, bg="#024ea1", fg="white",
                                    font=("Arial", 14), width=10, height=3, relief=tk.RAISED, borderwidth=5,
                                    highlightthickness=1, activebackground='#2f56e0', activeforeground='white')
        autoplay_button = tk.Button(self.window, text="AutoPlay", command=lambda: self.spin(True), bg='#036610',
                                    fg='white', font=('Arial', 14), width=10, height=3, relief=tk.RAISED, borderwidth=5,
                                    highlightthickness=1, activebackground='#1ad65f', activeforeground='#ccc8b8')
        self.spin_button.pack(side=tk.RIGHT, anchor=tk.S, pady=10)
        self.bet_button.pack(side=tk.RIGHT, anchor=tk.S, pady=10)
        cash_out_button.pack(side=tk.LEFT, anchor=tk.S, pady=10)
        autoplay_button.pack(side=tk.LEFT, anchor=tk.S, pady=10)

    def hide_text(self):
        self.label.config(text="            ")
        self.window.update()

    def show_text(self, text):
        if text:
            self.label.config(text=f"WON {round(text, 2)}")
        else:
            self.label.config(text="LOST")
        self.window.update()

    def update_slots(self, final=None):
        if final is None:
            final = []
        if not final:
            columns, rows = 5, 3
            reels = [[self.symbols[randint(0, 7)] for _ in range(columns)] for _ in range(rows)]
        else:
            reels = final
        for row, reel in enumerate(reels):
            for col, symbol in enumerate(reel):
                slot_label = self.slot_frame.grid_slaves(row=row, column=col)[0]
                slot_label.config(image=symbol)
                slot_label.image = symbol

    def update_cash(self):
        self.total_cash_label.config(text="Cash: $" + str(self.total_cash))
        self.window.update()

    def update_bet_size(self):
        self.bet_size_label.config(text="Bet : $" + str(self.bet_size))
        self.window.update()

    def gamble_red(self):
        self.red = True

    def gamble_black(self):
        self.black = True

    def check_condition(self):
        for _ in range(500):
            if self.black or self.red:
                return True
            elif self.claim_pot:
                return False
            else:
                sleep(0.2)
                self.window.update()
                if self.option_window:
                    self.option_window.update()
        return False

    def highlight_symbols(self, streak_symbols, duration=4.0):
        streak_symbols = streak_symbols[0]
        for _ in range(int(duration * 2.5)):
            if self.stop:
                break
            for win in streak_symbols:
                image = self.active_symbols[self.symbols.index(win[0])]
                for row, col in win[2]:
                    slot_label = self.slot_frame.grid_slaves(row=row, column=col)[0]
                    slot_label.config(image=image)
                    slot_label.image = image
                    self.window.update()
            sleep(0.2)
            for win in streak_symbols:
                for row, col in win[2]:
                    slot_label = self.slot_frame.grid_slaves(row=row, column=col)[0]
                    slot_label.config(image=win[0])
                    slot_label.image = win[0]
                    self.window.update()
            sleep(0.2)

    def gamble(self):
        self.gamble_mode, self.red, self.black = True, False, False
        color = choices([0, 1, 2, 3], [0.25, 0.25, 0.25, 0.25])[0]
        self.check_condition()
        if self.claim_pot:
            return True
        self.card_labels[self.card_index].config(image=self.cards[color])
        if len(self.cards_in_labels) < 4:
            self.cards_in_labels.append(self.cards[color])
        else:
            self.cards_in_labels.pop(0)
            self.cards_in_labels.append(self.cards[color])
        if self.card_index < 3:
            self.card_index += 1
        else:
            for index in range(len(self.cards_in_labels)):
                self.card_labels[index].config(image=self.cards_in_labels[index])
        if self.black:
            if color == 0 or color == 1:
                self.coefficient *= 2
                self.option_message.config(text=f'POT {self.win_amount * self.coefficient}')
                self.show_text(self.win_amount * self.coefficient)
                self.gamble()
            else:
                self.coefficient = 0
                self.gamble_mode = False
                self.option_message.config(text=f'LOST')
                self.show_text(self.win_amount * self.coefficient)
                sleep(1.2)
                self.option_window.destroy()
                self.option_window = None
                return False
        elif self.red:
            if color == 2 or color == 3:
                self.coefficient *= 2
                self.option_message.config(text=f'POT {self.win_amount * self.coefficient}')
                self.show_text(self.win_amount * self.coefficient)
                self.gamble()
            else:
                self.coefficient = 0
                self.gamble_mode = False
                self.option_message.config(text=f'LOST')
                self.show_text(self.win_amount * self.coefficient)
                sleep(1.2)
                self.option_window.destroy()
                self.option_window = None
                return False

    def stop_spin(self):
        self.auto, self.stop = False, True

    def spin(self, auto=False):
        self.hide_text()
        self.auto = auto
        self.win_amount, self.coefficient = 0, 1
        self.claim_pot, self.stop = False, False
        self.gamble_mode, self.red, self.black = False, False, False
        if self.total_cash:
            if self.total_cash >= self.bet_size:
                self.window.unbind("<space>")
                self.window.bind("<space>", lambda event: self.stop_spin())
                self.spin_button.config(command=self.stop_spin)
                self.total_cash = round(self.total_cash - self.bet_size, 2)
                self.update_cash()
                spin_duration, spin_interval = 1.2, 0.1
                spin_frames = int(spin_duration / spin_interval)
                dest = self.distribute()
                for _ in range(spin_frames):
                    if self.stop:
                        self.update_slots(dest[1])
                        self.window.update()
                        break
                    for reel in self.reels:
                        shuffle(reel)
                    self.update_slots()
                    self.window.update()
                    sleep(spin_interval)
                else:
                    self.update_slots(dest[1])
                    self.window.update()
                sleep(0.2)
                self.window.unbind("<space>")
                self.window.bind("<space>", lambda event: self.spin())
                self.spin_button.config(command=lambda: self.spin(False))
                if (win := self.calculate_win(dest[0], self.bet_size)) > 0:
                    self.win_amount = win
                    self.show_text(self.win_amount * self.coefficient)
                    if not self.auto:
                        self.window.unbind('<space>')
                        self.window.unbind('<Left>')
                        self.window.unbind('<Right>')
                        self.bet_button.config(command=lambda: None)
                        self.spin_button.config(command=lambda: None)
                        self.window.bind("<space>", lambda event: self.stop_spin())
                        self.stop = False
                        self.highlight_symbols(dest, duration=2.5)
                        self.window.bind('<space>', lambda event: self.claim())
                        self.window.bind('<Left>', lambda event: self.gamble_red())
                        self.window.bind('<Right>', lambda event: self.gamble_black())
                        self.bet_button.config(command=self.gamble_red)
                        self.spin_button.config(command=lambda: self.claim(force=True))
                        if self.check_condition():
                            self.open_second_window()
                        else:
                            self.claim(force=True)
                        self.window.unbind('<space>')
                        self.window.unbind('<Left>')
                        self.window.unbind('<Right>')
                        sleep(0.2)
                        self.window.bind('<space>', lambda event: self.spin())
                        self.window.bind('<Left>', lambda event: self.bet())
                        self.window.bind('<Right>', lambda event: self.max_bet())
                        self.bet_button.config(command=self.bet)
                        self.spin_button.config(command=lambda: self.spin(False))
                        sleep(0.5)
                    else:
                        self.highlight_symbols(dest, duration=1.5)
                        self.claim(force=True)
                        sleep(0.6)
                        self.spin(self.auto)
                if self.auto:
                    sleep(1.2)
                    self.spin(self.auto)
            else:
                messagebox.showinfo("Bet higher than total Cash", "Bet is higher than total cash, lower it or cash in!")
                self.show_input()
        else:
            messagebox.showinfo("No Cash Balance", "Not enough cash to spin. Please insert money to continue.")
            self.show_input()

    def show_input(self):
        if not self.entry and not self.cash_in_button:
            self.entry = tk.Entry(self.window, bg='white', fg='black', relief='solid', bd=2, font=(None, 12))
            self.entry.place(x=10, y=10, relheight=0.07)
            self.entry.focus_set()
            self.cash_in_button = tk.Button(self.window, text="Insert Cash", command=self.insert, bg='black',
                                            fg='white', relief=tk.RAISED, bd=2)
            self.cash_in_button.place(x=13, y=45, relheight=0.035, relwidth=0.1)

    @staticmethod
    def get_images(images, width=70, height=120):
        return [ImageTk.PhotoImage(Image.open(image).resize((width, height), Image.LANCZOS)) for image in images]

    def open_second_window(self):
        if self.option_window:
            return True
        self.option_window = tk.Toplevel(self.window, bg='#161f30')
        self.option_window.title("Claim or Gamble")
        self.option_window.bind('<space>', lambda event: self.claim(force=True))
        self.option_window.bind('<Left>', lambda event: self.gamble_red())
        self.option_window.bind('<Right>', lambda event: self.gamble_black())

        frame = tk.Frame(self.option_window, bg='#142e38', relief=tk.RAISED, borderwidth=1, highlightthickness=0)
        frame.pack(side=tk.RIGHT, anchor=tk.S, padx=10, pady=10)

        black_button = tk.Button(frame, text="BLACK", command=self.gamble_black, bg='black', fg='white',
                                 relief=tk.RIDGE, borderwidth=4, highlightthickness=0, activebackground='gray',
                                 activeforeground='black')
        black_button.pack(side=tk.BOTTOM, padx=10, pady=10)

        red_button = tk.Button(frame, text="RED", command=self.gamble_red, bg='red', fg='black', relief=tk.RIDGE,
                               borderwidth=4, highlightthickness=0, activebackground='pink', activeforeground='gray')
        red_button.pack(side=tk.TOP, padx=10, pady=10)

        claim_button = tk.Button(self.option_window, text="Claim", command=lambda: self.claim(force=True), bg='#0c660f',
                                 fg='#d1c89d', relief=tk.RAISED, borderwidth=5, highlightthickness=1,
                                 activebackground='#1ad65f', activeforeground='#ccc8b8')
        claim_button.pack(side=tk.LEFT, anchor=tk.S, padx=10, pady=10)

        self.card_labels = []
        if self.card_index == 0:
            for i in range(5):
                card_label = tk.Label(self.option_window, image=self.back_card)
                card_label.pack(side=tk.RIGHT, anchor=tk.E, padx=10)
                self.card_labels.append(card_label)
        else:
            for i in range(len(self.cards_in_labels)):
                card_label = tk.Label(self.option_window, image=self.cards_in_labels[i])
                card_label.pack(side=tk.RIGHT, anchor=tk.E, padx=10)
                self.card_labels.append(card_label)
            for i in range(5 - len(self.cards_in_labels)):
                card_label = tk.Label(self.option_window, image=self.back_card)
                card_label.pack(side=tk.RIGHT, anchor=tk.E, padx=10)
                self.card_labels.append(card_label)

        self.option_message = tk.Label(self.option_window, height=4, width=30, font=("Arial", 10), bg='#0d2063',
                                       fg='#8a8a8a', relief=tk.SUNKEN, bd=2)
        self.option_message.pack(side=tk.LEFT, anchor=tk.NW, padx=10, pady=10)
        self.option_message.config(text=f'POT {self.win_amount * self.coefficient}')

        self.option_window.maxsize(750, 250)
        self.option_window.minsize(750, 250)
        self.option_window.focus_force()
        self.gamble()

    def claim(self, force=False):
        self.claim_pot = True
        if force:
            self.total_cash = round(self.total_cash + self.win_amount * self.coefficient, 2)
            self.update_cash()
            if self.option_window:
                self.option_window.destroy()
                self.option_window = None

    def calculate_win(self, won_pot, bet):
        total_win = 0
        for win in won_pot:
            total_win += self.item_probabilities[win[0]][1][win[1]] * bet
        return total_win

    def bet(self):
        try:
            if self.total_cash >= (bet := self.bet_sizes[self.bet_sizes.index(self.bet_size) + 1]):
                self.bet_size = bet
            else:
                self.bet_size = 0.2
        except (ValueError, IndexError):
            self.bet_size = 0.2
        self.update_bet_size()

    def max_bet(self):
        self.bet_size = min(self.bet_sizes[-1], self.total_cash)
        self.update_bet_size()

    def auto_spin(self):
        while True:
            self.spin(True)

    def cash_out(self):
        if self.cash_in_button and self.entry:
            self.insert()
        else:
            messagebox.showinfo("Cash out", f"Cashing out. Total cash: {self.total_cash}")
            self.window.destroy()

    def start(self):
        self.window.mainloop()

    def pick_symbols(self, columns, rows):
        return [[choices([symbol for symbol in self.symbols],
                         [prob[0] for symbol, prob in self.item_probabilities.items()])[0] for _ in
                 range(columns)] for _ in range(rows)]

    def distribute(self):
        win_pattern = []
        columns, rows = 5, 3
        slot_matrix = self.pick_symbols(columns, rows)
        for row_nr, row in enumerate(slot_matrix):
            if (item := row[0]) == row[1] == row[2] == row[3] == row[4]:
                win_pattern.append([item, 2, [[row_nr, 0], [row_nr, 1], [row_nr, 2], [row_nr, 3], [row_nr, 4]]])
                continue
            if (item := row[0]) == row[1] == row[2] == row[3]:
                win_pattern.append([item, 1, [[row_nr, 0], [row_nr, 1], [row_nr, 2], [row_nr, 3]]])
                continue
            if (item := row[0]) == row[1] == row[2]:
                win_pattern.append([item, 0, [[row_nr, 0], [row_nr, 1], [row_nr, 2]]])
                continue
        if (item := slot_matrix[0][0]) == slot_matrix[1][1] == slot_matrix[2][2]:
            if item == slot_matrix[1][3] == slot_matrix[0][4]:
                win_pattern.append([item, 2, [[0, 0], [1, 1], [2, 2], [1, 3], [0, 4]]])
            else:
                win_pattern.append([item, 0, [[0, 0], [1, 1], [2, 2]]])
        if (item := slot_matrix[2][0]) == slot_matrix[1][1] == slot_matrix[0][2]:
            if item == slot_matrix[1][3] == slot_matrix[2][4]:
                win_pattern.append([item, 2, [[2, 0], [1, 1], [0, 2], [1, 3], [2, 4]]])
            else:
                win_pattern.append([item, 0, [[2, 0], [1, 1], [0, 2]]])
        stars = []
        for row_nr, row in enumerate(slot_matrix):
            for index, symbol in enumerate(row):
                if symbol == self.symbols[6]:
                    stars.append([row_nr, index])
        if len(stars) > 2:
            win_pattern.append([self.symbols[6], len(stars) - 3, stars])

        return win_pattern, slot_matrix


try:
    SlotMachine().start()
except Exception as e:
    print(e)
    sys.exit()
