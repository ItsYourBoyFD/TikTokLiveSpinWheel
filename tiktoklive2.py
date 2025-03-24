import random
import tkinter as tk
from tkinter import messagebox, Canvas, scrolledtext
import math
import time
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, FollowEvent, LikeEvent, GiftEvent
import threading
import winsound

# Sound file paths (adjust these to your actual .wav files)
BUTTON_SOUND = "button_press.wav"
ERROR_SOUND = "error.wav"
SPIN_SOUND = "spin.wav"
WINNER_SOUND = "winner.wav"

# TikTok Live Client Setup
def start_tiktok_client():
    global client
    username = tiktok_username_entry.get().strip()
    if not username:
        play_sound(ERROR_SOUND)
        messagebox.showwarning("No Username", "Please enter a TikTok username!")
        return
    
    play_sound(BUTTON_SOUND)
    if client is not None:
        disconnect_tiktok_client()  # Disconnect existing client if any
    
    client = TikTokLiveClient(unique_id=f"@{username}")
    
    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        print(f"Connected to @{username}'s live stream!")
        status_label.config(text=f"Connected to @{username}")
        log_event(f"Connected to @{username}")

    @client.on(FollowEvent)
    async def on_follow(event: FollowEvent):
        global is_spinning
        if not is_spinning:
            viewer_name = event.user.unique_id
            if viewer_name not in names:
                names.append(viewer_name)
                name_listbox.insert(tk.END, viewer_name)
                draw_wheel()
                log_event(f"Added follower: {viewer_name}")

    @client.on(LikeEvent)
    async def on_like(event: LikeEvent):
        global is_spinning
        if not is_spinning:
            viewer_name = event.user.unique_id
            if viewer_name not in names:
                names.append(viewer_name)
                name_listbox.insert(tk.END, viewer_name)
                draw_wheel()
                log_event(f"Added liker: {viewer_name}")

    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent):
        global is_spinning, total_coins
        if not is_spinning:
            viewer_name = event.user.unique_id
            if viewer_name not in names:
                names.append(viewer_name)
                name_listbox.insert(tk.END, viewer_name)
                draw_wheel()
                log_event(f"Added gifter: {viewer_name}")
            
            gift_coins = event.gift.diamond_count
            total_coins += gift_coins
            update_winner_counter()
            log_event(f"Gift worth {gift_coins} coins, total now {total_coins}")

    client_thread = threading.Thread(target=lambda: client.run(), daemon=True)
    client_thread.start()
    connect_button.config(state="disabled")
    disconnect_button.config(state="normal")

def disconnect_tiktok_client():
    global client
    if client is not None:
        client.stop()
        client = None
        status_label.config(text="Not Connected")
        connect_button.config(state="normal")
        disconnect_button.config(state="disabled")
        log_event("Disconnected from TikTok Live")

def update_winner_counter():
    prize = total_coins // 4
    winner_canvas.delete("counter_text")
    winner_canvas.create_text(100, 50, text=f"Winner Gets: {prize} Coins", 
                             font=("Arial", 16, "bold"), fill="#FFD700", 
                             tags="counter_text")

def play_sound(sound_file):
    try:
        winsound.PlaySound(sound_file, winsound.SND_ASYNC)
    except Exception as e:
        log_event(f"Error playing sound {sound_file}: {e}")

def log_event(message):
    log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
    log_text.see(tk.END)  # Auto-scroll to the latest log

def add_name():
    global is_spinning
    play_sound(BUTTON_SOUND)
    if is_spinning:
        return
    name = name_entry.get().strip()
    if name:
        if name not in names:
            names.append(name)
            name_listbox.insert(tk.END, name)
            name_entry.delete(0, tk.END)
            draw_wheel()
            log_event(f"Manually added: {name}")
        else:
            play_sound(ERROR_SOUND)
            messagebox.showwarning("Duplicate Name", "This name is already in the list.")
    else:
        play_sound(ERROR_SOUND)
        messagebox.showwarning("Invalid Input", "Please enter a valid name.")

def start_timer():
    global timer_running
    if not timer_running:
        play_sound(BUTTON_SOUND)
        timer_running = True
        start_button.config(state="disabled")
        update_countdown()
        log_event("Timer started")

