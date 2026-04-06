# main.py
import tkinter as tk
from tkinter import messagebox
import ctypes
from engine import GameState

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


# ---------- СЛОВАРЬ ----------
class ScrabbleDictionary:
    def __init__(self):
        self.path = "words.txt"
        try:
            with open(self.path, encoding="utf-8") as f:
                self.words = {w.strip().upper() for w in f if w.strip()}
        except FileNotFoundError:
            self.words = set()

    def is_word(self, word):
        return word.upper() in self.words


# ---------- APP ----------
class ScrabbleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scrabble")
        self.root.geometry("560x780")

        self.selected_tile = None      # (index, ch)
        self.turn_letters = []         # [(r,c,index,ch)]

        self.swap_mode = False
        self.swap_selected = []
        self.swap_cooldown = 0

        self.build_menu()

    # ---------- MENU ----------
    def build_menu(self):
        self.menu = tk.Frame(self.root, padx=20, pady=20)
        self.menu.pack(expand=True)

        tk.Label(self.menu, text="SCRABBLE", font=("Arial", 22, "bold")).pack(pady=10)

        self.mode = tk.StringVar(value="pvp")
        tk.Radiobutton(self.menu, text="PvP", variable=self.mode,
                       value="pvp", command=self.update_menu).pack(anchor="w")
        tk.Radiobutton(self.menu, text="Против AI", variable=self.mode,
                       value="ai", command=self.update_menu).pack(anchor="w")

        self.e1 = tk.Entry(self.menu)
        self.e1.insert(0, "Игрок 1")
        self.e1.pack(pady=4)

        self.e2 = tk.Entry(self.menu)
        self.e2.insert(0, "Игрок 2")
        self.e2.pack(pady=4)

        self.update_menu()

        tk.Button(self.menu, text="ИГРАТЬ",
                  width=15, command=self.start_game).pack(pady=15)

    def update_menu(self):
        if self.mode.get() == "ai":
            self.e2.pack_forget()
        else:
            if not self.e2.winfo_ismapped():
                self.e2.pack(pady=4)

    # ---------- START ----------
    def start_game(self):
        self.player1 = self.e1.get()
        if self.mode.get() == "ai":
            self.player2 = "Степан"
            self.is_ai = True
        else:
            self.player2 = self.e2.get()
            self.is_ai = False

        self.menu.destroy()

        self.dictionary = ScrabbleDictionary()
        self.state = GameState([self.player1, self.player2], self.dictionary)
        self.current = self.state.current

        self.build_ui()
        self.refresh()

    # ---------- UI ----------
    def build_ui(self):
        self.board = tk.Canvas(self.root, width=450, height=450)
        self.board.pack(pady=6)
        self.board.bind("<Button-1>", self.on_board_click)

        self.rack = tk.Canvas(self.root, width=450, height=90)
        self.rack.pack(pady=6)
        self.rack.bind("<Button-1>", self.on_rack_click)

        self.info = tk.Label(self.root, font=("Arial", 11, "bold"))
        self.info.pack(pady=4)

        btns = tk.Frame(self.root)
        btns.pack(pady=6)

        tk.Button(btns, text="✓ Ход", width=12,
                  command=self.confirm_turn).pack(side="left", padx=5)
        tk.Button(btns, text="↩ Отмена", width=12,
                  command=self.cancel_turn).pack(side="left", padx=5)
        tk.Button(btns, text="🔁 Замена", width=12,
                  command=self.toggle_swap).pack(side="left", padx=5)

    # ---------- DRAW ----------
    def refresh(self):
        self.board.delete("all")

        for r in range(15):
            for c in range(15):
                if (r, c) in self.state.board:
                    fill = "#c8f7c5"
                elif (r, c) in self.state.bonus_spots:
                    kind, mult = self.state.bonus_spots[(r, c)]
                    fill = "#ffeaa7" if kind == "WORD" else "#dff9fb"
                else:
                    fill = "#ecf0f1"

                self.board.create_rectangle(
                    c*30, r*30, c*30+30, r*30+30,
                    fill=fill, outline="#aaa"
                )

                if (r, c) in self.state.bonus_spots and (r, c) not in self.state.board:
                    _, mult = self.state.bonus_spots[(r, c)]
                    self.board.create_text(c*30+15, r*30+15,
                                           text=f"x{mult}", font=("Arial", 8))

        for (r, c), ch in self.state.board.items():
            self.board.create_text(c*30+15, r*30+15,
                                   text=ch, font=("Arial", 14, "bold"))

        for r, c, _, ch in self.turn_letters:
            self.board.create_text(c*30+15, r*30+15,
                                   text=ch, font=("Arial", 14, "bold"),
                                   fill="#2980b9")

        self.rack.delete("all")
        used = {idx for _, _, idx, _ in self.turn_letters}

        for i, ch in enumerate(self.state.racks[self.current]):
            if i in used:
                continue
            x = i*60 + 45
            if self.selected_tile and self.selected_tile[0] == i:
                fill = "#74b9ff"
            elif i in self.swap_selected:
                fill = "#e67e22"
            else:
                fill = "#f1c40f"

            self.rack.create_rectangle(x-22, 18, x+22, 62,
                                       fill=fill, outline="#555")
            self.rack.create_text(x, 40, text=ch,
                                  font=("Arial", 14, "bold"))

        self.info.config(
            text=f"{self.player1}: {self.state.scores[self.player1]} | "
                 f"{self.player2}: {self.state.scores[self.player2]} | "
                 f"Ход: {self.current}"
        )

    # ---------- INPUT ----------
    def on_rack_click(self, e):
        idx = e.x // 60
        rack = self.state.racks[self.current]

        if not (0 <= idx < len(rack)):
            return

        if self.swap_mode:
            if idx in self.swap_selected:
                self.swap_selected.remove(idx)
            elif len(self.swap_selected) < 3:
                self.swap_selected.append(idx)
        else:
            self.selected_tile = (idx, rack[idx])

        self.refresh()

    def on_board_click(self, e):
        if not self.selected_tile or self.swap_mode:
            return

        r, c = e.y // 30, e.x // 30
        if (r, c) in self.state.board:
            return

        idx, ch = self.selected_tile
        self.turn_letters.append((r, c, idx, ch))
        self.selected_tile = None
        self.refresh()

    # ---------- TURN ----------
    def cancel_turn(self):
        self.turn_letters.clear()
        self.selected_tile = None
        self.swap_selected.clear()
        self.swap_mode = False
        self.refresh()

    def confirm_turn(self):
        if not self.turn_letters:
            return

        letters = [(r, c, ch) for r, c, _, ch in self.turn_letters]
        ok, msg = self.state.can_place(self.current, letters)

        if not ok:
            messagebox.showerror("Ошибка", msg)
            self.cancel_turn()
            return

        self.state.apply_move(self.current, letters)
        self.turn_letters.clear()
        self.end_turn()

    # ---------- SWAP ----------
    def toggle_swap(self):
        if self.swap_cooldown > 0:
            messagebox.showinfo("Замена", "Замена доступна раз в 3 хода")
            return

        if not self.swap_mode:
            self.swap_mode = True
            self.swap_selected.clear()
        else:
            if len(self.swap_selected) != 3:
                messagebox.showinfo("Замена", "Выберите ровно 3 буквы")
                return

            letters = [self.state.racks[self.current][i]
                       for i in self.swap_selected]
            self.state.swap_letters(self.current, letters)
            self.swap_selected.clear()
            self.swap_mode = False
            self.swap_cooldown = 1
            self.end_turn()
            return

        self.refresh()

    # ---------- END TURN ----------
    def end_turn(self):
        self.current = self.state.current

        if self.swap_cooldown > 0:
            self.swap_cooldown += 1
            if self.swap_cooldown >= 3:
                self.swap_cooldown = 0

        self.selected_tile = None
        self.swap_selected.clear()
        self.swap_mode = False
        self.refresh()

        if self.is_ai and self.current == self.player2:
            self.root.after(600, self.make_ai_move)
        elif not self.is_ai:
            messagebox.showinfo("Ход", f"Ход игрока: {self.current}")

    # ---------- AI ----------
    def make_ai_move(self):
        rack = self.state.racks[self.player2][:]

        for word in self.dictionary.words:
            if all(rack.count(c) >= word.count(c) for c in set(word)):
                letters = [(7+i, 7, ch) for i, ch in enumerate(word)]
                ok, _ = self.state.can_place(self.player2, letters)
                if ok:
                    self.state.apply_move(self.player2, letters)
                    self.end_turn()
                    return

        self.current = self.player1
        self.refresh()


# ---------- RUN ----------
if __name__ == "__main__":
    root = tk.Tk()
    ScrabbleApp(root)
    root.mainloop()
