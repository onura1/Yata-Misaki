# Yata Misaki/commands/restart.py

import discord
from discord.ext import commands
import os
import sys

# Sınıf adı RestartCog olarak değiştirildi
class RestartCog(commands.Cog, name="Yeniden Başlatma"):
    """Botu yeniden başlatma komutunu içerir."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- Yeniden Başlatma Komutu ---
    @commands.command(name="restart", aliases=["reboot"])
    @commands.is_owner()
    async def restart(self, ctx: commands.Context):
        """Botu yeniden başlatır (Sadece sahip kullanabilir)."""
        try:
            await ctx.message.add_reaction("🔄")
            await ctx.send("Bot yeniden başlatılıyor...")
            print("Bot yeniden başlatılıyor...")
            os.execv(sys.executable, ['python'] + sys.argv)
        except discord.Forbidden:
             await ctx.send("Tepki ekleme iznim yok ama yeniden başlatıyorum.")
             os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            await ctx.send(f"Yeniden başlatma sırasında bir hata oluştu: {e}")
            print(f"Yeniden başlatma hatası: {e}")

    # --- Komut Hatalarını Yakalama ---
    @restart.error
    async def restart_error(self, ctx: commands.Context, error):
         if isinstance(error, commands.NotOwner):
            await ctx.send("❌ Bu komutu sadece bot sahibi kullanabilir!")
         else:
            print(f"'restart' komutunda beklenmedik hata: {error}")


# Cog'u bota tanıtmak için gerekli setup fonksiyonu
async def setup(bot: commands.Bot):
    # Eklenecek Cog adı RestartCog olarak güncellendi
    await bot.add_cog(RestartCog(bot))
    # Yüklendi mesajı güncellendi
    print("✅ Restart Cog yüklendi!")