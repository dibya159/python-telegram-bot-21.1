import os
import random
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Render के लिए वेब सर्वर
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running successfully!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    # Flask को बिना किसी थ्रेडिंग एरर के चलाने के लिए
    app.run(host='0.0.0.0', port=port, use_reloader=False)

# सभी 60 चैलेंजेस की लिस्ट
EMOJI_POOL = [
    {"emojis": "🌧️ + 🏹", "answer": "rainbow"},
    {"emojis": "🔥 + 🐶", "answer": "hot dog"},
    {"emojis": "☀️ + 🌸", "answer": "sunflower"},
    {"emojis": "🐮 + 👦", "answer": "cowboy"},
    {"emojis": "🌲 + 🍎", "answer": "pineapple"},
    {"emojis": "🥛 + 🤝", "answer": "milkshake"},
    {"emojis": "🦷 + 🖌️", "answer": "toothbrush"},
    {"emojis": "👩‍🏫 + 🧑‍🎓", "answer": "teacher"},
    {"emojis": "❤️ + 🐦", "answer": "lovebird"},
    {"emojis": "❄️ + 👦", "answer": "snowman"},
    {"emojis": "🚒 + 🚚", "answer": "fire truck"},
    {"emojis": "🧈 + 🪰", "answer": "butterfly"},
    {"emojis": "🥵 + 🍫", "answer": "hot chocolate"},
    {"emojis": "🍔 + 👑", "answer": "burger king"},
    {"emojis": "🏴‍☠️ + 🦜", "answer": "pirate"},
    {"emojis": "🍳 + 🎂", "answer": "pancake"},
    {"emojis": "🚽 + 🧻", "answer": "toilet paper"},
    {"emojis": "🗑️ + 🏀", "answer": "basketball"},
    {"emojis": "🌙 + 💡", "answer": "moonlight"},
    {"emojis": "🧊 + 🐻", "answer": "polar bear"},
    {"emojis": "🔴 + 🐂", "answer": "red bull"},
    {"emojis": "🚪 + 🔔", "answer": "doorbell"},
    {"emojis": "💡 + 🏠", "answer": "lighthouse"},
    {"emojis": "⭐ + 🐟", "answer": "starfish"},
    {"emojis": "☀️ + 🕶️", "answer": "sunglasses"},
    {"emojis": "🌹 + 🧜‍♀️", "answer": "rosemary"},
    {"emojis": "💧 + 🧗‍♂️", "answer": "waterfall"},
    {"emojis": "🧅 + 💍", "answer": "onion rings"},
    {"emojis": "🎹 + 🪵", "answer": "keyboard"},
    {"emojis": "👂 + 💍", "answer": "earring"},
    {"emojis": "🦇 + 👨", "answer": "batman"},
    {"emojis": "💧 + 🍈", "answer": "watermelon"},
    {"emojis": "🌊 + 🐴", "answer": "seahorse"},
    {"emojis": "⭐ + 💵", "answer": "starbucks"},
    {"emojis": "👄 + 🪵", "answer": "lipstick"},
    {"emojis": "👂 + 📱", "answer": "earphone"},
    {"emojis": "✋ + 👜", "answer": "handbag"},
    {"emojis": "🥚 + 🌲", "answer": "eggplant"},
    {"emojis": "🕷️ + 👨", "answer": "spider-man"},
    {"emojis": "🪼 + 🐟", "answer": "jellyfish"},
    {"emojis": "⚙️ + 👨", "answer": "iron man"},
    {"emojis": "🔵 + 🍓", "answer": "blueberry"},
    {"emojis": "🥩 + 🔴", "answer": "meatball"},
    {"emojis": "🧀 + 🎂", "answer": "cheesecake"},
    {"emojis": "🩺 + 🌶️", "answer": "dr pepper"},
    {"emojis": "🦁 + 👑", "answer": "lion king"},
    {"emojis": "🌮 + 🔔", "answer": "taco bell"},
    {"emojis": "🛠️ + 📦", "answer": "toolbox"},
    {"emojis": "🍯 + 🌙", "answer": "honeymoon"},
    {"emojis": "📸 + 📈", "answer": "photograph"},
    {"emojis": "🐜 + 👨", "answer": "ant-man"},
    {"emojis": "🍕 + 🛖", "answer": "pizza hut"},
    {"emojis": "🍬 + 🥔", "answer": "sweet potato"},
    {"emojis": "✉️ + 📦", "answer": "mailbox"},
    {"emojis": "🐒 + 🔑", "answer": "monkey"},
    {"emojis": "🧁 + 🎂", "answer": "cupcake"},
    {"emojis": "🌲 + 🏠", "answer": "treehouse"},
    {"emojis": "🦶 + ⚽", "answer": "football"},
    {"emojis": "🥜 + 🧈", "answer": "peanut butter"},
    {"emojis": "⚔️ + 🐟", "answer": "swordfish"}
]

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    
    # अगर गेम पहले से चल रहा है
    if context.chat_data.get("game_active"):
        await update.message.reply_text("Game is already running in this chat!")
        return

    # गेम का डेटा सेट करें
    sample_size = min(20, len(EMOJI_POOL))
    context.chat_data["current_questions"] = random.sample(EMOJI_POOL, sample_size)
    context.chat_data["active_question_index"] = 0
    context.chat_data["score_board"] = {}
    context.chat_data["game_active"] = True

    await update.message.reply_text("Game started! You have 30 seconds per question.")
    await ask_question(chat_id, context)

