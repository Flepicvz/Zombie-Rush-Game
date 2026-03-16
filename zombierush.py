import tkinter as tk
import math
import time
import random


WINDOW_W, WINDOW_H = 600, 600
PLAYER_SIZE = 20
ZOMBIE_SIZE = 40
BULLET_SPEED = 10
ZOMBIE_SPEED = 2


highscore = 0
game_running = False
bullets = []
zombies = []
wave = 0
player_alive = True


mods = {
    "Aimbot": False,
    "Godmode": False,
    "RapidFire": False,
    "MultiShot": False
}


root = tk.Tk()
root.title("Zombie Rush Deluxe")
root.geometry(f"{WINDOW_W}x{WINDOW_H}")

canvas = tk.Canvas(root, width=WINDOW_W, height=WINDOW_H, bg="green")
canvas.pack()


def show_main_menu():
    canvas.delete("all")
    global main_menu_frame
    main_menu_frame = tk.Frame(root)
    main_menu_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(main_menu_frame, text=f"Highscore: {highscore}", font=("Arial", 16)).pack(pady=10)
    tk.Button(main_menu_frame, text="Play", width=15, command=start_game).pack(pady=5)
    tk.Button(main_menu_frame, text="Exit", width=15, command=root.quit).pack(pady=5)
    tk.Label(main_menu_frame, text="Zombie Rush Deluxe", font=("Arial", 12)).pack(pady=10)


def open_mod_menu(event=None):
    mod = tk.Toplevel(root)
    mod.title("Mod Menu")
    mod.geometry("250x200")

    tk.Label(mod, text="Mods").pack(pady=5)
    for mod_name in mods:
        var = tk.BooleanVar(value=mods[mod_name])
        chk = tk.Checkbutton(mod, text=mod_name, variable=var,
                             command=lambda m=mod_name, v=var: toggle_mod(m, v))
        chk.pack(anchor="w")

    tk.Button(mod, text="Close", command=mod.destroy).pack(pady=10)

def toggle_mod(mod_name, var):
    mods[mod_name] = var.get()
    print(f"{mod_name} set to {mods[mod_name]}")

root.bind("<m>", open_mod_menu)


player = None
touch_start = None

def spawn_player():
    global player
    x1, y1 = (WINDOW_W//2 - PLAYER_SIZE, WINDOW_H//2 - PLAYER_SIZE)
    x2, y2 = (WINDOW_W//2 + PLAYER_SIZE, WINDOW_H//2 + PLAYER_SIZE)
    player = canvas.create_oval(x1, y1, x2, y2, fill="blue")

def spawn_zombies(count):
    for _ in range(count):
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x, y = random.randint(0, WINDOW_W-ZOMBIE_SIZE), 0
        elif side == "bottom":
            x, y = random.randint(0, WINDOW_W-ZOMBIE_SIZE), WINDOW_H-ZOMBIE_SIZE
        elif side == "left":
            x, y = 0, random.randint(0, WINDOW_H-ZOMBIE_SIZE)
        else:
            x, y = WINDOW_W-ZOMBIE_SIZE, random.randint(0, WINDOW_H-ZOMBIE_SIZE)
        zombie = canvas.create_oval(x, y, x+ZOMBIE_SIZE, y+ZOMBIE_SIZE, fill="red")
        zombies.append(zombie)

mouse_x, mouse_y = 0, 0
def mouse_motion(event):
    global mouse_x, mouse_y
    mouse_x, mouse_y = event.x, event.y
canvas.bind("<Motion>", mouse_motion)

def shoot(event):
    if not player:
        return
    px1, py1, px2, py2 = canvas.coords(player)
    start_x = (px1 + px2)/2
    start_y = (py1 + py2)/2

    targets = []
    if mods["Aimbot"] and zombies:
        
        min_dist = float("inf")
        nearest = None
        for z in zombies:
            zx1, zy1, zx2, zy2 = canvas.coords(z)
            zx = (zx1+zx2)/2
            zy = (zy1+zy2)/2
            d = math.hypot(zx-start_x, zy-start_y)
            if d < min_dist:
                min_dist = d
                nearest = (zx, zy)
        if nearest:
            dx = nearest[0]-start_x
            dy = nearest[1]-start_y
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length
    else:
        dx = mouse_x-start_x
        dy = mouse_y-start_y
        length = math.hypot(dx, dy)
        if length != 0:
            dx /= length
            dy /= length
        else:
            dx = dy = 0

    shots = 3 if mods["MultiShot"] else 1
    for _ in range(shots):
        bullet = {"id": canvas.create_oval(start_x-5, start_y-5, start_x+5, start_y+5, fill="yellow"),
                  "dx": dx*BULLET_SPEED, "dy": dy*BULLET_SPEED}
        bullets.append(bullet)

root.bind("<f>", shoot)

def update_bullets():
    global bullets, zombies
    for b in bullets[:]:
        canvas.move(b["id"], b["dx"], b["dy"])
        x1, y1, x2, y2 = canvas.coords(b["id"])
        for z in zombies[:]:
            if canvas.coords(z):
                zx1, zy1, zx2, zy2 = canvas.coords(z)
                if not (x2 < zx1 or x1 > zx2 or y2 < zy1 or y1 > zy2):
                    canvas.delete(z)
                    zombies.remove(z)
                    canvas.delete(b["id"])
                    bullets.remove(b)
                    break
        if x2<0 or x1>WINDOW_W or y2<0 or y1>WINDOW_H:
            canvas.delete(b["id"])
            bullets.remove(b)
    if game_running:
        root.after(16, update_bullets)

def move_zombies():
    global touch_start, player_alive, game_running
    if not game_running:
        return
    if player_alive and player:
        px1, py1, px2, py2 = canvas.coords(player)
        for z in zombies[:]:
            if canvas.coords(z):
                zx1, zy1, zx2, zy2 = canvas.coords(z)
                zx = (zx1+zx2)/2
                zy = (zy1+zy2)/2

                dx = dy = 0
                if zx<px1: dx=ZOMBIE_SPEED
                if zx>px2: dx=-ZOMBIE_SPEED
                if zy<py1: dy=ZOMBIE_SPEED
                if zy>py2: dy=-ZOMBIE_SPEED

                canvas.move(z, dx, dy)

               
                if not (zx2<px1 or zx1>px2 or zy2<py1 or zy1>py2):
                    if not mods["Godmode"]:
                        if touch_start is None:
                            touch_start = time.time()
                        elif time.time()-touch_start>=3:
                            game_over()
                            return
                    else:
                        touch_start = None
                else:
                    touch_start = None
    if game_running:
        root.after(50, move_zombies)

def game_over():
    global game_running, player_alive
    game_running = False
    player_alive = False
    canvas.delete("all")
    canvas.create_text(WINDOW_W/2, WINDOW_H/2, text="GAME OVER", font=("Arial", 30), fill="red")
    print("Game Over!")

def start_game():
    global bullets, zombies, wave, player_alive, game_running
    bullets = []
    zombies = []
    wave = 1
    game_running = True
    player_alive = True
    if 'main_menu_frame' in globals():
        main_menu_frame.destroy()
    canvas.delete("all")
    spawn_player()
    spawn_zombies(wave)
    update_bullets()
    move_zombies()
    next_wave()

def next_wave():
    global wave
    if not game_running:
        return
    wave += 1
    spawn_zombies(wave)
    root.after(10000, next_wave)  # new wave every 10 seconds


show_main_menu()
root.mainloop()
