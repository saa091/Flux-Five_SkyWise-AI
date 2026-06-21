"""
Migration: seed Tips Cuaca + Galeri foto dengan gambar dari Unsplash (CDN publik, no-login).
Gambar diunduh saat migrate dan disimpan ke media/galeri/.
"""
import os
import urllib.request
from django.db import migrations
from django.conf import settings

# ── DATA TIPS ────────────────────────────────────────────────────────────────

TIPS_DATA = [
    # (judul, isi, nama_kategori)
    (
        "Tips Aman Berkendara Saat Hujan Lebat",
        """Hujan lebat bisa sangat berbahaya bagi pengemudi. Berikut langkah-langkah yang wajib kamu ikuti:

1. **Kurangi kecepatan** — jarak pengereman bisa 2x lebih panjang di jalan basah.
2. **Nyalakan lampu utama** — bukan lampu hazard! Lampu hazard membingungkan pengendara lain.
3. **Jaga jarak aman** — minimal 3 detik dari kendaraan di depan.
4. **Hindari genangan dalam** — kamu tidak tahu seberapa dalam air tersebut.
5. **Waspadai aquaplaning** — jika ban kehilangan traksi, lepaskan gas perlahan tanpa mengerem keras.
6. **Periksa kondisi wiper** — wiper yang aus sangat berbahaya di hujan deras.

Ingat: tidak ada yang lebih penting dari keselamatan. Jika hujan terlalu lebat, tepilah dan tunggu hingga reda.""",
        "Hujan"
    ),
    (
        "Cara Melindungi Diri dari Paparan Sinar UV Ekstrem",
        """Saat cuaca cerah dengan indeks UV tinggi (6+), kulit bisa terbakar hanya dalam 15 menit. Ikuti panduan ini:

1. **Gunakan tabir surya SPF 30+** — oleskan 30 menit sebelum keluar, ulangi setiap 2 jam.
2. **Hindari paparan langsung pukul 10.00–14.00** — ini adalah jam puncak sinar UV.
3. **Kenakan pakaian pelindung** — kemeja lengan panjang berbahan ringan, topi bertepi lebar, dan kacamata UV400.
4. **Cari tempat teduh** — pohon, payung, atau atap dapat mengurangi paparan UV hingga 50%.
5. **Perbanyak minum air** — minimal 8 gelas sehari, lebih banyak jika berolahraga di luar.
6. **Lindungi bibir** — gunakan lip balm dengan SPF.

Perhatian khusus untuk anak-anak dan lansia yang lebih rentan terhadap heat stroke.""",
        "Cerah"
    ),
    (
        "Langkah Evakuasi Diri Saat Badai Petir",
        """Badai petir adalah fenomena cuaca paling mematikan. Ikuti protokol keselamatan berikut:

**Jika di dalam ruangan:**
- Tutup semua jendela dan pintu.
- Jauhi jendela, pipa ledeng, dan peralatan listrik.
- Cabut colokan perangkat elektronik.
- Hindari mandi atau mencuci tangan selama badai.

**Jika di luar ruangan:**
- Segera cari perlindungan di gedung tertutup atau kendaraan bermetal.
- Jauhi pohon tinggi, tiang listrik, dan benda logam.
- Jika tidak ada tempat berlindung: jongkok di area rendah, jangan berbaring.
- Jauhi badan air (sungai, danau, kolam renang).
- Tunggu 30 menit setelah petir terakhir sebelum keluar lagi.

Ingat: aturan "30-30" — jika jarak antara kilat dan guntur < 30 detik, segera masuk; tunggu 30 menit setelah terakhir kali melihat kilat.""",
        "Badai"
    ),
    (
        "Menjaga Kesehatan Saat Musim Hujan: Panduan Lengkap",
        """Musim hujan meningkatkan risiko berbagai penyakit. Lindungi diri dengan cara berikut:

**Cegah penyakit pernapasan:**
- Gunakan masker saat keluar di udara lembap.
- Jaga sirkulasi udara dalam ruangan.
- Konsumsi vitamin C dan zinc untuk daya tahan tubuh.

**Cegah penyakit kulit:**
- Keringkan tubuh dan kaki setelah terkena hujan.
- Ganti pakaian basah sesegera mungkin.
- Gunakan alas kaki tertutup untuk menghindari kutu air.

**Cegah demam berdarah:**
- Kuras tempat penampungan air setiap 3 hari.
- Tutup tempat air dengan rapat.
- Gunakan lotion anti-nyamuk terutama saat sore hari.

**Konsumsi makanan bergizi:**
- Sup hangat, jahe, dan rempah-rempah membantu melawan infeksi.
- Hindari makanan mentah yang berisiko terkontaminasi.""",
        "Hujan"
    ),
    (
        "Aktivitas Outdoor Terbaik Saat Cuaca Cerah Berawan",
        """Cuaca cerah berawan adalah kondisi IDEAL untuk aktivitas luar ruangan. Tidak terlalu panas, tidak berhujan. Manfaatkan dengan:

**Olahraga Pagi (06.00–09.00):**
- Jogging atau bersepeda di taman kota.
- Yoga atau senam di teras/halaman.
- Renang (perhatikan arah awan).

**Aktivitas Siang (09.00–15.00):**
- Piknik keluarga di taman.
- Hiking jalur pendek di pegunungan lokal.
- Fotografi alam — cahaya diffuse sempurna untuk foto!
- Bermain layang-layang di lapangan terbuka.

**Aktivitas Sore (15.00–17.30):**
- Bersepeda santai menikmati pemandangan.
- Olahraga tim: voli, futsal, badminton outdoor.
- Berkunjung ke kebun binatang atau taman botani.

Tips: Selalu bawa air minum dan sunscreen meskipun langit berawan — UV tetap menembus awan tipis.""",
        "Berawan"
    ),
    (
        "Panduan Berkemah Aman di Segala Cuaca",
        """Camping bisa menjadi pengalaman luar biasa jika kamu tahu cara menghadapi perubahan cuaca:

**Persiapan Sebelum Berangkat:**
- Cek prakiraan cuaca 3 hari ke depan via SkyWise AI.
- Bawa tenda tahan air dengan rating waterproof minimal 3000mm.
- Siapkan pakaian berlapis (base layer, mid layer, outer layer).
- Bawa sleeping bag sesuai rating suhu terendah di lokasi.

**Di Lokasi Camping:**
- Pilih area yang tidak berada di lembah (risiko banjir) atau puncak (risiko petir).
- Dirikan tenda membelakangi angin dominan.
- Pastikan tali pengikat tenda kuat untuk menghadapi angin kencang.

**Saat Cuaca Memburuk:**
- Masuk tenda segera saat ada tanda badai.
- Simpan perlengkapan berharga dalam tas tahan air.
- Jangan masak di dalam tenda — risiko kebakaran dan keracunan CO.

Ingat: gunung di Indonesia cuacanya bisa berubah drastis dalam 30 menit.""",
        "Berawan"
    ),
    (
        "Cara Membaca Awan untuk Memprediksi Cuaca",
        """Nenek moyang kita sudah membaca awan jauh sebelum ada teknologi. Pelajari caranya:

**Awan Tanda Cuaca Baik:**
- ☁️ **Cumulus kecil** — awan putih bergelembung di langit biru, cuaca stabil.
- 🌤️ **Cirrus tipis** — serat putih tinggi di langit, cuaca masih cerah 12-24 jam.

**Awan Tanda Hujan Akan Datang:**
- ☁️ **Nimbostratus** — lapisan abu-abu tebal dan gelap yang menutupi seluruh langit.
- 🌩️ **Cumulonimbus** — awan menjulang seperti jamur/landasan terbang, BAHAYA: badai petir.
- 🌫️ **Stratus rendah** — kabut rendah yang tebal, biasanya gerimis.

**Awan Tanda Cuaca Akan Memburuk:**
- Jika awan Cumulus terus tumbuh ke atas sepanjang siang → kemungkinan badai sore.
- Langit berwarna kuning/kemerahan yang tidak biasa saat siang → cuaca ekstrem mendekat.

Tips praktis: Jika kamu di Kalimantan/Sumatra, awan Cumulonimbus sering muncul mulai pukul 13.00. Pantau terus!""",
        "Berawan"
    ),
    (
        "Pertolongan Pertama Saat Heat Stroke (Serangan Panas)",
        """Heat stroke adalah kondisi darurat medis akibat kepanasan ekstrem. Kenali dan tangani dengan cepat:

**Gejala Heat Stroke:**
- Suhu tubuh > 40°C
- Kulit merah, panas, dan kering (bukan berkeringat)
- Kebingungan, bicara tidak jelas, atau tidak sadar
- Denyut nadi cepat dan lemah
- Mual atau muntah

**Langkah Pertolongan Pertama:**
1. Segera HUBUNGI 119 (darurat medis).
2. Pindahkan korban ke tempat teduh dan sejuk.
3. Lepaskan pakaian berlebihan.
4. Dinginkan tubuh CEPAT: kompres es di ketiak, leher, dan selangkangan.
5. Kipasi korban sambil menyiram dengan air dingin.
6. JANGAN beri minum jika korban tidak sadar.

**Pencegahan:**
- Hindari aktivitas berat saat suhu > 35°C.
- Minum air setiap 15-20 menit saat beraktivitas di luar.
- Kenali tanda-tanda awal heat exhaustion: pusing, berkeringat berlebihan, lemas.""",
        "Cerah"
    ),
    (
        "Tips Hemat Energi Saat Cuaca Ekstrem",
        """Cuaca ekstrem (panas terik atau hujan deras berkepanjangan) mempengaruhi konsumsi energi di rumah:

**Saat Cuaca Panas:**
- Tutup tirai/gorden sisi barat pada siang hari — mengurangi panas masuk hingga 35%.
- Set AC di 24-26°C, bukan 18°C — setiap 1°C lebih dingin = +8% konsumsi listrik.
- Gunakan kipas angin + AC bersama untuk sirkulasi lebih efisien.
- Masak di pagi atau malam hari — kompor menambah panas ruangan.
- Tanam pohon atau pasang sunshading di sekitar jendela.

**Saat Cuaca Hujan/Mendung:**
- Manfaatkan cahaya alami selama masih terang.
- Cabut charger dan perangkat standby — ini "phantom load" 5-10% tagihan listrik.
- Gunakan dehumidifier jika kelembapan > 70% untuk cegah jamur.
- Cuci pakaian penuh kapasitas mesin, bukan setengah-setengah.

Dengan kebiasaan ini, tagihan listrik bisa turun 20-30% per bulan!""",
        "Cerah"
    ),
    (
        "Panduan Lengkap Menghindari Banjir Saat Hujan Deras",
        """Banjir bisa terjadi sangat cepat. Persiapkan diri dengan panduan ini:

**Kesiapan Sebelum Musim Hujan:**
- Bersihkan selokan dan saluran air di sekitar rumah.
- Siapkan "go-bag": dokumen penting (fotokopi KTP, KK), obat-obatan, makanan kering 3 hari, senter, radio baterai, uang tunai.
- Simpan barang berharga di tempat tinggi.
- Ketahui rute evakuasi dan titik kumpul terdekat.

**Saat Hujan Deras Berlangsung:**
- Pantau info BMKG dan SkyWise AI untuk prakiraan.
- Waspadai jika air mulai naik lebih dari 30cm.
- Matikan listrik jika air masuk rumah.
- Jangan berjalan/berkendara melewati banjir > 30cm — ada risiko terseret arus.

**Setelah Banjir:**
- Jangan gunakan air ledeng sampai dipastikan aman.
- Waspada ular atau binatang berbahaya yang masuk saat banjir.
- Bersihkan dengan disinfektan untuk mencegah leptospirosis.
- Laporkan kerusakan ke BPBD setempat.""",
        "Hujan"
    ),
]