async def ask_question(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    idx = context.chat_data["active_question_index"]
    questions = context.chat_data["current_questions"]

    # अगर सारे सवाल खत्म हो गए
    if idx >= len(questions):
        await finish_game(chat_id, context)
        return

    q_data = questions[idx]
    context.chat_data["current_answer"] = q_data["answer"]

    # सवाल भेजें
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Question {idx + 1}:\n{q_data['emojis']}"
    )

    # अगर कोई पुराना टाइमर चल रहा है तो उसे रोक दें
    old_job = context.chat_data.get("timeout_job")
    if old_job:
        old_job.schedule_removal()

    # नया 30 सेकंड का टाइमर सेट करें
    new_job = context.job_queue.run_once(
        timeout_handler, 
        30, 
        chat_id=chat_id, 
        data={"expected_index": idx}
    )
    context.chat_data["timeout_job"] = new_job

async def timeout_handler(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = context.job.chat_id
    expected_index = context.job.data["expected_index"]
    
    if not context.chat_data.get("game_active"):
        return
        
    # अगर यह टाइमर उस सवाल का नहीं है जो अभी चल रहा है, तो इग्नोर करें
    if context.chat_data["active_question_index"] != expected_index:
        return

    current_answer = context.chat_data.get("current_answer", "")
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Time's up! The correct answer was: {current_answer.upper()}"
    )

    # अगले सवाल पर बढ़ें
    context.chat_data["active_question_index"] += 1
    await ask_question(chat_id, context)

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
        
    if not context.chat_data.get("game_active"):
        return
    
    current_answer = context.chat_data.get("current_answer")
    if not current_answer:
        return
    
    user_guess_clean = update.message.text.strip().lower().replace(" ", "")
    correct_answer_clean = current_answer.replace(" ", "")
    
    if user_guess_clean == correct_answer_clean:
        # सही जवाब मिलने पर टाइमर बंद करें
        old_job = context.chat_data.get("timeout_job")
        if old_job:
            old_job.schedule_removal()

        user_name = update.message.from_user.full_name
        score_board = context.chat_data["score_board"]
        score_board[user_name] = score_board.get(user_name, 0) + 1
        
        await update.message.reply_text(
            f"Correct! {user_name} got it right. The answer was: {current_answer.upper()}"
        )
        
        # अगले सवाल पर बढ़ें
        context.chat_data["active_question_index"] += 1
        await ask_question(update.message.chat_id, context)

async def finish_game(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.chat_data["game_active"] = False
    score_board = context.chat_data.get("score_board", {})
    
    result_text = "Game Over! Leaderboard:\n"
    if not score_board:
        result_text += "No one scored any points!"
    else:
        sorted_scores = sorted(score_board.items(), key=lambda x: x[1], reverse=True)
        for rank, (name, score) in enumerate(sorted_scores, 1):
            result_text += f"{rank}. {name}: {score}\n"
            
    await context.bot.send_message(chat_id=chat_id, text=result_text)

def main() -> None:
    # वेब सर्वर को अलग थ्रेड में शुरू करें
    server_thread = Thread(target=run_web_server, daemon=True)
    server_thread.start()
    
    # बॉट शुरू करें
    application = Application.builder().token("8686475748:AAF1o1HMCIaJMjQZIOC4PGNuV4oFH8tvdAA").build()
    
    application.add_handler(CommandHandler("start", start_game))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))
    
    # बॉट को पोलिंग मोड में चलाएं
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
