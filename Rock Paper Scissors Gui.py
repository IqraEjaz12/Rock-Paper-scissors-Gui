"""
Rock Paper Scissors - Graphical Game (Tkinter)
Save as: rock_paper_scissors_gui.py
Run: python rock_paper_scissors_gui.py

Features:
- Clickable buttons with emoji and text
- Best-of-N match selection
- Animated CPU choice preview
- Scoreboard, round announcements, and Play Again
- Lightweight single-file (no external assets required)
"""

import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import sys
import time

# --- Constants ---
CHOICES = ["Rock", "Paper", "Scissors"]
EMOJI = {"Rock": "✊", "Paper": "✋", "Scissors": "✌️"}
WIN_MAP = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}

# --- Game logic ---

def decide_winner(user, comp):
    if user == comp:
        return "tie"
    return "user" if WIN_MAP[user] == comp else "comp"

# --- GUI Application ---
class RPSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rock Paper Scissors — Play")
        self.resizable(False, False)
        self.configure(padx=12, pady=12, bg="#111" )

        # state
        self.best_of = 3
        self.needed = self.best_of // 2 + 1
        self.score_user = 0
        self.score_comp = 0
        self.round_no = 0

        # UI
        self._create_header()
        self._create_board()
        self._create_controls()
        self._reset_match()

    def _create_header(self):
        header = tk.Label(self, text="Rock • Paper • Scissors", font=("Segoe UI", 18, "bold"), fg="#fff", bg="#111")
        header.grid(row=0, column=0, columnspan=3, pady=(0,8))

        self.match_label = tk.Label(self, text="Best of: 3", font=("Segoe UI", 10), fg="#ddd", bg="#111")
        self.match_label.grid(row=1, column=0, columnspan=3)

    def _create_board(self):
        # scoreboard
        self.score_label = tk.Label(self, text="You: 0    CPU: 0", font=("Segoe UI", 12), fg="#fff", bg="#111")
        self.score_label.grid(row=2, column=0, columnspan=3, pady=(8,6))

        # central announcement
        self.announce = tk.Label(self, text="Choose your move", font=("Segoe UI", 12), fg="#ffd", bg="#111")
        self.announce.grid(row=3, column=0, columnspan=3, pady=(0,10))

        # choices preview
        self.user_choice_label = tk.Label(self, text="You: —", font=("Segoe UI", 14), fg="#9f9", bg="#111")
        self.user_choice_label.grid(row=4, column=0, padx=6)

        self.vs_label = tk.Label(self, text="VS", font=("Segoe UI", 14, "bold"), fg="#fff", bg="#111")
        self.vs_label.grid(row=4, column=1)

        self.comp_choice_label = tk.Label(self, text="CPU: —", font=("Segoe UI", 14), fg="#f99", bg="#111")
        self.comp_choice_label.grid(row=4, column=2, padx=6)

    def _create_controls(self):
        # Buttons for Rock, Paper, Scissors
        btn_frame = tk.Frame(self, bg="#111")
        btn_frame.grid(row=5, column=0, columnspan=3, pady=(12,6))

        for i, choice in enumerate(CHOICES):
            b = tk.Button(btn_frame, text=f"{EMOJI[choice]}\n{choice}", font=("Segoe UI", 12), width=10, height=3,
                          command=lambda c=choice: self.player_move(c))
            b.grid(row=0, column=i, padx=6)

        # controls row
        ctrl_frame = tk.Frame(self, bg="#111")
        ctrl_frame.grid(row=6, column=0, columnspan=3, pady=(10,0))

        self.best_btn = tk.Button(ctrl_frame, text="Set Best-of", command=self.set_best_of)
        self.best_btn.grid(row=0, column=0, padx=6)

        self.reset_btn = tk.Button(ctrl_frame, text="Reset Match", command=self._reset_match)
        self.reset_btn.grid(row=0, column=1, padx=6)

        self.exit_btn = tk.Button(ctrl_frame, text="Exit", command=self._on_exit)
        self.exit_btn.grid(row=0, column=2, padx=6)

    # --- Controls ---
    def set_best_of(self):
        ans = simpledialog.askstring("Best of...", "Enter an odd number of rounds (e.g., 1,3,5,7):", parent=self)
        if ans is None:
            return
        if not ans.isdigit():
            messagebox.showerror("Invalid", "Please enter a positive odd integer.")
            return
        n = int(ans)
        if n <= 0 or n % 2 == 0:
            messagebox.showerror("Invalid", "Number must be positive and odd.")
            return
        self.best_of = n
        self.needed = n // 2 + 1
        self.match_label.config(text=f"Best of: {self.best_of}")
        self._reset_match()

    def _reset_match(self):
        self.score_user = 0
        self.score_comp = 0
        self.round_no = 0
        self._update_scoreboard()
        self.user_choice_label.config(text="You: —")
        self.comp_choice_label.config(text="CPU: —")
        self.announce.config(text="Choose your move")

    def _on_exit(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.destroy()
            sys.exit(0)

    def _update_scoreboard(self):
        self.score_label.config(text=f"You: {self.score_user}    CPU: {self.score_comp}")

    # --- Gameplay ---
    def player_move(self, choice):
        if self.score_user >= self.needed or self.score_comp >= self.needed:
            # match already over
            messagebox.showinfo("Match over", "Match is over. Reset to play again or change Best-of.")
            return

        self.round_no += 1
        self.user_choice_label.config(text=f"You: {EMOJI[choice]} {choice}")
        self.announce.config(text="CPU is choosing...")
        self.update()  # show immediate changes

        # animated CPU selection preview
        comp = self._animated_cpu_choice()

        self.comp_choice_label.config(text=f"CPU: {EMOJI[comp]} {comp}")
        result = decide_winner(choice, comp)

        if result == "tie":
            self.announce.config(text=f"Round {self.round_no}: It's a tie.")
        elif result == "user":
            self.score_user += 1
            self.announce.config(text=f"Round {self.round_no}: You win this round!")
        else:
            self.score_comp += 1
            self.announce.config(text=f"Round {self.round_no}: CPU wins this round.")

        self._update_scoreboard()

        # check for match end
        if self.score_user >= self.needed or self.score_comp >= self.needed:
            self._finish_match()

    def _animated_cpu_choice(self):
        # simple loop to show changing choice
        spins = 9
        comp_choice = random.choice(CHOICES)
        for i in range(spins):
            comp_choice = random.choice(CHOICES)
            self.comp_choice_label.config(text=f"CPU: {EMOJI[comp_choice]} ?")
            self.update()
            # speed up near the end
            time.sleep(0.06 + (spins - i) * 0.01)
        return comp_choice

    def _finish_match(self):
        if self.score_user > self.score_comp:
            winner_text = "You won the match! 🎉"
        else:
            winner_text = "CPU won the match. 😵"

        self.announce.config(text=winner_text)
        # prompt to play again
        if messagebox.askyesno("Match finished", f"{winner_text}\n\nPlay again?"):
            self._reset_match()
        else:
            # leave scoreboard visible; user can Exit
            pass


if __name__ == '__main__':
    app = RPSApp()
    app.mainloop()
