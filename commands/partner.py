# Yata Misaki/commands/partner.py

import discord
from discord.ext import commands
import re
from datetime import datetime
import json # Partnerlik sayılarını dosyaya kaydetmek/yüklemek için
import os   # Dosya varlığını kontrol etmek için

# Partnerlik verilerinin saklanacağı dosyanın adı
PARTNER_DATA_FILE = "partner_data.json"

class PartnershipCog(commands.Cog):
    """Partnerlik ile ilgili komutları ve olayları yönetir."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Bot başladığında partnerlik verilerini dosyadan yükle
        self.partner_counts = self._load_partner_data()
        # Config ayarlarına self.bot.config üzerinden erişeceğiz

    # Alt çizgi (_) ile başlayan metodlar genellikle sınıfın iç kullanımı içindir
    def _load_partner_data(self) -> dict[int, int]:
        """Partnerlik verilerini JSON dosyasından yükler."""
        if os.path.exists(PARTNER_DATA_FILE):
            try:
                with open(PARTNER_DATA_FILE, 'r', encoding='utf-8') as f:
                    # JSON'dan yüklerken anahtarlar (kullanıcı ID'leri) string olur,
                    # bunları integer'a çevirerek sözlüğe ekleyelim.
                    data = json.load(f)
                    # Sözlük oluşturucu (dictionary comprehension) ile dönüşüm
                    return {int(k): v for k, v in data.items()}
            except (json.JSONDecodeError, IOError, ValueError) as e:
                # ValueError: int'e çevirme hatası olursa
                print(f"[Hata] {PARTNER_DATA_FILE} yüklenemedi veya bozuk. Yeni veri oluşturuluyor. Hata: {e}")
                return {} # Hata durumunda boş sözlükle başla
        return {} # Dosya yoksa boş sözlükle başla

    def _save_partner_data(self):
        """Partnerlik verilerini JSON dosyasına kaydeder."""
        try:
            # Kaydederken anahtarlar (integer ID'ler) otomatik olarak string'e çevrilir JSON standardı gereği.
            with open(PARTNER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.partner_counts, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"[Hata] {PARTNER_DATA_FILE} kaydedilemedi. Hata: {e}")
        except Exception as e:
             print(f"[Hata] Partner verileri kaydedilirken beklenmedik bir sorun oluştu: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Partner kanalındaki linkleri tespit eder ve sayacı günceller."""

        # Bot mesajlarını veya DM'leri yoksay
        if message.author.bot or message.guild is None:
            return

        # Ayarlardan partner kanalının ID'sini al
        partner_channel_id = self.bot.config.get("PARTNER_CHANNEL_ID")
        if not partner_channel_id:
            # Hata mesajını sadece bir kere veya belirli aralıklarla yazdırmak daha iyi olabilir
            # print("[Hata] Yapılandırmada PARTNER_CHANNEL_ID bulunamadı.")
            return

        # Sadece belirlenen partner kanalındaki mesajları işle
        if message.channel.id != int(partner_channel_id):
             return

        # Mesajda link var mı kontrol et (basit kontrol)
        # Daha gelişmiş kontrol gerekebilir (örn. sadece discord davet linkleri vb.)
        if re.search(r"https?://", message.content):
            now = datetime.utcnow()
            user_id = message.author.id

            # Partner sayısını artır ve dosyayı güncelle
            self.partner_counts[user_id] = self.partner_counts.get(user_id, 0) + 1
            user_total_partners = self.partner_counts[user_id]
            self._save_partner_data() # Değişikliği dosyaya kaydet

            # Bildirim embed'ini oluştur
            embed = discord.Embed(
                title="🎯 Yeni bir partnerlik bildirimi!",
                color=discord.Color.red(), # Rengi config'den alabiliriz
                timestamp=now
            )
            # Partnerlik resmini config'den al
            partner_image_url = self.bot.config.get("PARTNER_IMAGE_URL", "")
            if partner_image_url:
                embed.set_image(url=partner_image_url)

            embed.add_field(
                name=f"👤 Partnerliği yapan: {message.author.display_name}", # İsim yeterli olabilir
                value=(f"✨ Bu kullanıcının toplam partnerlik sayısı: **{user_total_partners}**"),
                inline=False
            )
            embed.set_footer(text=f"ID: {user_id}") # Kullanıcı ID'sini ekleyebiliriz

            try:
                # Bildirimi aynı kanala gönder
                await message.channel.send(embed=embed)
                # İsteğe bağlı: Orijinal mesaja tepki ekle
                await message.add_reaction("🤝")
            except discord.Forbidden:
                print(f"[Hata] {message.channel.name} kanalına mesaj gönderme veya tepki ekleme izni yok.")
            except discord.HTTPException as e:
                print(f"Partnerlik bildirimi gönderilirken bir HTTP hatası oluştu: {e}")

            # Bu listener sadece bu kanal ve link içeren mesajlar içindi.
            # Komutların işlenmesini engellemez (main.py'daki on_message halleder)

    @commands.command(name="partnersayim", aliases=["psay", "partnerliklerim"])
    @commands.cooldown(1, 5, commands.BucketType.user) # Komutun kötüye kullanımını engellemek için bekleme süresi
    async def partner_sayim(self, ctx: commands.Context, member: discord.Member = None):
        """
        Belirtilen üyenin veya komutu kullananın yaptığı toplam partnerlik sayısını gösterir.
        Kullanım: y!partnersayim [@Kullanıcı]
        """
        # Eğer komutta bir üye etiketlenmediyse, komutu yazanı hedef al
        target_member = member or ctx.author

        # Hedef üyenin partnerlik sayısını verilerden al (eğer yoksa 0)
        count = self.partner_counts.get(target_member.id, 0)

        await ctx.send(f"📊 **{target_member.display_name}** kullanıcısının yaptığı toplam partnerlik sayısı: **{count}**")

    @partner_sayim.error
    async def partner_sayim_error(self, ctx: commands.Context, error):
        """partner_sayim komutundaki hataları yakalar."""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Bu komutu tekrar kullanmak için lütfen {error.retry_after:.1f} saniye bekleyin.", delete_after=5)
        elif isinstance(error, commands.MemberNotFound):
             await ctx.send(f"❌ Belirtilen üye bulunamadı: `{error.argument}`")
        else:
            print(f"partner_sayim komutunda hata: {error}")
            await ctx.send("❓ Komutu kullanırken bir hata oluştu.")


# Cog'u bota tanıtmak için gerekli setup fonksiyonu
async def setup(bot: commands.Bot):
    # PartnershipCog sınıfından bir örnek oluşturup bota ekliyoruz
    await bot.add_cog(PartnershipCog(bot))
    print("✅ Partnership Cog yüklendi!")
