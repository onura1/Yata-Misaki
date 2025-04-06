# Yata Misaki/main.py (Logging Eklenmiş Sürüm)

# ----- Gerekli Kütüphaneler -----
import discord
from discord.ext import commands
import os
import asyncio
import logging # <-- Logging için eklendi
import logging.handlers # <-- Dosya rotasyonu için eklendi
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# ----- Logging Ayarları -----
# Bu kısım dosyanın başında, diğer işlemlerden önce ayarlanmalı
log_file_name = 'yata_misaki.log'
log_level = logging.INFO # Hangi seviyedeki logların tutulacağı (INFO, DEBUG, WARNING, ERROR, CRITICAL)

# Logger nesnesini al (root logger'ı kullanabiliriz)
logger = logging.getLogger() # Root logger'ı alıyoruz, discord.py de bunu kullanacak
logger.setLevel(log_level)

# Log formatını belirle
log_format = logging.Formatter('%(asctime)s [%(levelname)-8s] %(name)-15s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Konsol Handler (Çıktıyı konsola/terminale yazdırır)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# Dönen Dosya Handler (Logları dosyaya yazar ve boyutunu yönetir)
# maxBytes: Dosyanın maksimum boyutu (örn: 5MB), backupCount: Kaç tane yedek dosya tutulacağı
rotating_file_handler = logging.handlers.RotatingFileHandler(
    filename=log_file_name,
    encoding='utf-8',
    maxBytes=5 * 1024 * 1024, # 5 MB
    backupCount=3 # Eski loglardan 3 tane tut (yata_misaki.log.1, .2, .3)
)
rotating_file_handler.setFormatter(log_format)
logger.addHandler(rotating_file_handler)

# ----- .env dosyasını yükle -----
load_dotenv()
logger.info(".env dosyası yüklendi (eğer varsa).") # print yerine logger

# ----- Yapılandırma (CONFIG) -----
CONFIG = {
    "BOT_TOKEN": os.getenv("DISCORD_TOKEN"),
    "PREFIX": "y!",
    # ... (Diğer CONFIG ayarların) ...
     "WELCOME_CHANNEL_ID": 1110239331953672373,
    "PARTNER_CHANNEL_ID": 1110970304773247057,
    "RULES_CHANNEL_ID": 1110236874775207996,
    "COLOR_ROLE_CHANNEL_ID": 1231563961695207494,
    "GENERAL_ROLES_CHANNEL_ID": 1231563981186007141,
    "EVENTS_CHANNEL_ID": 1110237174739247195,
    "GIVEAWAYS_CHANNEL_ID": 1110237208264327169,
    "PARTNERSHIP_RULES_CHANNEL_ID": 1357997075874447570,
    "WELCOME_IMAGE_URL": "https://cdn.discordapp.com/attachments/1279807720534311045/1358023330044575924/k-anime-fall.gif",
    "PARTNER_IMAGE_URL": "https://cdn.discordapp.com/attachments/1279807720534311045/1358023632877785128/yata-misaki-k-project.gif",
}
logger.info("Yapılandırma (CONFIG) sözlüğü oluşturuldu.")

# ----- Discord Bot Ayarları (Intents) -----
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
logger.info("Discord Intent'leri ayarlandı.")

# ----- Bot Nesnesini Oluşturma -----
bot = commands.Bot(
    command_prefix=CONFIG["PREFIX"],
    intents=intents,
    help_command=None,
    case_insensitive=True
)
bot.config = CONFIG
logger.info("Discord Bot nesnesi oluşturuldu.")

# ----- Botu Ayakta Tutma (Keep Alive - Flask) -----
app = Flask('')
@app.route('/')
def home(): return "Yata Misaki Bot Aktif!"
def run_flask():
    port = int(os.environ.get('PORT', 8080))
    # Flask'ın kendi loglarını biraz kısalım (isteğe bağlı)
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.WARNING)
    app.run(host='0.0.0.0', port=port)
def keep_alive():
    logger.info("Keep-alive sunucusu başlatılıyor...")
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()
    logger.info(f"Keep-alive sunucusu {os.environ.get('PORT', 8080)} portunda başlatıldı.")

# ----- Temel Bot Olayları -----
@bot.event
async def on_ready():
    """Bot başarıyla Discord'a bağlandığında çalışır."""
    logger.info("-" * 30)
    logger.info(f'Bot olarak giriş yapıldı: {bot.user.name} (ID: {bot.user.id})')
    logger.info(f'Discord.py Sürümü: {discord.__version__}')
    logger.info(f'{len(bot.guilds)} sunucuda aktif.')
    logger.info(f"Yüklü Cog'lar: {', '.join(bot.cogs.keys()) if bot.cogs else 'Yok'}")
    logger.info("-" * 30)
    try:
        await bot.change_presence(activity=discord.Game(name=f"{CONFIG['PREFIX']}help | Yata Misaki"))
        logger.info("Bot durumu ayarlandı.")
    except Exception as e:
        logger.error(f"Bot durumu ayarlanırken hata oluştu: {e}")


@bot.event
async def on_message(message):
    """Gelen her mesajda çalışır."""
    if message.author.bot:
        return
    # Normalde her mesajı loglamak çok fazla olabilir, sadece komutları loglayabiliriz.
    # logger.debug(f"Mesaj alındı: {message.author}: {message.content}")
    await bot.process_commands(message)

