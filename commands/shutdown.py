# Yata Misaki/commands/shutdown.py

import discord
from discord.ext import commands
import asyncio # await bot.close() için gerekli

class ShutdownCog(commands.Cog, name="Kapatma"):
    """Botu güvenli bir şekilde kapatma komutunu içerir."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Sadece kapatma işlevi gören komut
    @commands.command(name="kapat")
    @commands.is_owner() # Sadece bot sahibi kullanabilir
    async def shutdown(self, ctx: commands.Context):
        """Botu güvenli bir şekilde kapatır (Sadece sahip kullanabilir)."""
        try:
            await ctx.message.add_reaction("🛑") # Kapatma emojisi
            await ctx.send("Bot kapatılıyor... Hoşçakal!") # Kapatma mesajı
            print(f"Bot kapatma komutu {ctx.author} tarafından kullanıldı.")
            # Kapatma işlemi:
            await self.bot.close()
        except discord.Forbidden:
             await ctx.send("Tepki ekleme iznim yok ama kapatıyorum.")
             await self.bot.close()
        except Exception as e:
            await ctx.send(f"Kapatma sırasında bir hata oluştu: {e}")
            print(f"Kapatma hatası: {e}")

    # Bu komuta özel hata yakalama
    @shutdown.error
    async def shutdown_error(self, ctx: commands.Context, error):
         if isinstance(error, commands.NotOwner):
            await ctx.send("❌ Bu komutu sadece bot sahibi kullanabilir!")
         else:
             print(f"'kapat' komutunda beklenmedik hata: {error}")


# Cog'u bota tanıtmak için gerekli setup fonksiyonu
async def setup(bot: commands.Bot):
    await bot.add_cog(ShutdownCog(bot))
    print("✅ Shutdown Cog (Kapat) yüklendi!")