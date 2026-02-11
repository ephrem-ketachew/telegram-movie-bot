import os
from dotenv import load_dotenv
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random
import requests

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

elite_movies = [
    "The Shawshank Redemption", "The Godfather", "The Dark Knight", 
    "12 Angry Men", "Schindler's List", "The Lord of the Rings: The Return of the King", 
    "Pulp Fiction", "Fight Club", "Forrest Gump", "Inception", 
    "The Matrix", "Goodfellas", "Se7en", "City of God", 
    "The Silence of the Lambs", "Spirited Away", "Saving Private Ryan", 
    "Interstellar", "Parasite", "The Green Mile", "Gladiator", 
    "The Departed", "Whiplash", "The Prestige", "The Lion King"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = "Hi Epha 👋\nI am now connected to the global movie database! 🌍\nType /movie or /info <name>."
    await update.message.reply_text(welcome_message)

async def movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Let me find a certified masterpiece for you...")
    
    chosen_movie = random.choice(elite_movies)
    url = f"http://www.omdbapi.com/?t={chosen_movie}&apikey={OMDB_API_KEY}"
    
    response = requests.get(url)
    data = response.json()

    if data.get("Response") == "True":
        title = data.get("Title")
        year = data.get("Year")
        rating = data.get("imdbRating")
        genre = data.get("Genre")
        plot = data.get("Plot")
        poster = data.get("Poster")

        msg = (
            f"🔥 *TOP TIER RECOMMENDATION* 🔥\n\n"
            f"⭐ *{title} ({year})*\n"
            f"📈 IMDb Rating: {rating} / 10\n"
            f"🎭 Genre: {genre}\n"
            f"📖 Plot: {plot}"
        )
        
        if poster and poster != "N/A":
            await update.message.reply_photo(photo=poster, caption=msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("Oops! My database hiccuped. Try /movie again!")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please give me a movie name! Example: /info Titanic")
        return

    user_movie_name = " ".join(context.args)
    url = f"http://www.omdbapi.com/?t={user_movie_name}&apikey={OMDB_API_KEY}"
    
    response = requests.get(url)
    data = response.json()

    if data.get("Response") == "True":
        title = data.get("Title")
        year = data.get("Year")
        rating = data.get("imdbRating")
        genre = data.get("Genre")
        plot = data.get("Plot")
        director = data.get("Director")
        poster = data.get("Poster")

        msg = (
            f"⭐ *{title} ({year})*\n"
            f"🎬 Director: {director}\n"
            f"📈 Rating: {rating}\n"
            f"🎭 Genre: {genre}\n"
            f"📖 Plot: {plot}"
        )
        
        if poster and poster != "N/A":
            await update.message.reply_photo(photo=poster, caption=msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text(f"Sorry, I couldn't find '{user_movie_name}' on the global database! 😔")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "/movie - Get a masterpiece recommendation\n/info <name> - Search the global database\n/help - Show commands"
    await update.message.reply_text(help_text)

async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "Hmm, I don't understand normal chat yet! 🤔\nPlease use my commands. Type /help to see what I can do."
    await update.message.reply_text(response)

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Epha's Bot is alive and polling!")
            
    httpd = HTTPServer(server_address, Handler)
    httpd.serve_forever()

if __name__ == '__main__':
    print("Bot is waking up securely! Loading keys from .env...")
    
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("movie", movie))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text))
    
    print("Bot is online!")
    app.run_polling()