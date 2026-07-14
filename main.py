import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True # Important pour renommer les membres

bot = commands.Bot(command_prefix="!", intents=intents)

# Bases de données temporaires (dans la vraie vie on utiliserait un fichier, 
# mais pour commencer sur téléphone, cela stocke en mémoire)
economie = {}  # ID Discord -> Argent de poche
colles = {}    # ID Discord -> Nombre d'heures de colle
eleves_rp = {} # ID Discord -> {"nom": str, "classe": str}

@bot.event
async def on_ready():
    print(f"Le surveillant général {bot.user.name} est dans la place !")

# --- SYSTÈME D'INSCRIPTION RP ---
@bot.command()
async def inscription(ctx, prenom: str, nom: str, classe: str):
    """S'inscrire au lycée RP. Exemple: !inscription Jean Dupont Seconde"""
    nom_complet = f"{prenom.capitalize()} {nom.upper()}"
    classe_propre = classe.capitalize()
    
    eleves_rp[ctx.author.id] = {"nom": nom_complet, "classe": classe_propre}
    economie[ctx.author.id] = 10  # 10€ de bienvenue
    
    # On renomme l'élève automatiquement sur le serveur
    nouveau_pseudo = f"[{classe_propre}] {nom_complet}"
    try:
        await ctx.author.edit(nick=nouveau_pseudo)
        await ctx.send(f"🏫 **Inscription validée !** Bienvenue au lycée, {ctx.author.mention}. Tu as été renommé(e) `{nouveau_pseudo}` et tu reçois 10€ d'argent de poche !")
    except discord.Forbidden:
        await ctx.send(f"🏫 **Inscription validée !** Bienvenue {nom_complet}. *(Note : Je n'ai pas la permission de modifier ton pseudo, vérifie que mon rôle est bien au-dessus du tien !)*")

# --- SYSTÈME D'ARGENT DE POCHE (ÉCONOMIE) ---
@bot.command()
async def poche(ctx):
    """Regarder dans ses poches (solde)"""
    argent = economie.get(ctx.author.id, 0)
    await ctx.send(f"👛 {ctx.author.mention}, tu as **{argent}€** d'argent de poche.")

@bot.command()
async def travailler(ctx):
    """Faire un petit boulot au lycée (nettoyer le tableau, aider au CDI)"""
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

# --- SYSTÈME DE DISCIPLINE (COLLES) ---
@bot.command()
@commands.has_permissions(manage_messages=True) # Seuls les modérateurs/pions peuvent l'utiliser
async def colle(ctx, membre: discord.Member, heures: int = 1):
    """[Pions/Profs] Coller un élève. Exemple: !colle @Jean 2"""
    colles[membre.id] = colles.get(membre.id, 0) + heures
    await ctx.send(f"🚨 **DISCIPLINE :** {membre.mention} a écopé de **{heures} heure(s) de colle** pour comportement perturbateur !")

@bot.command()
async def bulletin(ctx, membre: discord.Member = None):
    """Consulter son casier scolaire ou celui d'un autre élève"""
    cible = membre or ctx.author
    infos = eleves_rp.get(cible.id)
    
    if not infos:
        await ctx.send(f"❌ Cet élève n'est pas encore inscrit au secrétariat.")
        return
        
    heures_colle = colles.get(cible.id, 0)
    argent = economie.get(cible.id, 0)
    
    embed = discord.Embed(title=f"📋 Dossier Scolaire - {infos['nom']}", color=0x3498db)
    embed.add_field(name="Classe", value=infos['classe'], inline=True)
    embed.add_field(name="Argent de poche", value=f"{argent}€", inline=True)
    embed.add_field(name="Heures de colle au compteur", value=f"⚠️ {heures_colle} heure(s)", inline=False)
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Seuls les professeurs et les surveillants ont le droit d'utiliser cette commande !")
  