def update_countdown():
    global countdown_seconds, timer_running
    if timer_running and countdown_seconds > 0:
        countdown_seconds -= 1
        mins = countdown_seconds // 60
        secs = countdown_seconds % 60
        countdown_canvas.delete("timer_text")
        countdown_canvas.create_text(75, 50, text=f"Time Left: {mins:02d}:{secs:02d}", 
                                    font=("Arial", 16, "bold"), fill="#00FFFF", 
                                    tags="timer_text")
        root.after(1000, update_countdown)
    elif countdown_seconds <= 0:
        timer_running = False
        start_button.config(state="normal")
        countdown_canvas.delete("timer_text")
        countdown_canvas.create_text(75, 50, text="Time Left: 00:00", 
                                    font=("Arial", 16, "bold"), fill="#FF2D55", 
                                    tags="timer_text")
        log_event("Timer ended")

def add_one_minute():
    global countdown_seconds, timer_running
    if timer_running:
        play_sound(BUTTON_SOUND)
        countdown_seconds += 60
        mins = countdown_seconds // 60
        secs = countdown_seconds % 60
        countdown_canvas.delete("timer_text")
        countdown_canvas.create_text(75, 50, text=f"Time Left: {mins:02d}:{secs:02d}", 
                                    font=("Arial", 16, "bold"), fill="#00FFFF", 
                                    tags="timer_text")
        log_event("Added 1 minute to timer")

def start_spin(event):
    global spin_strength, increasing, is_spinning
    play_sound(BUTTON_SOUND)
    spin_strength = 0
    increasing = True
    is_spinning = True
    increase_strength()
    play_sound(SPIN_SOUND)
    log_event("Spin started")

def increase_strength():
    global spin_strength, increasing
    if increasing:
        spin_strength = min(spin_strength + 5, 100)
        strength_meter.coords(strength_bar, 10, 110 - spin_strength, 40, 110)
        strength_meter.itemconfig(strength_bar, fill="#FF2D55")
        root.after(50, increase_strength)

def stop_spin(event):
    global increasing
    increasing = False
    spin_wheel(spin_strength)

def spin_wheel(strength):
    global is_spinning, total_coins, countdown_seconds, timer_running
    if not names:
        play_sound(ERROR_SOUND)
        messagebox.showwarning("No Names", "No names in the list. Add names first!")
        is_spinning = False
        return
    
    final_angle = animate_spin(strength)
    segment_angle = 360 / len(names)
    prize = total_coins // 4
    
    arrow_angle = 90
    original_angle = (arrow_angle - final_angle) % 360
    winner_index = int(original_angle / segment_angle) % len(names)
    winner = names[winner_index]
    
    winners.append(winner)
    winners_listbox.insert(tk.END, winner)
    play_sound(WINNER_SOUND)
    messagebox.showinfo("Winner!", f"The winner is: {winner} and gets {prize} coins!")
    log_event(f"Winner: {winner} gets {prize} coins (Total coins: {total_coins})")
    
    # Reset after spin
    total_coins = 0
    update_winner_counter()
    countdown_seconds = 300
    timer_running = False
    start_button.config(state="normal")
    countdown_canvas.delete("timer_text")
    countdown_canvas.create_text(75, 50, text="Time Left: 05:00", 
                                font=("Arial", 16, "bold"), fill="#00FFFF", 
                                tags="timer_text")
    is_spinning = False
    log_event("Spin ended, reset prize and timer")

def clear_names():
    play_sound(BUTTON_SOUND)
    names.clear()
    name_listbox.delete(0, tk.END)
    draw_wheel()
    log_event("Names cleared")

def exit_app():
    play_sound(BUTTON_SOUND)
    disconnect_tiktok_client()
    root.destroy()
    log_event("Application exited")

