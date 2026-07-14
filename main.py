import discord
from discord import app_commands
from discord.ext import commands
import random
import os
from threading import Thread
from flask import Flask

# --- SERVEUR WEB (Pour garder le bot en ligne sur Render) ---
app = Flask('')
@app.route('/')
def home(): return "Le bot est en vie !"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CONFIGURATION DU BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Cette ligne synchronise les commandes SLASH avec Discord
        await self.tree.sync()
        print("Commandes Slash synchronisées !")

bot = MyBot()

# Bases de données temporaires
economie = {}  
colles = {}    
eleves_rp = {} 

@bot.event
async def on_ready():
    print(f"Le surveillant {bot.user.name} est prêt !")
    keep_alive()

# --- COMMANDES SLASH ---

@bot.tree.command(name="ping", description="Vérifie si le bot fonctionne")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong ! 🏓 Le bot est bien en ligne.")

@bot.tree.command(name="inscription", description="S'inscrire au lycée RP")
async def inscription(interaction: discord.Interaction, prenom: str, nom: str, classe: str):
    nom_complet = f"{prenom.capitalize()} {nom.upper()}"
    classe_propre = classe.capitalize()
    eleves_rp[interaction.user.id] = {"nom": nom_complet, "classe": classe_propre}
    economie[interaction.user.id] = 10
    
    nouveau_pseudo = f"[{classe_propre}] {nom_complet}"
    try:
        await interaction.user.edit(nick=nouveau_pseudo)
        await interaction.response.send_message(f"🏫 Inscription validée ! Bienvenue {nouveau_pseudo}.")
    except Exception:
        await interaction.response.send_message(f"🏫 Inscription validée ! Bienvenue {nom_complet}.")

@bot.tree.command(name="travail", description="Faire un boulot pour gagner de l'argent")
async def travail(interaction: discord.Interaction):
    if interaction.user.id not in eleves_rp:
        await interaction.response.send_message("❌ Tu dois d'abord faire /inscription !")
        return
    gain = random.randint(5, 15)
    economie[interaction.user.id] = economie.get(interaction.user.id, 0) + gain
    await interaction.response.send_message(f"🧹 Travail terminé ! Tu gagnes {gain}€.")

@bot.tree.command(name="colle", description="[Pions] Coller un élève")
@app_commands.checks.has_permissions(manage_messages=True)
async def colle(interaction: discord.Interaction, membre: discord.Member, heures: int):
    colles[membre.id] = colles.get(membre.id, 0) + heures
    await interaction.response.send_message(f"🚨 {membre.mention} a pris {heures}h de colle !")

@bot.tree.command(name="bulletin", description="Voir son dossier scolaire")
async def bulletin(interaction: discord.Interaction, membre: discord.Member = None):
    cible = membre or interaction.user
    infos = eleves_rp.get(cible.id)
    if not infos:
        await interaction.response.send_message("❌ Cet élève n'est pas inscrit.")
        return
    argent = economie.get(cible.id, 0)
    colles_total = colles.get(cible.id, 0)
    await interaction.response.send_message(f"📋 **Dossier de {infos['nom']}**\nClasse: {infos['classe']}\nArgent: {argent}€\nHeures de colle: {colles_total}h")

# Lancement
bot.run(os.environ.get('DISCORD_TOKEN'))