# Genel komut hatası yakalayıcı (isteğe bağlı ama faydalı)
@bot.event
async def on_command_error(ctx: commands.Context, error):
    """İşlenmemiş komut hatalarını yakalar."""
    # Eğer hata bir Cog içindeki özel error handler tarafından zaten işlendiyse, tekrar işlemeyelim
    if hasattr(ctx.command, 'on_error'):
        return

    # Bilinen hata türlerini daha kullanıcı dostu yönetebiliriz
    if isinstance(error, commands.CommandNotFound):
        logger.warning(f"Bilinmeyen komut denendi: {ctx.message.content} ({ctx.author})")
        # Kullanıcıya mesaj göndermeyebiliriz veya "Komut bulunamadı" diyebiliriz.
        # await ctx.send(f"❓ `{ctx.invoked_with}` adında bir komut bulunamadı.", delete_after=10)
        pass # Şimdilik bir şey yapma
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Bu komutu tekrar kullanmak için lütfen {error.retry_after:.1f} saniye bekleyin.", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        logger.warning(f"'{ctx.command.name}' komutunda eksik argüman: {error.param.name} ({ctx.author})")
        await ctx.send(f"❌ Eksik argüman: `{error.param.name}`. Kullanım: `{CONFIG['PREFIX']}{ctx.command.qualified_name} {ctx.command.signature}`")
    elif isinstance(error, commands.CheckFailure): # Genel yetki hatası (is_owner, has_permissions vb.)
        logger.warning(f"Yetkisiz komut denemesi: {ctx.command.name} ({ctx.author})")
        await ctx.send("❌ Bu komutu kullanma izniniz yok!")
    elif isinstance(error, commands.CommandInvokeError):
         # Komutun *içinde* bir hata oluştuğunda tetiklenir
         original_error = error.original
         logger.error(f"'{ctx.command.name}' komutu çalıştırılırken hata oluştu: {original_error.__class__.__name__}: {original_error}")
         # Traceback'i de loglamak için logger.exception kullanabiliriz:
         # logger.exception(f"'{ctx.command.name}' komutunda hata:")
         await ctx.send(" Komut işlenirken bir hata oluştu. Geliştirici bilgilendirildi.") # Kullanıcıya genel mesaj
    else:
        # Bilinmeyen/işlenmemiş diğer hatalar
        logger.error(f"İşlenmemiş bir komut hatası oluştu ({ctx.command.name if ctx.command else 'Bilinmiyor'}): {error}")


# ----- Cog'ları Yükleme Fonksiyonu -----
async def load_extensions():
    """commands klasöründeki tüm Cog'ları yükler."""
    logger.info("-" * 30)
    logger.info("Cog'lar yükleniyor...")
    loaded_cogs = 0
    cog_count = 0
    commands_dir = './commands'
    if not os.path.exists(commands_dir) or not os.path.isdir(commands_dir):
        logger.error(f"'{commands_dir}' klasörü bulunamadı!")
        logger.info("-" * 30)
        return

    for filename in os.listdir(commands_dir):
        if filename.endswith('.py') and os.path.isfile(os.path.join(commands_dir, filename)):
            cog_count += 1
            extension_name = f'commands.{filename[:-3]}'
            try:
                await bot.load_extension(extension_name)
                # Başarı logunu Cog'un kendi setup fonksiyonu yazdırıyor zaten
                # logger.info(f"{extension_name} başarıyla yüklendi.") # İstersen açabilirsin
                loaded_cogs += 1
            except Exception as e:
                # Hata logunu Cog'un setup fonksiyonu veya burası yazdırabilir
                logger.exception(f'{extension_name} yüklenirken sorun oluştu:') # Exception ile traceback loglanır
                # print(f'[HATA] {extension_name} yüklenirken sorun: {type(e).__name__}: {e}') # Eski print

    logger.info(f"{loaded_cogs}/{cog_count} Cog yüklendi.")
    logger.info("-" * 30)

# ----- Botu Başlatma -----
async def main():
    """Ana bot başlatma ve çalıştırma fonksiyonu."""
    logger.info("Bot başlatma süreci başlıyor...")
    bot_token = bot.config.get("BOT_TOKEN")
    if not bot_token:
        logger.critical("DISCORD_TOKEN ortam değişkeni bulunamadı! Bot başlatılamıyor.")
        return

    keep_alive() # Keep Alive'ı başlat

    async with bot:
        await load_extensions()
        logger.info("Bot Discord'a bağlanıyor...")
        await bot.start(bot_token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot manuel olarak kapatıldı (KeyboardInterrupt).")
    except discord.LoginFailure:
        logger.critical("Geçersiz Discord Token! Bot başlatılamadı.")
    except discord.PrivilegedIntentsRequired:
         logger.critical("Gerekli Intent'ler (Members/Message Content) Discord Developer Portal'da etkin değil!")
    except Exception as e:
        # Diğer tüm beklenmedik hataları logla
        logger.critical(f"Bot başlatılırken veya çalışırken yakalanamayan ana hata!", exc_info=True) # exc_info=True traceback'i ekler