import os
import sqlite3
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")
TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")
DATABASE = "king_daily.db"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def init_database():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                request TEXT NOT NULL,
                work_date TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "KING DAILY đã sẵn sàng!\n"
        "Đăng ký ốp bằng cú pháp:\n"
        "/op 28/11 Ca tối"
    )

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "Anh/chị nhập theo mẫu:\n/op 28/11 Ca tối"
        )
        return

    request = " ".join(context.args)
    user = update.effective_user
    group_id = update.effective_chat.id
    now = datetime.now(TIMEZONE)

    try:
        work_date = datetime.strptime(
            context.args[0], "%d/%m"
        ).replace(year=now.year).strftime("%Y-%m-%d")

        if len(context.args) < 2:
            raise ValueError("Thiếu nội dung đăng ký")

    except ValueError:
        await update.message.reply_text(
            "Ngày chưa đúng định dạng. Ví dụ:\n/op 28/11 Ca tối"
        )
        return

    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            INSERT INTO registrations
            (group_id, user_name, request, work_date, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            group_id,
            user.full_name,
            request,
            work_date,
            now.isoformat()
        ))

    await update.message.reply_text(
        f"Đã ghi nhận đăng ký của {user.full_name}:\n{request}"
    )

async def daily_summary(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")

    with sqlite3.connect(DATABASE) as conn:
        groups = conn.execute("""
            SELECT DISTINCT group_id
            FROM registrations
            WHERE work_date = ?
        """, (today,)).fetchall()

        for (group_id,) in groups:
            rows = conn.execute("""
                SELECT user_name, request
                FROM registrations
                WHERE group_id = ? AND work_date = ?
                ORDER BY id
            """, (group_id, today)).fetchall()

            if not rows:
                continue

            lines = [
                f"📋 LỊCH ỐP KING DAILY - {datetime.now(TIMEZONE).strftime('%d/%m/%Y')}",
                ""
            ]

            for index, (name, request) in enumerate(rows, 1):
                lines.append(f"{index}. {name}: {request}")

            await context.bot.send_message(
                chat_id=group_id,
                text="\n".join(lines)
            )

def main():
    if not TOKEN:
        raise RuntimeError("Chưa cấu hình BOT_TOKEN")

    init_database()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("op", register))

    app.job_queue.run_daily(
        daily_summary,
        time=datetime.strptime("17:00", "%H:%M").time().replace(
            tzinfo=TIMEZONE
        ),
        name="king_daily_summary"
    )

    app.run_polling()

if _name_ == "_main_":
    main()
Đã gửi
Soạn
Viết cho Phạm Thị Thu Hà


