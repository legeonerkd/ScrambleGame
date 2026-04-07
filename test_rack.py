
import tkinter as tk
from ui_styles import create_3d_tile, Colors

root = tk.Tk()
rack = tk.Canvas(root, width=510, height=110, bg=Colors.BG_CARD)
rack.pack()

# Рисуем 7 плиток
letters = ["К", "О", "Т", "И", "Н", "О", "С"]
for i, ch in enumerate(letters):
    x = (58 // 2) + i * 70 + 20
    y = 110 // 2
    print(f"Tile {i}: x={x}, y={y}, letter={ch}")
    create_3d_tile(rack, x, y, 58, 70, Colors.LETTER_TILE, Colors.LETTER_TILE_SHADOW, ch, Colors.LETTER_TEXT)

print("All tiles drawn")
root.mainloop()
