import json
import os
import matplotlib.pyplot as plt
from datetime import datetime


def plot_user_skin_history(user_id):
    folder = os.path.join("data", "users", user_id)
    tips_file = os.path.join(folder, "daily_tips.json")

    if not os.path.exists(tips_file):
        print("No tip history available.")
        return

    with open(tips_file, "r") as f:
        tips = json.load(f)

    dates = []
    emojis = []

    for key in sorted(tips):
        date_str, period = key.split("_")[:2]
        tip = tips[key]
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        dates.append(date.strftime("%m-%d") + f" ({period})")
        emojis.append(tip.split()[0])

    plt.figure(figsize=(12, 4))
    plt.plot(dates, [1] * len(dates), "o", markersize=10, color="white")

    for i, emoji in enumerate(emojis):
        plt.text(i, 1, emoji, fontsize=16, ha="center", va="center")

    plt.yticks([])
    plt.xticks(rotation=45, fontsize=9)
    plt.title(f"Skin Tip History for {user_id.capitalize()}")
    plt.grid(axis="x")
    plt.tight_layout()
    plt.show()


# Example usage:
# plot_user_skin_history("sorin test")
