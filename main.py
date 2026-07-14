import discord
from discord.ext import commands
import random
import os
from threading import Thread
from flask import Flask

# --- MINI SERVEUR WEB POUR GARDER LE BOT ACTIF SUR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Le bot est en vie !"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ------------------------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# Base de données temporaire
economie = {}  
colles = {}    
eleves_rp = {} 

@bot.event
async def on_ready():
    print(f"Le surveillant général {bot.user.name} est dans la place !")

@bot.command()
async def inscription(ctx, prenom: str, nom: str, classe: str):
    nom_complet = f"{prenom.capitalize()} {nom.upper()}"
    classe_propre = classe.capitalize()
    eleves_rp[ctx.author.id] = {"nom": nom_complet, "classe": classe_propre}
    economie[ctx.author.id] = 10  
    nouveau_pseudo = f"[{classe_propre}] {nom_complet}"
    try:
        await ctx.author.edit(nick=nouveau_pseudo)
        await ctx.send(f"🏫 **Inscription validée !** Bienvenue au lycée, {ctx.author.mention}. Tu as été renommé(e) `{nouveau_pseudo}` et tu reçois 10€ d'argent de poche !")
    except discord.Forbidden:
        await ctx.send(f"🏫 **Inscription validée !** Bienvenue {nom_complet}. *(Permissions insuffisantes pour changer ton pseudo)*")

@bot.command()
async def poche(ctx):
    argent = economie.get(ctx.author.id, 0)
    await ctx.send(f"👛 {ctx.author.mention}, tu as **{argent}€** d'argent de poche.")

@bot.command()
async def travailler(ctx):
    if ctx.author.id not in eleves_rp:
        await ctx.send("❌ Tu dois d'abord t'inscrire avec `!inscription [Prénom] [Nom] [Classe]` !")
        return
    gain = random.randint(5, 15)
    economie[ctx.author.id] = economie.get(ctx.author.id, 0) + gain
    jobs = [
        "Tu as lavé les tableaux de l'aile B.",
        "Tu as aidé la documentaliste à ranger le CDI.",
        "Tu as ramassé les papiers dans la cour de récréation."
    ]
    await ctx.send(f"🧹 {random.choice(jobs)} Tu gagnes **{gain}€**.")

@bot.command()
@commands.has_permissions(manage_messages=True) 
async def colle(ctx, membre: discord.Member, heures: int = 1):
    colles[membre.id] = colles.get(membre.id, 0) + heures
    await ctx.send(f"🚨 **DISCIPLINE :** {membre.mention} a écopé de **{heures} heure(s) de colle** !")

@bot.command()
async def bulletin(ctx, membre: discord.Member = None):
    cible = membre or ctx.author
    infos = eleves_rp.get(cible.id)
    if not infos:
        await ctx.send(f"❌ Cet élève n'est pas encore inscrit.")
        return
    heures_colle = colles.get(cible.id, 0)
    argent = economie.get(cible.id, 0)
    
    embed = discord.Embed(title=f"📋 Dossier Scolaire - {infos['nom']}", color=0x3498db)
    embed.add_field(name="Classe", value=infos['classe'], inline=True)
    embed.add_field(name="Argent", value=f"{argent}€", inline=True)
    embed.add_field(name="Heures de colle", value=f"⚠️ {heures_colle}h", inline=False)
    await ctx.send(embed=embed)

# On lance le serveur web pour tromper Render et garder le bot en ligne
keep_alive()

# Lancement du bot via la variable d'environnement
bot.run(os.environ.get('DISCORD_TOKEN'))
