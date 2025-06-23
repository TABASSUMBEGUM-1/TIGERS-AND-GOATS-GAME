from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

root = Tk()
root.title("Bagh-Chal (Tigers and Goats)")

canvas = Canvas(root, width=600, height=600, bg="light yellow")
canvas.pack()

bg = Image.open("background.jpg")
bg = bg.resize((600, 600))
bg_img = ImageTk.PhotoImage(bg)
canvas.bg_img = bg_img # prevent garbage collection
canvas.create_image(0, 0, anchor=NW, image=bg_img)


status_label = Label(root, text="", font=("Arial", 14),bg="burlywood1")
status_label.pack(pady=10)

tiger_img_raw = Image.open("tiger.png")
tiger_img_raw = tiger_img_raw.resize((50, 50))  # Adjust size if needed
tiger_img = ImageTk.PhotoImage(tiger_img_raw)

goat_img_raw = Image.open("goat.png")
goat_img_raw = goat_img_raw.resize((50, 50))  # Adjust size if needed
goat_img = ImageTk.PhotoImage(goat_img_raw)

canvas.tiger_img = tiger_img
canvas.goat_img = goat_img

GRID_SIZE = 5
SPACING = 100
RADIUS = 10

points = {}
for row in range(GRID_SIZE):
    for col in range(GRID_SIZE):
        x = SPACING + col * SPACING
        y = SPACING + row * SPACING
        canvas.create_oval(x - 7, y - 7, x + 7, y + 7, fill="black")
        points[(row, col)] = (x, y)

def get_neighbors(r, c):
    neighbors = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            neighbors.append((nr, nc))
    special = [(0,0),(0,2),(0,4),(2,0),(2,2),(2,4),(4,0),(4,2),(4,4),(1,1),(1,3),(3,1),(3,3)]
    if (r, c) in special:
        for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                neighbors.append((nr, nc))
    return neighbors

for (r, c), (x1, y1) in points.items():
    for (nr, nc) in get_neighbors(r, c):
        x2, y2 = points[(nr, nc)]
        canvas.create_line(x1, y1, x2, y2, width=2)

tiger_positions = [(0, 0), (0, 2), (0, 4)]
goat_positions = []
goats_left = 15
captured_goats = 0
current_turn = "goats"
selected_goat = None
selected_tiger = None

tiger_items = {}
goat_items = {}

for pos in tiger_positions:
    x, y = points[pos]
    tiger_items[pos] = canvas.create_image(x, y, image=tiger_img)

def update_status():
    status_label.config(
        text=f"Turn: {'🐯 Tiger' if current_turn == 'tiger' else '🐐 Goat'}     "
             f"Goats Left: {goats_left}     Captured: {captured_goats}"
    )

def is_valid_jump(sr, sc, er, ec):
    if (er, ec) in points and abs(er - sr) <= 2 and abs(ec - sc) <= 2:
        mid = ((sr + er) // 2, (sc + ec) // 2)
        if (mid in goat_positions and
            (er, ec) not in tiger_positions and
            (er, ec) not in goat_positions and
            (mid in get_neighbors(sr, sc)) and
            (er, ec) in get_neighbors(mid[0], mid[1])):
            return True, mid
    return False, None

def check_goat_win():
    for sr, sc in tiger_positions:
        for (r, c) in get_neighbors(sr, sc):
            if (r, c) not in tiger_positions and (r, c) not in goat_positions:
                return False
        for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)]:
            er, ec = sr + dr, sc + dc
            valid, _ = is_valid_jump(sr, sc, er, ec)
            if valid:
                return False
    return True

def on_click(event):
    global goats_left, current_turn, selected_goat, selected_tiger, captured_goats

    for (r, c), (x, y) in points.items():
        if abs(event.x - x) <= 15 and abs(event.y - y) <= 15:

            if current_turn == "goats":
                if goats_left > 0:
                    if (r, c) not in goat_positions and (r, c) not in tiger_positions:
                        goat_positions.append((r, c))
                        goat_items[(r, c)] = canvas.create_image(x, y, image=goat_img)
                        goats_left -= 1
                        current_turn = "tiger"
                        update_status()
                        break
                elif selected_goat is None:
                    if (r, c) in goat_positions:
                        selected_goat = (r, c)
                        break
                else:
                    if goats_left == 0:
                        sr, sc = selected_goat
                        if (r, c) in get_neighbors(sr, sc) and (r, c) not in goat_positions and (r, c) not in tiger_positions:
                            goat_positions.remove((sr, sc))
                            goat_positions.append((r, c))
                            dx = points[(r, c)][0] - points[(sr, sc)][0]
                            dy = points[(r, c)][1] - points[(sr, sc)][1]
                            canvas.move(goat_items[(sr, sc)], dx, dy)
                            goat_items[(r, c)] = goat_items.pop((sr, sc))
                            selected_goat = None
                            current_turn = "tiger"
                            update_status()
                            break
                        else:
                            selected_goat = None
                            break

            elif current_turn == "tiger":
                if selected_tiger is None:
                    if (r, c) in tiger_positions:
                        selected_tiger = (r, c)
                        break
                else:
                    sr, sc = selected_tiger
                    if (r, c) in get_neighbors(sr, sc) and (r, c) not in goat_positions and (r, c) not in tiger_positions:
                        tiger_positions.remove((sr, sc))
                        tiger_positions.append((r, c))
                        dx = points[(r, c)][0] - points[(sr, sc)][0]
                        dy = points[(r, c)][1] - points[(sr, sc)][1]
                        canvas.move(tiger_items[(sr, sc)], dx, dy)
                        tiger_items[(r, c)] = tiger_items.pop((sr, sc))
                        selected_tiger = None
                        current_turn = "goats"
                        update_status()
                        break
                    else:
                        valid, mid = is_valid_jump(sr, sc, r, c)
                        if valid:
                            goat_positions.remove(mid)
                            canvas.delete(goat_items[mid])
                            del goat_items[mid]
                            tiger_positions.remove((sr, sc))
                            tiger_positions.append((r, c))
                            dx = points[(r, c)][0] - points[(sr, sc)][0]
                            dy = points[(r, c)][1] - points[(sr, sc)][1]
                            canvas.move(tiger_items[(sr, sc)], dx, dy)
                            tiger_items[(r, c)] = tiger_items.pop((sr, sc))
                            selected_tiger = None
                            captured_goats += 1
                            if captured_goats >= 5:
                                update_status()
                                messagebox.showinfo("Game Over", "🐯 TIGERS WIN!\nCaptured 5 goats.")
                                canvas.unbind("<Button-1>")
                            else:
                                current_turn = "goats"
                                update_status()
                            break
                        else:
                            selected_tiger = None
                            break

            if check_goat_win():
                update_status()
                messagebox.showinfo("Game Over", "🐐 GOATS WIN!\nTigers are blocked.")
                canvas.unbind("<Button-1>")
                break

canvas.bind("<Button-1>", on_click)
update_status()
root.mainloop()