import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import hashlib
import os
from textblob import TextBlob
import json
from datetime import datetime
import matplotlib.pyplot as plt

PASSWORD_FILE = "pass.txt"
JOURNAL_FILE = "journal.json"

# --- Authentication ---
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def set_password(new_password):
    with open(PASSWORD_FILE, "w") as f:
        f.write(hash_password(new_password))

def check_password(password_attempt):
    if not os.path.exists(PASSWORD_FILE):
        return None
    with open(PASSWORD_FILE, "r") as f:
        stored_hash = f.read().strip()
    return stored_hash == hash_password(password_attempt)

# --- Sentiment Analysis ---
def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

# --- Save Entry ---
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

# --- Show Mood Trend ---
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

    dates = [entry['date'] for entry in data]
    moods = [entry['mood'] for entry in data]

    plt.figure(figsize=(10, 4))
    plt.plot(dates, moods, marker='o', linestyle='-', color='royalblue')
    plt.title("Mood Trend Over Time")
    plt.xlabel("Date")
    plt.ylabel("Mood Score")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(True)
    plt.show()

# --- View Past Entries ---
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

    # Filter by tag if provided
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

    # Create a new window
    entries_win = tk.Toplevel(root)
    entries_win.title(f"Journal Entries - Tag: '{filter_tag or 'All'}'")
    entries_win.geometry("700x400")

    st = scrolledtext.ScrolledText(entries_win, wrap=tk.WORD, font=("Arial", 10))
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

# --- Filter Entries by Tag ---
def filter_entries_by_tag():
    tag_win = tk.Toplevel(root)
    tag_win.title("Filter by Tag")

    tk.Label(tag_win, text="Enter a tag to filter by (leave blank for all):").pack(padx=10, pady=10)
    tag_entry = tk.Entry(tag_win, width=30)
    tag_entry.pack(padx=10, pady=(0,10))

    def show_filtered():
        tag = tag_entry.get().strip().lower()
        tag_win.destroy()
        view_entries(filter_tag=tag)

    tk.Button(tag_win, text="Filter", command=show_filtered).pack(pady=(0,10))

# --- GUI Logic ---
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
    messagebox.showinfo("Mood Mirror", mood_msg)
    entry.delete("1.0", tk.END)
    tags_entry.delete(0, tk.END)

# --- Ask for Password ---
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

# --- Build GUI ---
root = tk.Tk()
root.title("Mood Mirror Journal")

if authenticate():
    tk.Label(root, text="How are you feeling today? Write it down.").pack(pady=10)
    entry = tk.Text(root, height=10, width=60)
    entry.pack()

    tk.Label(root, text="Add tags (comma separated):").pack(pady=(10,0))
    tags_entry = tk.Entry(root, width=60)
    tags_entry.pack()

    submit_btn = tk.Button(root, text="Reflect", command=submit_entry)
    submit_btn.pack(pady=5)

    mood_label = tk.Label(root, text="Latest Mood Score: --")
    mood_label.pack(pady=2)

    trend_btn = tk.Button(root, text="See Mood Trend", command=show_mood_trend)
    trend_btn.pack(pady=5)

    view_btn = tk.Button(root, text="View Entries", command=filter_entries_by_tag)
    view_btn.pack(pady=5)

    root.mainloop()