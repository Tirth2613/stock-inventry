import csv
import os
from datetime import date
from telegram.ext import Updater, MessageHandler, Filters

TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
CSV_FILE = "inventory.csv"

AVIRA_PROFIT = 480
TIRTH_PROFIT = 380

def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "date","avira_import","tirth_import",
                "avira_remaining","tirth_remaining",
                "avira_sold","tirth_sold",
                "avira_profit","tirth_profit","total_profit"
            ])

def get_today_row():
    today = str(date.today())
    if not os.path.exists(CSV_FILE):
        return None
    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["date"] == today:
                return row
    return None

def save_row(row):
    rows = []
    found = False
    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["date"] == row["date"]:
                rows.append(row)
                found = True
            else:
                rows.append(r)

    if not found:
        rows.append(row)

    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writeheader()
        writer.writerows(rows)

def handle(update, context):
    ensure_csv()
    text = update.message.text.lower().strip()
    today = str(date.today())

    if text.startswith("i"):
        parts = text.split()
        avira = int(parts[parts.index("avira")+1])
        tirth = int(parts[parts.index("tirth")+1])

        row = {
            "date": today,
            "avira_import": avira,
            "tirth_import": tirth,
            "avira_remaining": "",
            "tirth_remaining": "",
            "avira_sold": "",
            "tirth_sold": "",
            "avira_profit": "",
            "tirth_profit": "",
            "total_profit": ""
        }
        save_row(row)
        update.message.reply_text("✅ Import saved")

    elif text.startswith("r"):
        parts = text.split()
        avira_r = int(parts[parts.index("avira")+1])
        tirth_r = int(parts[parts.index("tirth")+1])

        row = get_today_row()
        if not row:
            update.message.reply_text("❌ Import first using I command")
            return

        avira_sold = int(row["avira_import"]) - avira_r
        tirth_sold = int(row["tirth_import"]) - tirth_r

        avira_profit = avira_sold * AVIRA_PROFIT
        tirth_profit = tirth_sold * TIRTH_PROFIT
        total_profit = avira_profit + tirth_profit

        row.update({
            "avira_remaining": avira_r,
            "tirth_remaining": tirth_r,
            "avira_sold": avira_sold,
            "tirth_sold": tirth_sold,
            "avira_profit": avira_profit,
            "tirth_profit": tirth_profit,
            "total_profit": total_profit
        })
        save_row(row)

        update.message.reply_text(
            f"📊 Today Summary\n"
            f"Avira Sold: {avira_sold}\n"
            f"Tirth Sold: {tirth_sold}\n"
            f"Total Profit: ₹{total_profit}"
        )

    elif text == "d":
        row = get_today_row()
        if not row:
            update.message.reply_text("No data for today")
            return
        update.message.reply_text(
            f"📅 Today\n"
            f"Profit: ₹{row['total_profit']}\n"
            f"Avira Sold: {row['avira_sold']}\n"
            f"Tirth Sold: {row['tirth_sold']}"
        )

    elif text == "m":
        total_profit = 0
        total_sold = 0
        days = 0

        with open(CSV_FILE, "r") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r["total_profit"]:
                    total_profit += int(r["total_profit"])
                    total_sold += int(r["avira_sold"]) + int(r["tirth_sold"])
                    days += 1

        avg = total_sold / days if days else 0
        update.message.reply_text(
            f"📆 Monthly Report\n"
            f"Total Profit: ₹{total_profit}\n"
            f"Total Sold: {total_sold}\n"
            f"Avg / Day: {avg:.2f}"
        )

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))
    updater.start_polling()
    updater.idle()

main()