# ── DATA GALERI (Unsplash CDN — public domain) ───────────────────────────────
# Format: (judul, kota, kondisi, deskripsi, url_gambar)

GALERI_DATA = [
    (
        "Matahari Terbit di Atas Awan",
        "Balikpapan",
        "cerah",
        "Pemandangan matahari terbit yang indah dari ketinggian. Langit berwarna oranye keemasan menyambut pagi.",
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
    ),
    (
        "Hujan Lebat di Kota Jakarta",
        "Jakarta",
        "hujan",
        "Hujan deras mengguyur Jakarta sore hari. Jalanan basah memantulkan cahaya lampu kota.",
        "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?w=800&q=80",
    ),
    (
        "Awan Cumulonimbus Mengancam",
        "Samarinda",
        "badai",
        "Awan besar berwarna gelap terbentuk di langit Samarinda menjelang sore. Pertanda badai petir akan segera datang.",
        "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=800&q=80",
    ),
    (
        "Kabut Tipis di Pagi Hari",
        "Bandung",
        "berkabut",
        "Kabut pagi yang lembut menyelimuti kota Bandung. Suhu sejuk membuat pagi hari terasa nyaman.",
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80",
    ),
    (
        "Langit Biru Cerah Berawan",
        "Surabaya",
        "berawan",
        "Hari yang sempurna untuk beraktivitas di luar ruangan. Awan putih berarak di langit biru Surabaya.",
        "https://images.unsplash.com/photo-1601297183305-6df142704ea2?w=800&q=80",
    ),
    (
        "Gerimis Sore di Makassar",
        "Makassar",
        "hujan",
        "Gerimis ringan turun menjelang sore di Makassar. Udara menjadi segar dan sejuk setelah panas seharian.",
        "https://images.unsplash.com/photo-1428592953211-077101b2021b?w=800&q=80",
    ),
    (
        "Cuaca Cerah di Pantai",
        "Bali",
        "cerah",
        "Hari yang sempurna di pantai Bali. Sinar matahari bersinar terik, cocok untuk berenang dan berjemur.",
        "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80",
    ),
    (
        "Awan Mendung Sebelum Hujan",
        "Yogyakarta",
        "berawan",
        "Awan mendung tebal mulai menggelayut di langit Yogyakarta. Hujan tampaknya akan segera turun.",
        "https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?w=800&q=80",
    ),
    (
        "Angin Kencang di Pantai Selatan",
        "Cilacap",
        "angin",
        "Angin kencang dari laut selatan membuat ombak tinggi di pantai Cilacap. Nelayan diimbau tidak melaut.",
        "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=800&q=80",
    ),
    (
        "Hujan Deras Disertai Petir",
        "Palembang",
        "badai",
        "Badai petir dahsyat melanda Palembang malam hari. Kilatan petir menerangi langit hitam.",
        "https://images.unsplash.com/photo-1504608524841-42584120d49f?w=800&q=80",
    ),
]