def draw_wheel():
    canvas.delete("all")
    if not names:
        return
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    center_x, center_y = canvas_width // 2, canvas_height // 2
    radius = min(canvas_width, canvas_height) // 2 - 10
    
    angle_step = 360 / len(names)
    
    canvas.create_oval(10, 10, canvas_width-10, canvas_height-10, fill="#333333", outline="")
    
    for i, name in enumerate(names):
        start_angle = i * angle_step
        color = "#FF2D55" if i % 2 == 0 else "#00FFFF"
        canvas.create_arc(5, 5, canvas_width-5, canvas_height-5, start=start_angle, 
                         extent=angle_step, fill=color, outline="#FFFFFF", width=2)
        mid_angle = math.radians(start_angle + angle_step / 2)
        text_x = center_x + math.cos(mid_angle) * (radius - 40)
        text_y = center_y - math.sin(mid_angle) * (radius - 40)
        font_size = max(14, radius // 10)
        canvas.create_text(text_x, text_y, text=name, font=("Arial", font_size, "bold"), 
                          fill="#FFFFFF", anchor="center")
    
    arrow_width = radius // 10
    canvas.create_polygon(center_x-arrow_width, 0, center_x+arrow_width, 0, 
                         center_x, arrow_width*1.5, fill="#FF2D55", outline="#FFFFFF", width=2)
    canvas.create_line(center_x, arrow_width*1.5, center_x, arrow_width*3, 
                      fill="#FF2D55", width=4)
    canvas.create_rectangle(10, 10, 60, 30, fill="#FF2D55", outline="#FFFFFF")
    canvas.create_text(35, 20, text="LIVE", font=("Arial", 10, "bold"), fill="#FFFFFF")

def ease_out(t):
    return 1 - (1 - t) ** 2

def animate_spin(strength):
    total_duration = 28.0
    total_rotation = 720 + (strength * 10)
    
    target_fps = 60
    steps = int(total_duration * target_fps)
    angle_increment = total_rotation / steps
    base_delay = int(1000 / target_fps)
    
    current_angle = 0
    start_time = time.time()
    
    for i in range(steps):
        progress = i / (steps - 1)
        eased_progress = ease_out(progress)
        current_angle = total_rotation * eased_progress
        
        canvas.delete("all")
        draw_wheel_rotated(current_angle)
        root.update()
        
        elapsed = (time.time() - start_time) * 1000
        target_time = (i + 1) * base_delay
        sleep_time = max(1, int(target_time - elapsed))
        root.after(sleep_time)
    
    final_angle = current_angle % 360
    canvas.delete("all")
    draw_wheel_rotated(final_angle)
    add_winner_marker(final_angle)
    return final_angle

def draw_wheel_rotated(angle):
    if not names:
        return
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    center_x, center_y = canvas_width // 2, canvas_height // 2
    radius = min(canvas_width, canvas_height) // 2 - 10
    
    angle_step = 360 / len(names)
    
    canvas.create_oval(10, 10, canvas_width-10, canvas_height-10, fill="#333333", outline="")
    
    for i, name in enumerate(names):
        start_angle = (i * angle_step + angle) % 360
        color = "#FF2D55" if i % 2 == 0 else "#00FFFF"
        canvas.create_arc(5, 5, canvas_width-5, canvas_height-5, start=start_angle, 
                         extent=angle_step, fill=color, outline="#FFFFFF", width=2)
        mid_angle = math.radians(start_angle + angle_step / 2)
        text_x = center_x + math.cos(mid_angle) * (radius - 40)
        text_y = center_y - math.sin(mid_angle) * (radius - 40)
        font_size = max(14, radius // 10)
        canvas.create_text(text_x, text_y, text=name, font=("Arial", font_size, "bold"), 
                          fill="#FFFFFF", anchor="center")
    
    arrow_width = radius // 10
    canvas.create_polygon(center_x-arrow_width, 0, center_x+arrow_width, 0, 
                         center_x, arrow_width*1.5, fill="#FF2D55", outline="#FFFFFF", width=2)
    canvas.create_line(center_x, arrow_width*1.5, center_x, arrow_width*3, 
                      fill="#FF2D55", width=4)
    canvas.create_rectangle(10, 10, 60, 30, fill="#FF2D55", outline="#FFFFFF")
    canvas.create_text(35, 20, text="LIVE", font=("Arial", 10, "bold"), fill="#FFFFFF")

def add_winner_marker(final_angle):
    segment_angle = 360 / len(names)
    original_angle = (90 - final_angle) % 360
    winner_index = int(original_angle / segment_angle) % len(names)
    winner_start_angle = (winner_index * segment_angle) % 360
    
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    center_x, center_y = canvas_width // 2, canvas_height // 2
    radius = min(canvas_width, canvas_height) // 2 - 70
    
    angle_rad = math.radians(winner_start_angle)
    marker_x = center_x + math.cos(angle_rad) * radius
    marker_y = center_y - math.sin(angle_rad) * radius
    
    canvas.create_oval(marker_x-5, marker_y-5, marker_x+5, marker_y+5, fill="#00FF00", 
                      outline="#FFFFFF", width=2)

# GUI Setup
root = tk.Tk()
root.title("TikTok Live Roulette")
root.configure(bg="#1A1A1A")
root.geometry("800x700")  # Increased height for log window

names = []
winners = []
spin_strength = 0
increasing = False
client = None
total_coins = 0  # Track all coins given
is_spinning = False
countdown_seconds = 300
timer_running = False

root.bind("<Configure>", lambda e: draw_wheel())

# Main Frame
main_frame = tk.Frame(root, bg="#1A1A1A")
main_frame.pack(expand=True, fill="both")
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=0)  # Log row
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=3)
main_frame.grid_columnconfigure(2, weight=1)

