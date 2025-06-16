import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import hashlib
import os
from textblob import TextBlob
import json
from datetime import datetime
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

PASSWORD_FILE = "pass.txt"
JOURNAL_FILE = "journal.json"


# create hash from string
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# write hashed password to file
def set_password(new_password):
    with open(PASSWORD_FILE, "w") as f:
        f.write(hash_password(new_password))


# check string with hashed password
def check_password(password_attempt):
    if not os.path.exists(PASSWORD_FILE):
        return None
    with open(PASSWORD_FILE, "r") as f:
        stored_hash = f.read().strip()
    return stored_hash == hash_password(password_attempt)


# analyze the entered text with TextBlob
def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity


# write entry to file
def save_entry(text, mood, tags):
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    entry = {"date": date_str, "text": text.strip(), "mood": mood, "tags": tag_list}
    data = []

    if os.path.exists(JOURNAL_FILE):
        with open(JOURNAL_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    data.append(entry)
    with open(JOURNAL_FILE, "w") as f:
        json.dump(data, f, indent=2)


def show_mood_trend():
    if not os.path.exists(JOURNAL_FILE):
        messagebox.showinfo("No Data", "No journal entries found.")
        return

    with open(JOURNAL_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Could not read journal data.")
            return

    if not data:
        messagebox.showinfo("No Data", "No mood data to display.")
        return

    # extract dates and moods, convert date strings to datetime objects for better x-axis formatting
    from datetime import datetime as dt
    dates = [dt.strptime(entry['date'], "%Y-%m-%d %H:%M") for entry in data]
    moods = [entry['mood'] for entry in data]

    # create a new toplevel window
    trend_win = tk.Toplevel(root)
    trend_win.title("Mood Trend Over Time")
    trend_win.geometry("800x500")

    # create matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    ax.plot(dates, moods, marker='o', linestyle='-', color='royalblue')
    ax.set_title("Mood Trend Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Mood Score")
    fig.autofmt_xdate(rotation=45)
    ax.grid(True)
    fig.tight_layout()

    # embed plot in tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master=trend_win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


# show entry list
def view_entries(filter_tag=None):
    if not os.path.exists(JOURNAL_FILE):
        messagebox.showinfo("No Data", "No journal entries found.")
        return

    with open(JOURNAL_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Could not read journal data.")
            return

    if not data:
        messagebox.showinfo("No Data", "No entries to display.")
        return

    if filter_tag:
        filtered = []
        for entry in data:
            tags = [t.lower() for t in entry.get("tags",[])]
            if filter_tag in tags:
                filtered.append(entry)
        data = filtered

    if not data:
        messagebox.showinfo("No Entries", f"No entries found with tag '{filter_tag}'.")
        return

    entries_win = tk.Toplevel(root)
    entries_win.title(f"Journal Entries - Tag: '{filter_tag or 'All'}'")
    entries_win.geometry("700x400")

    st = scrolledtext.ScrolledText(entries_win, wrap=tk.WORD, font=("Georgia", 12))
    st.pack(expand=True, fill=tk.BOTH)

    for entry in reversed(data):
        date = entry.get("date", "Unknown date")
        mood = entry.get("mood", 0)
        tags = entry.get("tags", [])
        text = entry.get("text", "")
        snippet = (text[:150] + "...") if len(text) > 150 else text

        st.insert(tk.END, f"Date: {date}\n")
        st.insert(tk.END, f"Mood Score: {mood:.2f}\n")
        st.insert(tk.END, f"Tags: {', '.join(tags) if tags else 'None'}\n")
        st.insert(tk.END, f"Entry Preview:\n{snippet}\n")
        st.insert(tk.END, "-"*60 + "\n\n")

    st.config(state=tk.DISABLED)


# filter entries by entered tag
def filter_entries_by_tag():
    tag_win = tk.Toplevel(root)
    tag_win.title("Filter by Tag")

    tk.Label(tag_win, text="Enter a tag to filter by (leave blank for all):", font=("Georgia", 12)).pack(padx=10, pady=10)
    tag_entry = tk.Entry(tag_win, width=30, font=("Georgia", 12))
    tag_entry.pack(padx=10, pady=(0,10))

    def show_filtered():
        tag = tag_entry.get().strip().lower()
        tag_win.destroy()
        view_entries(filter_tag=tag)

    tk.Button(tag_win, text="Filter", font=("Georgia", 12), command=show_filtered).pack(pady=(0,10))


def submit_entry():
    text = entry.get("1.0", tk.END)
    tags = tags_entry.get()
    if not text.strip():
        messagebox.showwarning("Empty Entry", "Please write something.")
        return
    mood = analyze_sentiment(text)
    save_entry(text, mood, tags)

    mood_msg = f"Mood Score: {mood:.2f}\n"
    if mood < -0.3:
        mood_msg += "There's pain that uses you and there's pain that you use."
    elif mood < 0:
        mood_msg += "Not every door that is closed is locked... push! 🌱"
    elif mood < 0.3:
        mood_msg += "I've never met a strong person with an easy past. You're on the right path! 💡"
    elif mood < 0.5:
        mood_msg += "In a society that profits from your self-doubt, liking yourself is a rebellious act :D"
    else:
        mood_msg += "You sound great! Keep riding that wave. 🌈"

    mood_label.config(text=f"Latest Mood Score: {mood:.2f}")
    quote_label.config(text=mood_msg)
    entry.delete("1.0", tk.END)
    tags_entry.delete(0, tk.END)


# handle password logic
def authenticate():
    if not os.path.exists(PASSWORD_FILE):
        pw = simpledialog.askstring("Set Password", "Create your Mood Mirror password:", show='*')
        if pw:
            set_password(pw)
            messagebox.showinfo("Password Set", "Password created! Now please log in.")
            return authenticate()
        else:
            root.destroy()
            return False

    attempts = 3
    while attempts > 0:
        pw = simpledialog.askstring("Login", "Enter your password:", show='*')
        if pw and check_password(pw):
            return True
        else:
            attempts -= 1
            messagebox.showerror("Error", f"Incorrect password. {attempts} attempts left.")
    root.destroy()
    return False


root = tk.Tk()
root.title("Mood Mirror Journal")

# full screen background setup
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{screen_width}x{screen_height}")
root.state('zoomed')

bg_image = Image.open("aurora_background.jpg")
bg_image = bg_image.resize((screen_width, screen_height), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

main_frame = tk.Frame(root, bg="#00004B", bd=0)
main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

if authenticate():
    tk.Label(main_frame, text="How are you feeling today? Write it down.", font=("Georgia", 18), fg="white", bg="#00004B").pack(pady=10)
    entry = tk.Text(main_frame, height=10, width=60, font=("Georgia", 16))
    entry.pack()

    tk.Label(main_frame, text="Add tags (comma separated):", font=("Georgia", 15), fg="white", bg="#00004B").pack(pady=(10,0))
    tags_entry = tk.Entry(main_frame, width=60, font=("Georgia", 14))
    tags_entry.pack()

    submit_btn = tk.Button(main_frame, text="Add Entry", font=("Georgia", 15), command=submit_entry)
    submit_btn.pack(pady=5)

    mood_label = tk.Label(main_frame, text="Latest Mood Score: --", font=("Georgia", 14), fg="white", bg="#00004B")
    mood_label.pack(pady=2)

    quote_label = tk.Label(main_frame, text="", font=("Georgia", 13, "italic"), fg="#FFD700", bg="#00004B", wraplength=500, justify="center")
    quote_label.pack(pady=(10, 15))

    trend_btn = tk.Button(main_frame, text="See Mood Trend", font=("Georgia", 15), command=show_mood_trend)
    trend_btn.pack(pady=5)

    view_btn = tk.Button(main_frame, text="View Entries", font=("Georgia", 15), command=filter_entries_by_tag)
    view_btn.pack(pady=5)

    root.mainloop()