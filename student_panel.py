import tkinter as tk
from tkinter import messagebox
import sqlite3
import sys

# -- Get student email from command-line argument --
if len(sys.argv) < 2:
    print("Error: No student email provided.")
    sys.exit(1)

student_email = sys.argv[1]

# -- Connect to DB --
conn = sqlite3.connect("hostel.db")
cur = conn.cursor()

# -- GUI Setup --
root = tk.Tk()
root.title("Student Panel")
root.geometry("600x400")
root.configure(bg="#2e3f4f")

tk.Label(root, text="🎓 Student Dashboard", font=("Arial", 20, "bold"), fg="white", bg="#2e3f4f").pack(pady=10)
tk.Label(root, text=f"Logged in as: {student_email}", font=("Arial", 12), fg="white", bg="#2e3f4f").pack(pady=5)

# === Features ===

def view_room():
    # Get student's floor and seater
    cur.execute("SELECT floor, seater FROM users WHERE email=?", (student_email,))
    result = cur.fetchone()
    if not result:
        messagebox.showerror("Error", "Student info not found.")
        return
    floor, seater = result
    if seater == "Single":
        messagebox.showinfo("Room Info", "You are in a single seater room.")
        return

    win = tk.Toplevel(root)
    win.title("Roommates")
    win.geometry("400x300")
    win.configure(bg="#34495e")
    tk.Label(win, text=f"{seater} Seater Roommates (Floor {floor})", font=("Arial", 14, "bold"), bg="#34495e", fg="white").pack(pady=10)
    cur.execute("SELECT name, phone FROM users WHERE floor=? AND seater=? AND email!=?", (floor, seater, student_email))
    roommates = cur.fetchall()
    if not roommates:
        tk.Label(win, text="No roommates found.", bg="#34495e", fg="white").pack(pady=10)
    else:
        for idx, (name, phone) in enumerate(roommates):
            tk.Label(win, text=f"{idx+1}. {name} | {phone}", bg="#34495e", fg="white").pack(anchor="w", padx=10, pady=2)

def make_complaint():
    def submit():
        text = complaint.get().strip()
        if not text:
            messagebox.showerror("Error", "Complaint cannot be empty.")
            return
        cur.execute("INSERT INTO complaints (email, complaint) VALUES (?, ?)", (student_email, text))
        conn.commit()
        messagebox.showinfo("Done", "Complaint submitted.")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Make Complaint")
    win.geometry("300x150")
    win.configure(bg="#34495e")
    tk.Label(win, text="Enter complaint:", bg="#34495e", fg="white").pack(pady=10)
    complaint = tk.StringVar()
    tk.Entry(win, textvariable=complaint, width=35).pack()
    tk.Button(win, text="Submit", command=submit, bg="#e67e22", fg="white").pack(pady=10)

def request_leave():
    def submit():
        text = reason.get().strip()
        if not text:
            messagebox.showerror("Error", "Reason cannot be empty.")
            return
        cur.execute("INSERT INTO leaves (email, reason) VALUES (?, ?)", (student_email, text))
        conn.commit()
        messagebox.showinfo("Done", "Leave requested.")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Request Leave")
    win.geometry("300x150")
    win.configure(bg="#34495e")
    tk.Label(win, text="Leave Reason:", bg="#34495e", fg="white").pack(pady=10)
    reason = tk.StringVar()
    tk.Entry(win, textvariable=reason, width=35).pack()
    tk.Button(win, text="Submit", command=submit, bg="#2ecc71", fg="white").pack(pady=10)

def view_complaints():
    win = tk.Toplevel(root)
    win.title("Your Complaints")
    win.geometry("400x350")
    win.configure(bg="#34495e")
    tk.Label(win, text="Your Complaints", font=("Arial", 14, "bold"), bg="#34495e", fg="white").pack(pady=10)
    # If 'viewed' column doesn't exist, complaints will always show as unviewed
    try:
        cur.execute("ALTER TABLE complaints ADD COLUMN viewed INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    cur.execute("SELECT complaint, viewed FROM complaints WHERE email=?", (student_email,))
    complaints = cur.fetchall()
    if not complaints:
        tk.Label(win, text="No complaints submitted.", bg="#34495e", fg="white").pack(pady=10)
    for idx, (msg, viewed) in enumerate(complaints):
        status = "Viewed" if viewed else "Unviewed"
        tk.Label(win, text=f"{idx+1}. {msg} [{status}]", bg="#34495e", fg="white", anchor="w").pack(fill="x", padx=10, pady=2)

def view_leaves():
    win = tk.Toplevel(root)
    win.title("Your Leave Requests")
    win.geometry("400x350")
    win.configure(bg="#34495e")
    tk.Label(win, text="Your Leave Requests", font=("Arial", 14, "bold"), bg="#34495e", fg="white").pack(pady=10)
    cur.execute("SELECT reason, status FROM leaves WHERE email=?", (student_email,))
    leaves = cur.fetchall()
    if not leaves:
        tk.Label(win, text="No leave requests submitted.", bg="#34495e", fg="white").pack(pady=10)
    for idx, (reason, status) in enumerate(leaves):
        tk.Label(win, text=f"{idx+1}. {reason} [{status}]", bg="#34495e", fg="white", anchor="w").pack(fill="x", padx=10, pady=2)

# === Buttons ===
tk.Button(root, text="View Complaints", width=20, bg="#8e44ad", fg="white", command=view_complaints).pack(pady=10)
tk.Button(root, text="View Leave Requests", width=20, bg="#3498db", fg="white", command=view_leaves).pack(pady=10)
tk.Button(root, text="Make Complaint", width=20, bg="#e67e22", fg="white", command=make_complaint).pack(pady=10)
tk.Button(root, text="Request Leave", width=20, bg="#2ecc71", fg="white", command=request_leave).pack(pady=10)
tk.Button(root, text="View Room", width=20, bg="#2980b9", fg="white", command=view_room).pack(pady=10)
tk.Button(root, text="Logout", width=10, bg="#c0392b", fg="white", command=root.destroy).pack(pady=20)

root.mainloop()