import tkinter as tk
from tkinter import messagebox
import sqlite3

# -- DB Connection --
conn = sqlite3.connect("hostel.db")
cur = conn.cursor()

# Alter table users to add new columns if they don't exist
try:
    cur.execute("ALTER TABLE users ADD COLUMN floor INTEGER")
except sqlite3.OperationalError:
    pass
try:
    cur.execute("ALTER TABLE users ADD COLUMN seater TEXT")
except sqlite3.OperationalError:
    pass
# Add viewed column to complaints if not exists
try:
    cur.execute("ALTER TABLE complaints ADD COLUMN viewed INTEGER DEFAULT 0")
except sqlite3.OperationalError:
    pass

# -- GUI Setup --
root = tk.Tk()
root.title("Admin Panel")
root.geometry("700x500")
root.configure(bg="#2e3f4f")

tk.Label(root, text="👨‍💼 Admin Dashboard", font=("Arial", 20, "bold"), fg="white", bg="#2e3f4f").pack(pady=10)

# === Features ===

def approve_leaves():
    win = tk.Toplevel(root)
    win.title("Approve Leaves")
    win.geometry("400x300")
    win.configure(bg="#34495e")
    tk.Label(win, text="Pending Leave Requests", bg="#34495e", fg="white").pack()

    cur.execute("SELECT id, email, reason FROM leaves WHERE status='Pending'")
    leaves = cur.fetchall()

    def approve(lid):
        cur.execute("UPDATE leaves SET status='Approved' WHERE id=?", (lid,))
        conn.commit()
        messagebox.showinfo("Done", "Leave Approved")
        win.destroy()

    def reject(lid):
        cur.execute("UPDATE leaves SET status='Rejected' WHERE id=?", (lid,))
        conn.commit()
        messagebox.showinfo("Done", "Leave Rejected")
        win.destroy()

    for leave in leaves:
        frame = tk.Frame(win, bg="#34495e")
        frame.pack(pady=5, fill="x")
        tk.Label(frame, text=f"{leave[1]}: {leave[2]}", bg="#34495e", fg="white").pack(side=tk.LEFT)
        tk.Button(frame, text="✅", command=lambda lid=leave[0]: approve(lid), bg="#27ae60", fg="white").pack(side=tk.RIGHT, padx=2)
        tk.Button(frame, text="❌", command=lambda lid=leave[0]: reject(lid), bg="#c0392b", fg="white").pack(side=tk.RIGHT, padx=2)

def assign_room():
    def assign():
        if not email.get() or not floor.get() or not seater.get():
            messagebox.showerror("Error", "All fields are required.")
            return
        cur.execute("UPDATE users SET floor=?, seater=? WHERE email=?", (int(floor.get()), seater.get(), email.get()))
        conn.commit()
        messagebox.showinfo("Done", f"Floor {floor.get()} and Seater {seater.get()} assigned to {email.get()}.")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Assign Room")
    win.geometry("350x220")
    win.configure(bg="#34495e")
    email = tk.StringVar()
    floor = tk.StringVar()
    seater = tk.StringVar()
    tk.Label(win, text="Student Email", bg="#34495e", fg="white").pack(pady=5)
    tk.Entry(win, textvariable=email).pack()
    tk.Label(win, text="Floor (1, 2, 3)", bg="#34495e", fg="white").pack(pady=5)
    tk.Entry(win, textvariable=floor).pack()
    tk.Label(win, text="Seater (Single, Double, Triple)", bg="#34495e", fg="white").pack(pady=5)
    tk.Entry(win, textvariable=seater).pack()
    tk.Button(win, text="Assign", command=assign, bg="#27ae60", fg="white").pack(pady=10)

def remove_student():
    def remove():
        cur.execute("DELETE FROM users WHERE email=?", (email.get(),))
        conn.commit()
        messagebox.showinfo("Removed", "Student removed.")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Remove Student")
    win.geometry("300x150")
    win.configure(bg="#34495e")
    email = tk.StringVar()
    tk.Label(win, text="Student Email", bg="#34495e", fg="white").pack(pady=10)
    tk.Entry(win, textvariable=email).pack()
    tk.Button(win, text="Remove", command=remove, bg="#c0392b", fg="white").pack(pady=10)

def view_complaints():
    win = tk.Toplevel(root)
    win.title("Student Complaints")
    win.geometry("400x350")
    win.configure(bg="#34495e")
    tk.Label(win, text="Unviewed Complaints", bg="#34495e", fg="white").pack()
    cur.execute("SELECT id, email, complaint FROM complaints WHERE viewed=0")
    unviewed = cur.fetchall()
    for cid, email, msg in unviewed:
        frame = tk.Frame(win, bg="#34495e")
        frame.pack(fill="x", pady=2)
        tk.Label(frame, text=f"{email}: {msg}", bg="#34495e", fg="white").pack(side=tk.LEFT)
        tk.Button(frame, text="Mark as Viewed", command=lambda cid=cid: mark_viewed(cid, win), bg="#27ae60", fg="white").pack(side=tk.RIGHT, padx=5)
    tk.Label(win, text="Viewed Complaints", bg="#34495e", fg="white").pack(pady=10)
    cur.execute("SELECT email, complaint FROM complaints WHERE viewed=1")
    viewed = cur.fetchall()
    for email, msg in viewed:
        tk.Label(win, text=f"{email}: {msg}", bg="#34495e", fg="white").pack(anchor="w", padx=10)

def mark_viewed(cid, win):
    cur.execute("UPDATE complaints SET viewed=1 WHERE id=?", (cid,))
    conn.commit()
    messagebox.showinfo("Done", "Complaint marked as viewed.")
    win.destroy()
    view_complaints()

def view_students():
    win = tk.Toplevel(root)
    win.title("All Students")
    win.geometry("650x400")
    win.configure(bg="#34495e")
    tk.Label(win, text="Students List", font=("Arial", 14, "bold"), bg="#34495e", fg="white").pack(pady=10)
    frame = tk.Frame(win, bg="#34495e")
    frame.pack(fill="both", expand=True)
    cur.execute("SELECT name, email, floor, seater FROM users WHERE role='student'")
    students = cur.fetchall()
    for idx, (name, email, floor, seater) in enumerate(students):
        tk.Label(frame, text=f"{idx+1}. {name} | {email} | Floor: {floor} | Seater: {seater}",
                 bg="#34495e", fg="white", anchor="w").pack(fill="x", padx=10, pady=2)

# === Buttons ===
tk.Button(root, text="Approve Leave", command=approve_leaves,
          bg="#27ae60", fg="white", width=25).pack(pady=10)

tk.Button(root, text="Assign Room", command=assign_room,
          bg="#3498db", fg="white", width=25).pack(pady=10)

tk.Button(root, text="Remove Student", command=remove_student,
          bg="#c0392b", fg="white", width=25).pack(pady=10)

tk.Button(root, text="View Complaints", command=view_complaints,
          bg="#f39c12", fg="white", width=25).pack(pady=10)

tk.Button(root, text="View All Students", command=view_students,
          bg="#8e44ad", fg="white", width=25).pack(pady=10)

tk.Button(root, text="Logout", command=root.destroy,
          bg="#7f8c8d", fg="white", width=10).pack(pady=20)

root.mainloop()