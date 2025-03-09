import random
import discord
from discord import app_commands
from discord.ext import commands
import socket
import struct
import time
import sys
import itertools

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

GUILD_ID = 1117787386772983920
GMOD_SERVER_IP = "134.255.218.16"
GMOD_SERVER_PORT = 27026

# Funktion, um den Sneakers-Effekt anzuwenden
def sneakers_effect(text, speed=0.05, color_code=""):
    for char in text:
        sys.stdout.write(color_code + char)
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write("\033[0m\n")  # Reset der Farbe nach dem Effekt

# Funktion für Regenbogentext
def rainbow_text(text):
    rainbow = [
        "\033[31m", "\033[33m", "\033[32m", "\033[36m", "\033[34m", "\033[35m"
    ]
    colored_text = ""
    color_index = 0
    for char in text:
        colored_text += rainbow[color_index % len(rainbow)] + char
        color_index += 1
    return colored_text + "\033[0m"  # Reset der Farbe am Ende

def is_server_online(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3.0)
            return sock.connect_ex((ip, port)) == 0
    except Exception:
        return False

def get_player_count(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(3.0)
            request = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
            sock.sendto(request, (ip, port))
            data, _ = sock.recvfrom(4096)

            if len(data) < 5 or data[:4] != b'\xFF\xFF\xFF\xFF':
                return 0

            if data[4] == 0x41:
                challenge = struct.unpack('<I', data[5:9])[0]
                request = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00' + struct.pack('<I', challenge)
                sock.sendto(request, (ip, port))
                data, _ = sock.recvfrom(4096)

            if data[4] != 0x49:
                return 0

            offset = 6
            name_end = data.index(b'\x00', offset) + 1
            map_end = data.index(b'\x00', name_end) + 1
            folder_end = data.index(b'\x00', map_end) + 1
            game_end = data.index(b'\x00', folder_end) + 1

            offset = game_end + 2
            players = data[offset]
            max_players = data[offset + 1]

            return players
    except Exception:
        return 0

def get_player_names(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(3.0)
            request = b'\xFF\xFF\xFF\xFFU' + b'\x00'
            sock.sendto(request, (ip, port))
            data, _ = sock.recvfrom(4096)

            if len(data) < 5 or data[:4] != b'\xFF\xFF\xFF\xFF':
                return []

            players = []
            offset = 5
            while offset < len(data):
                if data[offset] == 0:
                    break
                end_offset = data.index(b'\x00', offset)
                players.append(data[offset:end_offset].decode(errors='ignore'))
                offset = end_offset + 9

            return players
    except Exception:
        return []

@bot.event
async def on_ready():
    # ASCII-Banner für den Bot, jetzt rot
    banner = """
    __  __          _____   _____ ______ _      
    |  \/  |   /\   |  __ \ / ____|  ____| |     
    | \  / |  /  \  | |__) | |    | |__  | |     
    | |\/| | / /\ \ |  _  /| |   |  __|  | |     
    | |  | |/ ____ \| | \ \| |____| |____| |____ 
    |_|  |_/_/    \_\_|  \_\\_____|______|______|
    """
    message = "🤖 Bot NG | Server Status ist online! 🚀\nEntwickelt von #pmarcelq"
    
    # Den ASCII-Banner mit roter Farbe ausgeben und den Sneakers-Effekt darauf anwenden
    sys.stdout.write("\r\033[91m")  # Rot für den Banner
    sneakers_effect(banner, speed=0.01, color_code="\033[91m")  # Banner entschlüsseln mit Farbe
    sys.stdout.write("\033[0m")  # Reset der Farben nach dem Effekt
    
    # Nachricht in Lila für "🤖 Bot NG | Server Status ist online!" und dann den Sneakers-Effekt anwenden
    sys.stdout.write("\033[35m")  # Lila für die Nachricht
    sneakers_effect(message.split("\n")[0], speed=0.01, color_code="\033[35m")  # Entschlüsselung der ersten Zeile
    sys.stdout.write("\033[0m")  # Reset der Farben nach der Nachricht
    
    # Die zweite Zeile der Nachricht in Regenbogenfarben mit Sneakers-Effekt ausgeben
    rainbow_msg = rainbow_text(message.split("\n")[1])  # Rest der Nachricht im Regenbogen
    sneakers_effect(rainbow_msg, speed=0.01)  # Entschlüsseln mit dem Effekt
    
    try:
        # Synchronisiere alle Slash-Commands mit Discord
        await bot.tree.sync()
        print("\033[32m")
        print("✅ Slash-Commands wurden global synchronisiert.")
        print("\033[0m")
    except Exception as e:
        print("\033[91m")
        print(f"❌ Fehler beim Synchronisieren: {e}")
        print("\033[0m")

# Slash-Command für den Serverstatus
@bot.tree.command(name="status", description="Zeigt den Status des Nova-Servers")
async def status(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    server_online = is_server_online(GMOD_SERVER_IP, GMOD_SERVER_PORT)
    player_count = get_player_count(GMOD_SERVER_IP, GMOD_SERVER_PORT) if server_online else 0
    embed = discord.Embed(
        title="🎮 Nova-Gaming.eu Server Status",
        color=discord.Color.green() if server_online else discord.Color.red(),
        description="**Status:** " + ("🟢 Online" if server_online else "🔴 Offline"),
    )
    embed.add_field(name="🌐 Server IP", value=f"{GMOD_SERVER_IP}:{GMOD_SERVER_PORT}", inline=False)
    embed.add_field(name="👥 Spieleranzahl", value=f"{player_count} Spieler" if server_online else "Keine Spieler", inline=False)
    embed.set_footer(text=f"🕒 Abgefragt am {time.strftime('%d.%m.%Y %H:%M:%S')}")
    await interaction.followup.send(embed=embed)

# Slash-Command für die Spieler-Namen
@bot.tree.command(name="name", description="Zeigt die Namen der Spieler auf dem Server")
async def name(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    players = get_player_names(GMOD_SERVER_IP, GMOD_SERVER_PORT)
    if players:
        player_list = "\n".join(players)
        await interaction.followup.send(f"🎮 **Spieler auf dem Server:**\n{player_list}")
    else:
        await interaction.followup.send("🚫 Keine Spieler online oder Abruf fehlgeschlagen.")

bot.run('MTM0NjU3MzcyNDYzNTIzODQyMA.G1hS72.u9L5xSuN8aMDizZuaQ5Mz5W94siLEt1DyXzo4U')