def download_image(url, dest_path):
    """Download image from URL to dest_path, return True on success."""
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        req = urllib.request.Request(url, headers={'User-Agent': 'SkyWiseBot/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp, open(dest_path, 'wb') as f:
            f.write(resp.read())
        return True
    except Exception as e:
        print(f"[WARN] Could not download {url}: {e}")
        return False


def seed_tips(apps, schema_editor):
    TipsCuaca = apps.get_model('cuaca', 'TipsCuaca')
    Kategori  = apps.get_model('cuaca', 'Kategori')
    User      = apps.get_model('auth',  'User')

    if TipsCuaca.objects.count() > 0:
        return  # Already seeded

    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        admin_user = User.objects.first()
    if not admin_user:
        return  # No user, skip

    for judul, isi, nama_kat in TIPS_DATA:
        kat = Kategori.objects.filter(nama__iexact=nama_kat).first()
        if not kat:
            kat = Kategori.objects.first()
        if kat:
            TipsCuaca.objects.create(
                judul=judul, isi=isi,
                kategori=kat, penulis=admin_user,
            )
    print(f"[✓] Seeded {len(TIPS_DATA)} tips cuaca.")


def seed_galeri(apps, schema_editor):
    Galeri = apps.get_model('cuaca', 'Galeri')
    User   = apps.get_model('auth',  'User')

    if Galeri.objects.count() > 0:
        return

    admin_user = User.objects.filter(is_staff=True).first()
    media_root = settings.MEDIA_ROOT

    success = 0
    for judul, kota, kondisi, deskripsi, url in GALERI_DATA:
        filename  = f"galeri/seed_{kota.lower()}_{kondisi}_{GALERI_DATA.index((judul,kota,kondisi,deskripsi,url))}.jpg"
        dest_path = os.path.join(media_root, filename)

        downloaded = download_image(url, dest_path)

        # Even if download fails, create record with placeholder path
        Galeri.objects.create(
            judul=judul, kota=kota, kondisi_cuaca=kondisi,
            deskripsi=deskripsi,
            gambar=filename if downloaded else 'galeri/placeholder.jpg',
            diunggah_oleh=admin_user,
            nama_pengunggah='Tim SkyWise AI',
            disetujui=True,
        )
        if downloaded:
            success += 1

    print(f"[✓] Seeded {success}/{len(GALERI_DATA)} galeri photos.")


class Migration(migrations.Migration):
    dependencies = [
        ('cuaca', '0003_seed_kategori'),
        ('auth',  '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(seed_tips, migrations.RunPython.noop),
        migrations.RunPython(seed_galeri, migrations.RunPython.noop),
    ]
