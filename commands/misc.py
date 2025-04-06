# Yata Misaki/commands/misc.py (Uptime Düzeltmesi Dahil)

import discord
from discord.ext import commands
import time
import datetime # <-- ÖNEMLİ: Modülün tamamı import ediliyor

class MiscCog(commands.Cog, name="Çeşitli"):
    """Çeşitli genel komutları ve yardım menüsünü içerir."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Cog yüklendiğinde başlangıç zamanını kaydet
        self.start_time = time.time()

    @commands.command(name="ping", aliases=["gecikme"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def ping(self, ctx: commands.Context):
        """Botun Discord API'sine olan gecikmesini gösterir."""
        start = time.monotonic()
        msg = await ctx.send("🏓 Pong!")
        end = time.monotonic()
        websocket_latency = self.bot.latency * 1000
        roundtrip_latency = (end - start) * 1000
        await msg.edit(content=f"🏓 Pong!\n"
                               f"🔹 WebSocket Gecikmesi: **{websocket_latency:.2f}ms**\n"
                               f"🔸 Mesaj Gecikmesi: **{roundtrip_latency:.2f}ms**")

    @commands.command(name="uptime", aliases=["aktiflik"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def uptime(self, ctx: commands.Context):
        """Botun ne kadar süredir aktif olduğunu gösterir."""
        # Şu anki zamanı al
        current_time = time.time()
        # Başlangıç zamanı ile farkı saniye cinsinden hesapla
        difference = int(round(current_time - self.start_time))
        # Saniye farkını "Gün, Saat:Dakika:Saniye" formatına çevir
        # ÖNEMLİ: datetime.timedelta olarak kullanılıyor
        try:
             text = str(datetime.timedelta(seconds=difference))
             await ctx.send(f"⏳ Bot **{text}** süredir aktif.")
        except Exception as e:
             # Hesaplama veya gönderme sırasında bir hata olursa yakala
             print(f"Uptime komutunda timedelta hatası veya gönderme hatası: {e}")
             await ctx.send("Uptime hesaplanırken bir sorun oluştu.")


    # --- YARDIM KOMUTU ---
    @commands.command(name="help", aliases=["yardim", "komutlar"])
    async def help_command(self, ctx: commands.Context):
        """Tüm kullanılabilir komutları listeler."""
        prefix = self.bot.config.get("PREFIX", "y!")
        embed = discord.Embed(
            title="Yardım Menüsü",
            description=f"Aşağıda kullanabileceğin komutların bir listesi bulunmaktadır.\nPrefix: `{prefix}`",
            color=discord.Color.blue()
        )
        # ... (Help komutunun geri kalanı aynı) ...
        commands_by_cog = {}
        for command in self.bot.commands:
            if command.hidden: continue
            try:
                if not await command.can_run(ctx): continue
            except commands.CommandError: continue

            cog_name = command.cog_name or "Diğer"
            if cog_name not in commands_by_cog: commands_by_cog[cog_name] = []
            commands_by_cog[cog_name].append(f"`{prefix}{command.name}`")

        if not commands_by_cog:
            embed.description += "\n\nGörünüşe göre çalıştırabileceğin bir komut bulunmuyor."
        else:
            sorted_cogs = sorted(commands_by_cog.items())
            for cog_name, command_list in sorted_cogs:
                commands_str = "\n".join(command_list)
                if commands_str:
                    embed.add_field(name=f"**{cog_name}**", value=commands_str, inline=False)

        embed.set_footer(text=f"{ctx.guild.name if ctx.guild else 'DM'} | {self.bot.user.name}")
        embed.timestamp = discord.utils.utcnow()

        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Yardım mesajı gönderilemedi (çok fazla komut olabilir).")


    # --- Hata Yönetimi ---
    @ping.error
    @uptime.error
    @help_command.error
    async def misc_command_error(self, ctx: commands.Context, error):
         if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Bu komutu tekrar kullanmak için lütfen {error.retry_after:.1f} saniye bekleyin.", delete_after=5)
         else:
            print(f"Misc komutunda hata ({ctx.command.name}): {error}")
            await ctx.send(f"❓ Komut işlenirken bir hata oluştu. Detaylar loglarda.")


# Cog'u bota tanıtmak için gerekli setup fonksiyonu
async def setup(bot: commands.Bot):
    await bot.add_cog(MiscCog(bot))
    print("✅ Misc Cog (Ping, Uptime, Help) yüklendi!")