# Left Side: Current Names
left_frame = tk.Frame(main_frame, bg="#1A1A1A")
left_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
tk.Label(left_frame, text="Current Names:", font=("Arial", 12, "bold"), fg="#FF2D55", 
         bg="#1A1A1A").pack()
name_listbox = tk.Listbox(left_frame, height=10, width=15, font=("Arial", 10), 
                         bg="#333333", fg="#FFFFFF", selectbackground="#FF2D55", relief="flat")
name_listbox.pack(fill="y", expand=True)

# Center: Input, TikTok Connect, Wheel, and Spin Button
center_frame = tk.Frame(main_frame, bg="#1A1A1A")
center_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
center_frame.grid_rowconfigure(2, weight=1)
center_frame.grid_columnconfigure(0, weight=1)

# TikTok Username Input
tiktok_frame = tk.Frame(center_frame, bg="#1A1A1A")
tiktok_frame.grid(row=0, column=0, sticky="ew", pady=5)
tk.Label(tiktok_frame, text="TikTok Username:", font=("Arial", 12, "bold"), fg="#FFFFFF", 
         bg="#1A1A1A").pack(side=tk.LEFT, padx=5)
tiktok_username_entry = tk.Entry(tiktok_frame, font=("Arial", 12), bg="#333333", fg="#FFFFFF", 
                                 insertbackground="#FF2D55", borderwidth=2, relief="flat")
tiktok_username_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True)
connect_button = tk.Button(tiktok_frame, text="Connect", command=start_tiktok_client, 
                           font=("Arial", 10, "bold"), bg="#FF2D55", fg="#FFFFFF", 
                           activebackground="#00FFFF", relief="flat")
connect_button.pack(side=tk.LEFT, padx=5)
disconnect_button = tk.Button(tiktok_frame, text="Disconnect", command=disconnect_tiktok_client, 
                              font=("Arial", 10, "bold"), bg="#FF5555", fg="#FFFFFF", 
                              activebackground="#FF2D55", relief="flat", state="disabled")
disconnect_button.pack(side=tk.LEFT, padx=5)

# Status Label
status_label = tk.Label(center_frame, text="Not Connected", font=("Arial", 10), fg="#FFFFFF", 
                        bg="#1A1A1A")
status_label.grid(row=1, column=0, pady=5)

# Manual Name Input
input_frame = tk.Frame(center_frame, bg="#1A1A1A")
input_frame.grid(row=3, column=0, sticky="ew", pady=5)
tk.Label(input_frame, text="Enter Name:", font=("Arial", 12, "bold"), fg="#FFFFFF", 
         bg="#1A1A1A").pack(side=tk.LEFT, padx=5)
name_entry = tk.Entry(input_frame, font=("Arial", 12), bg="#333333", fg="#FFFFFF", 
                     insertbackground="#FF2D55", borderwidth=2, relief="flat")
name_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True)

# Buttons
button_frame = tk.Frame(center_frame, bg="#1A1A1A")
button_frame.grid(row=4, column=0, sticky="ew", pady=5)
tk.Button(button_frame, text="Add Name", command=add_name, font=("Arial", 10, "bold"), 
          bg="#FF2D55", fg="#FFFFFF", activebackground="#00FFFF", relief="flat").pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Clear Names", command=clear_names, font=("Arial", 10, "bold"), 
          bg="#00FFFF", fg="#FFFFFF", activebackground="#FF2D55", relief="flat").pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Exit", command=exit_app, font=("Arial", 10, "bold"), 
          bg="#FFFFFF", fg="#1A1A1A", activebackground="#FF2D55", relief="flat").pack(side=tk.LEFT, padx=5)

