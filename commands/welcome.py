# Yata Misaki/commands/welcome.py

import discord
from discord.ext import commands

class WelcomeCog(commands.Cog):
    """Yeni üyelere hoş geldin mesajı gönderen Cog."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Config ayarlarına self.bot.config üzerinden erişeceğiz

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Bir üye sunucuya katıldığında tetiklenir."""

        # Ayarlardan hoş geldin kanalının ID'sini al
        welcome_channel_id = self.bot.config.get("WELCOME_CHANNEL_ID")
        if not welcome_channel_id:
            print("Hata: Yapılandırmada WELCOME_CHANNEL_ID bulunamadı.")
            return

        # Kanal nesnesini ID ile bul
        kanal = self.bot.get_channel(int(welcome_channel_id)) # ID'yi integer yapalım

        if kanal:
            sunucu = member.guild
            uye_sayisi = sunucu.member_count # member_count zaten integer döner

            # Mesaj içeriğini ayarlardan alarak oluştur
            # (Not: Embed içeriğindeki kanal ID'lerini de config'den almak en iyisidir)
            rules_ch_id = self.bot.config.get("RULES_CHANNEL_ID", "#")
            color_role_ch_id = self.bot.config.get("COLOR_ROLE_CHANNEL_ID", "#")
            general_roles_ch_id = self.bot.config.get("GENERAL_ROLES_CHANNEL_ID", "#")
            events_ch_id = self.bot.config.get("EVENTS_CHANNEL_ID", "#")
            giveaways_ch_id = self.bot.config.get("GIVEAWAYS_CHANNEL_ID", "#")
            partnership_rules_ch_id = self.bot.config.get("PARTNERSHIP_RULES_CHANNEL_ID", "#")

            desc = (
                f"Hoş geldin! Kuralları okumayı unutma <#{rules_ch_id}>.\n"
                f"Kendine bir renk rolü al <#{color_role_ch_id}>.\n"
                f"Rollerimizden uygun olanları almayı unutma <#{general_roles_ch_id}>.\n"
                f"Etkinliklerimize göz at, belki eğlenirsin <#{events_ch_id}>.\n"
                f"Çekilişlerimize katılmayı unutma <#{giveaways_ch_id}>.\n"
                f"Partnerlik şartlarını oku <#{partnership_rules_ch_id}>."
            )

            embed = discord.Embed(
                description=desc,
                color=discord.Color.red() # Rengi de config'e ekleyebilirsiniz
            )

            embed.set_footer(text=f"👥 Şu anda sunucumuzda toplam {uye_sayisi} üye bulunuyor!")

            # Resim URL'sini config'den al
            welcome_image_url = self.bot.config.get("WELCOME_IMAGE_URL", "")
            if welcome_image_url:
                embed.set_image(url=welcome_image_url)

            try:
                await kanal.send(content=f" Heyy {member.mention}! Yooo! Sen Hoş geldin!", embed=embed)
            except discord.Forbidden:
                print(f"Hata: {kanal.name} kanalına mesaj gönderme izni yok.")
            except discord.HTTPException as e:
                print(f"Hoş geldin mesajı gönderilirken bir HTTP hatası oluştu: {e}")
        else:
            print(f"Hata: Hoş geldin kanalı (ID: {welcome_channel_id}) bulunamadı.")

# Cog'u bota tanıtmak için gerekli setup fonksiyonu
async def setup(bot: commands.Bot):
    # WelcomeCog sınıfından bir örnek oluşturup bota ekliyoruz
    await bot.add_cog(WelcomeCog(bot))
    print("✅ Welcome Cog yüklendi!") # Yüklendiğine dair konsola mesaj yazdırabiliriz