# Wheel Canvas
canvas_frame = tk.Frame(center_frame, bg="#1A1A1A")
canvas_frame.grid(row=2, column=0, sticky="nsew")
canvas = Canvas(canvas_frame, width=400, height=400, bg="#1A1A1A", highlightthickness=0)
canvas.pack(expand=True, fill="both")
draw_wheel()

# Spin and Timer Buttons
spin_timer_frame = tk.Frame(center_frame, bg="#1A1A1A")
spin_timer_frame.grid(row=5, column=0, pady=10)
spin_button = tk.Button(spin_timer_frame, text="Hold to Spin", font=("Arial", 12, "bold"), 
                        bg="#FF2D55", fg="#FFFFFF", activebackground="#00FFFF", relief="flat")
spin_button.pack(side=tk.LEFT, padx=5)
spin_button.bind("<ButtonPress-1>", start_spin)
spin_button.bind("<ButtonRelease-1>", stop_spin)
start_button = tk.Button(spin_timer_frame, text="Start Timer", command=start_timer, 
                         font=("Arial", 10, "bold"), bg="#00FFFF", fg="#FFFFFF", 
                         activebackground="#FF2D55", relief="flat")
start_button.pack(side=tk.LEFT, padx=5)
add_min_button = tk.Button(spin_timer_frame, text="Add 1 Min", command=add_one_minute, 
                           font=("Arial", 10, "bold"), bg="#FFD700", fg="#1A1A1A", 
                           activebackground="#FF2D55", relief="flat")
add_min_button.pack(side=tk.LEFT, padx=5)

# Right Side: Strength Meter, Countdown, Winner Counter, and Winners
right_frame = tk.Frame(main_frame, bg="#1A1A1A")
right_frame.grid(row=0, column=2, sticky="ns", padx=10, pady=10)

# Strength Meter
strength_frame = tk.Frame(right_frame, bg="#1A1A1A")
strength_frame.pack(pady=(0, 10))
strength_meter = Canvas(strength_frame, width=50, height=120, bg="#333333", highlightthickness=0)
strength_meter.pack()
strength_meter.create_rectangle(8, 8, 42, 112, outline="#FFFFFF", width=2)
strength_bar = strength_meter.create_rectangle(10, 110, 40, 110, fill="#FF2D55")

# Countdown Timer
countdown_frame = tk.Frame(right_frame, bg="#1A1A1A")
countdown_frame.pack(pady=(0, 10))
countdown_canvas = Canvas(countdown_frame, width=150, height=100, bg="#1A1A1A", highlightthickness=0)
countdown_canvas.pack()
countdown_canvas.create_rectangle(10, 10, 140, 90, fill="#2F2F2F", outline="#00FFFF", width=3)
countdown_canvas.create_text(75, 50, text="Time Left: 05:00", 
                            font=("Arial", 16, "bold"), fill="#00FFFF", tags="timer_text")

# Winner Coin Counter with Luxury Graphics
winner_frame = tk.Frame(right_frame, bg="#1A1A1A")
winner_frame.pack(pady=(0, 10))
winner_canvas = Canvas(winner_frame, width=200, height=100, bg="#1A1A1A", highlightthickness=0)
winner_canvas.pack()
winner_canvas.create_rectangle(10, 10, 190, 90, fill="#2F2F2F", outline="#FFD700", width=3)
winner_canvas.create_text(100, 50, text=f"Winner Gets: {total_coins // 4} Coins", 
                         font=("Arial", 16, "bold"), fill="#FFD700", tags="counter_text")

# Previous Winners
tk.Label(right_frame, text="Previous Winners:", font=("Arial", 12, "bold"), fg="#00FFFF", 
         bg="#1A1A1A").pack()
winners_listbox = tk.Listbox(right_frame, height=10, width=15, font=("Arial", 10), 
                            bg="#333333", fg="#FFFFFF", selectbackground="#00FFFF", relief="flat")
winners_listbox.pack(fill="y", expand=True)

# Log Window
log_frame = tk.Frame(main_frame, bg="#1A1A1A")
log_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
tk.Label(log_frame, text="Event Log:", font=("Arial", 12, "bold"), fg="#FFFFFF", 
         bg="#1A1A1A").pack()
log_text = scrolledtext.ScrolledText(log_frame, height=5, width=80, font=("Arial", 10), 
                                    bg="#333333", fg="#FFFFFF", relief="flat")
log_text.pack(fill="x", expand=True)

root.mainloop()
