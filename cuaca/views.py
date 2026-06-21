import json
import requests
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from .models import Kategori, TipsCuaca, Feedback, Galeri

def is_admin(user):
    return user.is_staff

WEATHER_EMOJI = {
    'clear sky':'☀️','few clouds':'🌤️','scattered clouds':'⛅',
    'broken clouds':'☁️','overcast clouds':'☁️',
    'light rain':'🌦️','moderate rain':'🌧️','heavy intensity rain':'🌧️',
    'thunderstorm':'⛈️','snow':'❄️','mist':'🌫️','fog':'🌫️',
    'haze':'🌫️','drizzle':'🌦️',
}

BG_MAP = {
    'clear':'bg-clear','clouds':'bg-cloudy','rain':'bg-rain',
    'drizzle':'bg-rain','thunderstorm':'bg-storm','snow':'bg-snow',
    'mist':'bg-fog','fog':'bg-fog','haze':'bg-fog',
    'smoke':'bg-fog','dust':'bg-fog','sand':'bg-fog','ash':'bg-fog',
    'squall':'bg-storm','tornado':'bg-storm',
}

WEATHER_VISUAL = {
    'clear': {
        'label':'Cerah','color':'#f59e0b','text_color':'#92400e',
        'desc':'Langit bersih tanpa tutupan awan. Sinar matahari langsung mencapai permukaan dengan intensitas penuh. Indeks UV cenderung tinggi, terutama antara pukul 10.00–14.00.',
        'tips':['UV index tinggi — paparan maksimal','Visibilitas jarak jauh optimal','Suhu udara naik signifikan siang hari'],
        'svg_key':'clear',
    },
    'clouds': {
        'label':'Berawan','color':'#94a3b8','text_color':'#1e293b',
        'desc': 'Langit tertutup sebagian awan. Suhu lebih sejuk dari cuaca cerah, kelembapan cenderung tinggi. Sinar UV terhalang awan sehingga paparan lebih rendah dari kondisi cerah.',
        'tips': ['Tutupan awan 60–100%', 'UV index rendah', 'Kelembapan bisa terasa lembab'],
        'svg_key':'clouds',
    },
    'rain': {
        'label':'Hujan','color':'#3b82f6','text_color':'#1e3a5f',
        'desc':'Curah hujan saat ini aktif. Jalanan bisa licin dan visibilitas berkurang. Kurangi kecepatan berkendara, gunakan jas hujan atau payung, dan hindari daerah rawan banjir.',
        'tips':['Bawa jas hujan atau payung','Hati-hati jalanan licin','Hindari area rawan banjir'],
        'svg_key':'rain',
    },
    'drizzle': {
        'label':'Gerimis','color':'#60a5fa','text_color':'#1e3a5f',
        'desc':'Gerimis ringan turun. Meski terasa sepele, tanah bisa menjadi licin dan pakaian basah perlahan. Siapkan jas hujan tipis dan waspadai visibilitas rendah saat berkendara.',
        'tips':['Siapkan jas hujan tipis','Waspadai permukaan licin','Tetap nyaman beraktivitas'],
        'svg_key':'rain',
    },
    'thunderstorm': {
        'label':'Badai Petir','color':'#6366f1','text_color':'#1e1b4b',
        'desc':'Badai petir aktif adalah kondisi paling berbahaya. Hindari berada di ruang terbuka, dekat pohon tinggi, atau benda logam. Matikan peralatan elektronik dan tunggu hingga badai berlalu.',
        'tips':['Tetap di dalam ruangan','Jauhi jendela dan pintu','Matikan elektronik tidak terpakai'],
        'svg_key':'storm',
    },
    'snow': {
        'label':'Salju','color':'#bfdbfe','text_color':'#1e3a5f',
        'desc':'Salju turun — kondisi langka di Indonesia! Suhu sangat dingin dan jalanan bisa sangat licin atau terblokir. Gunakan pakaian berlapis dan waspadai hypothermia.',
        'tips':['Gunakan pakaian berlapis','Hati-hati jalanan beku','Konsumsi makanan hangat'],
        'svg_key':'snow',
    },
    'mist': {
        'label':'Berkabut','color':'#cbd5e1','text_color':'#334155',
        'desc':'Kabut mengurangi jarak pandang secara signifikan. Saat berkendara, nyalakan lampu kabut atau lampu hazard, kurangi kecepatan, dan jaga jarak aman.',
        'tips':['Nyalakan lampu saat berkendara','Kurangi kecepatan','Jaga jarak aman'],
        'svg_key':'fog',
    },
    'fog': {
        'label':'Kabut Tebal','color':'#94a3b8','text_color':'#1e293b',
        'desc':'Kabut sangat tebal dengan visibilitas di bawah 200 meter. Hindari berkendara jika tidak mendesak.',
        'tips':['Hindari berkendara jika bisa','Gunakan lampu hazard','Ikuti marka jalan'],
        'svg_key':'fog',
    },
    'haze': {
        'label':'Asap/Kabut','color':'#d6d3d1','text_color':'#44403c',
        'desc':'Kabut asap mengurangi kualitas udara dan visibilitas. Gunakan masker N95.',
        'tips':['Gunakan masker N95','Hindari aktivitas berat outdoor','Tutup ventilasi jika perlu'],
        'svg_key':'fog',
    },
    'default': {
        'label':'Cuaca','color':'#64748b','text_color':'#0f172a',
        'desc':'Pantau terus kondisi cuaca terkini dan selalu siap dengan perlengkapan sesuai cuaca.',
        'tips':['Pantau prakiraan berkala','Siapkan perlengkapan cuaca','Tetap waspada perubahan'],
        'svg_key':'default',
    },
}

WIND_DIRS = ['U','TL','T','TG','S','BD','B','BL']

def get_weather_visual(visual_key, feels_like, kelembaban):
    """
    Mengembalikan copy dari WEATHER_VISUAL[visual_key] dengan desc & tips
    yang disesuaikan suhu terasa (feels_like) aktual, supaya konsisten
    dengan rekomendasi AI yang juga berbasis suhu real-time.
    """
    visual = dict(WEATHER_VISUAL[visual_key])  # copy, jangan ubah dict asli

    if visual_key == 'clouds':
        if feels_like >= 32:
            visual['desc'] = (
                'Langit tertutup sebagian awan, namun suhu tetap terasa panas akibat kelembapan tinggi. '
                'Sinar matahari memang terhalang awan, tapi udara lembap membuat suhu terasa lebih tinggi dari biasanya.'
            )
            visual['tips'] = [
                f'Suhu terasa {feels_like}°C meski berawan',
                f'Kelembapan {kelembaban}% — tubuh sulit berkeringat',
                'Perbanyak minum air putih meski tidak terlihat cerah',
            ]
        else:
            visual['desc'] = (
                'Langit tertutup sebagian awan. Suhu terasa lebih sejuk dibanding cuaca cerah, '
                'karena sinar matahari terhalang awan sehingga paparan panas berkurang.'
            )
            visual['tips'] = [
                'Tutupan awan 60–100%',
                'UV index lebih rendah dari cuaca cerah',
                f'Suhu terasa nyaman di {feels_like}°C',
            ]

    elif visual_key == 'clear':
        if feels_like >= 36:
            visual['desc'] = (
                'Langit bersih tanpa tutupan awan dan suhu terasa sangat terik. '
                'Paparan sinar matahari langsung membuat suhu terasa jauh lebih panas dari suhu udara sebenarnya.'
            )
            visual['tips'] = [
                f'Suhu terasa sangat panas {feels_like}°C',
                'Hindari aktivitas luar ruangan 10.00–16.00',
                'Gunakan tabir surya dan perbanyak cairan',
            ]
        else:
            visual['desc'] = (
                'Langit bersih tanpa tutupan awan. Sinar matahari mencapai permukaan dengan intensitas penuh, '
                'namun suhu terasa masih dalam batas nyaman untuk beraktivitas.'
            )
            visual['tips'] = [
                'UV index tinggi — tetap gunakan pelindung',
                'Visibilitas jarak jauh optimal',
                f'Suhu terasa nyaman di {feels_like}°C',
            ]

    return visual

def wind_direction(deg):
    if deg is None: return '—'
    return WIND_DIRS[round(deg / 45) % 8]

def aqi_info(aqi_val):
    labels  = {1:'Baik',2:'Sedang',3:'Tidak Sehat (sensitif)',4:'Tidak Sehat',5:'Sangat Tidak Sehat'}
    badges  = {1:'b-green',2:'b-yellow',3:'b-orange',4:'b-red',5:'b-red'}
    pct     = {1:10,2:30,3:55,4:75,5:92}
    return {
        'aqi':aqi_val,'label':labels.get(aqi_val,'—'),
        'badge_class':badges.get(aqi_val,'b-gray'),
        'percent':pct.get(aqi_val,5),
    }

POPULAR_CITIES = ['Balikpapan','Jakarta','Surabaya','Makassar','Bandung']

FEATURES = [
    {'icon':'⏱️','title':'Data Real-Time','desc':'Informasi cuaca diperbarui otomatis setiap 10 menit untuk memberikan data paling akurat.','color':'linear-gradient(135deg,#dbeafe,#bfdbfe)'},
    {'icon':'🗺️','title':'Peta Cuaca Interaktif','desc':'Klik lokasi mana saja di peta dunia dan langsung dapatkan data cuaca real-time lengkap dengan layer overlay.','color':'linear-gradient(135deg,#dcfce7,#bbf7d0)'},
    {'icon':'🌍','title':'Cakupan Global','desc':'Cakupan lebih dari 200.000 kota di seluruh dunia, dari Indonesia hingga mancanegara.','color':'linear-gradient(135deg,#e0f2fe,#bae6fd)'},
    {'icon':'📱','title':'Responsif','desc':'Tampilan optimal di semua perangkat: smartphone, tablet, hingga desktop.','color':'linear-gradient(135deg,#fce7f3,#fbcfe8)'},
    {'icon':'⚡','title':'Informasi Lengkap','desc':'Data detail meliputi suhu, kelembapan, kecepatan angin, tekanan udara, dan banyak lagi.','color':'linear-gradient(135deg,#fef9c3,#fde68a)'},
    {'icon':'🤖','title':'AI Rekomendasi','desc':'Cukup ketik nama kota dan dapatkan saran aktivitas dari AI dalam hitungan detik.','color':'linear-gradient(135deg,#ede9fe,#ddd6fe)'},
]

PHENOMENA = [
    ('Cerah Berawan','Ideal untuk aktivitas luar ruangan.','🌤️','Kondisi cuaca cerah berawan terjadi ketika sebagian langit tertutup awan tipis. Sinar matahari masih bisa menembus dengan baik. Cocok untuk olahraga, berpiknik, atau perjalanan jauh.','linear-gradient(135deg,#fbbf24,#f59e0b)','b-yellow','Cerah'),
    ('Hujan Ringan','Suhu menurun sedikit, udara terasa sejuk.','🌦️','Hujan ringan ditandai dengan curah hujan rendah dan berlangsung singkat. Tetap bawa payung! Hindari aktivitas berat di luar ruangan dan waspadai jalan licin.','linear-gradient(135deg,#60a5fa,#3b82f6)','b-blue','Hujan'),
    ('Hujan Petir','Waspada cuaca ekstrem, tetap di dalam rumah.','⛈️','Dihasilkan dari awan Cumulonimbus yang sangat besar, memicu gesekan listrik statis yang menghasilkan kilat dan guntur. Hindari berada di tempat terbuka, pohon tinggi, atau benda logam.','linear-gradient(135deg,#6366f1,#4338ca)','b-purple','Badai'),
    ('Berkabut','Visibilitas rendah, harap hati-hati.','🌫️','Kabut terjadi ketika uap air di dekat permukaan bumi mengembun menjadi tetesan kecil. Visibilitas bisa sangat rendah (<100m). Kurangi kecepatan berkendara dan nyalakan lampu kabut.','linear-gradient(135deg,#94a3b8,#64748b)','b-gray','Kabut'),
    ('Mendung','Langit tertutup awan mendung yang gelap.','☁️','Cuaca mendung tanpa hujan bisa berubah sewaktu-waktu. Persiapkan diri dengan membawa payung. Kelembapan udara biasanya tinggi dan suhu relatif lebih rendah dari biasanya.','linear-gradient(135deg,#475569,#334155)','b-gray','Mendung'),
    ('Angin Kencang','Potensi gangguan di daerah pesisir.','💨','Angin kencang dapat berbahaya terutama di daerah pesisir dan dataran tinggi. Hindari aktivitas di luar ruangan, amankan benda-benda ringan, dan waspadai pohon tumbang.','linear-gradient(135deg,#0ea5e9,#0369a1)','b-sky','Cerah'),
]

OSM_SUBCITY_TYPES = {
    'suburb', 'neighbourhood', 'quarter', 'hamlet',
    'residential', 'village', 'subdistrict',
}

OSM_CITY_TYPES = {
    'city', 'town', 'municipality', 'administrative',
    'county', 'state', 'country', 'region',
    'district', 'province',
}


def index(request):
    tips_terbaru  = TipsCuaca.objects.all().order_by('-dibuat')[:3]
    galeri_terbaru = Galeri.objects.filter(disetujui=True).order_by('-dibuat')[:6]
    return render(request, 'index.html', {
        'tips_terbaru': tips_terbaru,
        'features': FEATURES,
        'galeri_terbaru': galeri_terbaru,
    })


def _check_nominatim(kota_clean, country_hint=None):
    try:
        headers = {'User-Agent': 'SkyWise/1.0'}
        if country_hint:
            url = (
                f'https://nominatim.openstreetmap.org/search'
                f'?q={kota_clean}&countrycodes={country_hint}&format=json'
                f'&limit=3&addressdetails=1&accept-language=id'
            )
            resp = requests.get(url, timeout=6, headers=headers).json()
            if resp:
                best = resp[0]
                return (
                    best.get('type', ''),
                    best.get('address', {}).get('country_code', '').upper(),
                    float(best['lat']),
                    float(best['lon']),
                )

        url = (
            f'https://nominatim.openstreetmap.org/search'
            f'?q={kota_clean}&format=json&limit=3&addressdetails=1&accept-language=id'
        )
        resp = requests.get(url, timeout=6, headers=headers).json()
        if resp:
            best = resp[0]
            return (
                best.get('type', ''),
                best.get('address', {}).get('country_code', '').upper(),
                float(best['lat']),
                float(best['lon']),
            )
    except Exception:
        pass
    return None, None, None, None


def _search_owm_by_name(kota, API, expected_country=None):
    kota_clean = kota.strip()

    osm_type, nom_country, lat_nom, lon_nom = _check_nominatim(kota_clean, expected_country)

    if osm_type is not None:
        if osm_type in OSM_SUBCITY_TYPES:
            return None, 'subcity', lat_nom, lon_nom

    geo_url = f'https://api.openweathermap.org/geo/1.0/direct?q={kota_clean}&limit=5&appid={API}'
    try:
        geo_resp = requests.get(geo_url, timeout=8).json()
    except Exception:
        geo_resp = []

    if geo_resp:
        kota_lower = kota_clean.lower().split(',')[0].strip()

        best = None

        if expected_country:
            for g in geo_resp:
                if (g.get('name', '').lower() == kota_lower and
                        g.get('country', '').upper() == expected_country.upper()):
                    best = g
                    break

        if best is None:
            for g in geo_resp:
                if g.get('name', '').lower() == kota_lower:
                    best = g
                    break

        if best is None:
            best = geo_resp[0]

        lat = best['lat']
        lon = best['lon']
        owm_country = best.get('country', '').upper()

        if expected_country and owm_country and owm_country != expected_country.upper():
            if nom_country and nom_country != expected_country.upper():
                return None, 'notfound', None, None
            elif nom_country == expected_country.upper() and lat_nom and lon_nom:
                if osm_type in OSM_SUBCITY_TYPES:
                    return None, 'subcity', lat_nom, lon_nom
                url = (
                    f'https://api.openweathermap.org/data/2.5/weather'
                    f'?lat={lat_nom}&lon={lon_nom}&appid={API}&units=metric&lang=id'
                )
                try:
                    resp = requests.get(url, timeout=8)
                    data = resp.json()
                    if int(data.get('cod', 0)) == 200:
                        return data, None, data['coord']['lat'], data['coord']['lon']
                except Exception:
                    pass
            return None, 'notfound', None, None

        url = (
            f'https://api.openweathermap.org/data/2.5/weather'
            f'?lat={lat}&lon={lon}&appid={API}&units=metric&lang=id'
        )
        try:
            resp = requests.get(url, timeout=8)
            data = resp.json()
            if int(data.get('cod', 0)) == 200:
                return data, None, data['coord']['lat'], data['coord']['lon']
        except Exception:
            pass

    url_direct = (
        f'https://api.openweathermap.org/data/2.5/weather'
        f'?q={kota_clean}&appid={API}&units=metric&lang=id'
    )
    try:
        resp = requests.get(url_direct, timeout=8)
        data = resp.json()
        if int(data.get('cod', 0)) == 200:
            owm_country = data.get('sys', {}).get('country', '').upper()
            if expected_country and owm_country and owm_country != expected_country.upper():
                return None, 'wrong_location', data['coord']['lat'], data['coord']['lon']
            return data, None, data['coord']['lat'], data['coord']['lon']
    except Exception:
        pass

    if osm_type is None:
        return None, 'notfound', None, None

    if osm_type in OSM_SUBCITY_TYPES:
        return None, 'subcity', lat_nom, lon_nom

    return None, 'subcity', lat_nom, lon_nom


def cek_cuaca(request):
    cuaca = None; forecast = None; hourly = None
    air_quality = None; error = None; rekomendasi_ai = None
    kota = ''; weather_code = ''; is_day = 1
    weather_emoji = '🌤️'; bg_class = 'bg-default'
    tanggal_sekarang = datetime.now().strftime('%A, %d %b %Y')
    for en, idn in {'Monday':'Senin','Tuesday':'Selasa','Wednesday':'Rabu','Thursday':'Kamis','Friday':'Jumat','Saturday':'Sabtu','Sunday':'Minggu'}.items():
        tanggal_sekarang = tanggal_sekarang.replace(en, idn)
    weather_visual = None; galeri_related = []
    aqi_data = None
    aqi_val = 1

    if request.method == 'POST':
        kota = request.POST.get('kota', '').strip()
        lat_param = request.POST.get('lat', '').strip()
        lon_param = request.POST.get('lon', '').strip()
        negara_hint  = request.POST.get('negara', '').strip().upper()
        is_subcity_hint = request.POST.get('is_subcity', '').strip()
        API  = settings.OPENWEATHER_API_KEY
        data = None
        error_type = None

        if is_subcity_hint == '1':
            error = 'subcity'
        if lat_param and lon_param:
            try:
                url = (
                    f'https://api.openweathermap.org/data/2.5/weather'
                    f'?lat={lat_param}&lon={lon_param}&appid={API}&units=metric&lang=id'
                )
                resp = requests.get(url, timeout=8)
                data = resp.json()
                if int(data.get('cod', 0)) != 200:
                    data = None
                    error = 'notfound'
                else:
                    if negara_hint:
                        owm_country = data.get('sys', {}).get('country', '').upper()
                        if owm_country and owm_country != negara_hint:
                            pass
            except Exception:
                data = None
                error = 'notfound'
        else:
            data, error_type, _, _ = _search_owm_by_name(kota, API, negara_hint or None)
            if error_type:
                error = error_type

        if data and int(data.get('cod', 0)) == 200:
            owm_name = data.get('name', '').lower()
            user_input = kota.lower()

        if data and int(data.get('cod', 0)) == 200:
            error = None
            desc_raw = data['weather'][0]['description'].lower()
            main_raw = data['weather'][0]['main'].lower()
            sunrise  = data['sys']['sunrise']
            sunset   = data['sys']['sunset']
            now_ts   = data['dt']
            is_day   = 1 if sunrise < now_ts < sunset else 0

            weather_emoji = WEATHER_EMOJI.get(desc_raw, '🌤️')
            bg_class = BG_MAP.get(main_raw, 'bg-default')
            if not is_day: bg_class = 'bg-night'

            weather_code = data['weather'][0]['id']
            clouds = data.get('clouds', {}).get('all', 0)
            dew    = round(data['main']['temp'] - ((100 - data['main']['humidity']) / 5), 1)

            cuaca = {
                'kota': kota.title() if kota else data['name'],
                'negara': data['sys']['country'],
                'suhu': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'suhu_min': round(data['main']['temp_min']),
                'suhu_max': round(data['main']['temp_max']),
                'deskripsi': data['weather'][0]['description'].title(),
                'kelembaban': data['main']['humidity'],
                'angin': round(data['wind']['speed']*3.6, 1),
                'wind_dir': wind_direction(data['wind'].get('deg')),
                'visibilitas': round(data.get('visibility', 0)/1000, 1),
                'tekanan': data['main']['pressure'],
                'icon': data['weather'][0]['icon'],
                'sunrise': datetime.fromtimestamp(sunrise).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(sunset).strftime('%H:%M'),
                'clouds': clouds, 'dew_point': dew,
                'lat': data['coord']['lat'],
                'lon': data['coord']['lon'],
            }

            visual_key = main_raw if main_raw in WEATHER_VISUAL else 'default'
            weather_visual = get_weather_visual(visual_key, cuaca['feels_like'], cuaca['kelembaban'])

            galeri_related = list(Galeri.objects.filter(
                disetujui=True, kota__icontains=cuaca['kota']
            ).order_by('-dibuat')[:3])
            if len(galeri_related) < 3:
                kondisi_map = {
                    'clear': 'cerah', 'clouds': 'berawan', 'rain': 'hujan',
                    'drizzle': 'hujan', 'thunderstorm': 'badai', 'mist': 'berkabut',
                    'fog': 'berkabut', 'haze': 'berkabut', 'snow': 'salju',
                }
                cond = kondisi_map.get(main_raw, 'lainnya')
                ids_sudah = [g.id for g in galeri_related]
                tambahan = Galeri.objects.filter(
                    disetujui=True, kondisi_cuaca=cond
                ).exclude(id__in=ids_sudah).order_by('-dibuat')[:3-len(galeri_related)]
                galeri_related += list(tambahan)

            lat_fc = data['coord']['lat']
            lon_fc = data['coord']['lon']
            url_fc = (
                f'https://api.openweathermap.org/data/2.5/forecast'
                f'?lat={lat_fc}&lon={lon_fc}&appid={API}&units=metric&lang=id'
            )
            try:
                rfc = requests.get(url_fc, timeout=8).json()
                forecast = []; hourly = []; seen_dates = []
                DAY_ID = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']
                for item in rfc.get('list', []):
                    if len(hourly) < 16:
                        hourly.append({
                            'jam': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
                            'suhu': round(item['main']['temp']),
                            'icon': item['weather'][0]['icon'],
                            'pop': round(item.get('pop', 0)*100),
                        })
                    tgl = item['dt_txt'].split(' ')[0]
                    if tgl not in seen_dates and len(forecast) < 5:
                        seen_dates.append(tgl)
                        dt_obj = datetime.strptime(tgl, '%Y-%m-%d')
                        forecast.append({
                            'hari': DAY_ID[dt_obj.weekday()], 'tanggal': tgl,
                            'suhu_min': round(item['main']['temp_min']),
                            'suhu_max': round(item['main']['temp_max']),
                            'icon': item['weather'][0]['icon'],
                        })
            except Exception:
                forecast = []
                hourly = []

            try:
                lat = data['coord']['lat']; lon = data['coord']['lon']
                url_aq = f'https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API}'
                raq = requests.get(url_aq, timeout=8).json()
                aqi_val = raq['list'][0]['main']['aqi']
                comp = raq['list'][0]['components']
                air_info = aqi_info(aqi_val)
                air_info['components'] = [
                    {'name': 'PM2.5', 'value': round(comp.get('pm2_5', 0), 1)},
                    {'name': 'PM10', 'value': round(comp.get('pm10', 0), 1)},
                    {'name': 'CO', 'value': round(comp.get('co', 0), 1)},
                    {'name': 'NO₂', 'value': round(comp.get('no2', 0), 1)},
                    {'name': 'O₃', 'value': round(comp.get('o3', 0), 1)},
                    {'name': 'SO₂', 'value': round(comp.get('so2', 0), 1)},
                ]
                air_quality = air_info
                aqi_data = air_info
            except Exception:
                air_quality = None
                aqi_data = None

        elif not error:
            error = 'notfound'

    return render(request,'cek_cuaca.html',{
        'cuaca':cuaca,'forecast':forecast,'hourly':hourly,
        'air_quality':air_quality,'aqi_data':aqi_data,
        'error':error,'kota':kota,
        'rekomendasi_ai':rekomendasi_ai,'weather_code':weather_code,
        'is_day':is_day,'weather_emoji':weather_emoji,'bg_class':bg_class,
        'tanggal_sekarang':tanggal_sekarang,'popular_cities':POPULAR_CITIES,
        'weather_visual':weather_visual,'galeri_related':galeri_related,
        'OPENWEATHER_API_KEY': settings.OPENWEATHER_API_KEY,
        'aqi_value': aqi_val,
    })


def galeri_list(request):
    kondisi_filter = request.GET.get('kondisi','')
    kota_filter    = request.GET.get('kota','').strip()
    galeri = Galeri.objects.filter(disetujui=True)
    if kondisi_filter:
        galeri = galeri.filter(kondisi_cuaca=kondisi_filter)
    if kota_filter:
        galeri = galeri.filter(kota__icontains=kota_filter)
    galeri = galeri.order_by('-dibuat')
    kondisi_choices = Galeri.KONDISI_CHOICES
    return render(request,'galeri.html',{
        'galeri':galeri,'kondisi_choices':kondisi_choices,
        'kondisi_filter':kondisi_filter,'kota_filter':kota_filter,
    })


def galeri_upload(request):
    kondisi_choices = Galeri.KONDISI_CHOICES
    kategori_list   = Kategori.objects.all()
    if request.method == 'POST':
        judul     = request.POST.get('judul','').strip()
        kota      = request.POST.get('kota','').strip()
        kondisi   = request.POST.get('kondisi_cuaca','lainnya')
        deskripsi = request.POST.get('deskripsi','').strip()
        gambar    = request.FILES.get('gambar')
        nama_input = request.POST.get('nama_pengunggah','').strip()
        if not judul or not kota or not gambar:
            messages.error(request,'Judul, kota, dan foto wajib diisi!')
        else:
            obj = Galeri(
                judul=judul, kota=kota, kondisi_cuaca=kondisi,
                deskripsi=deskripsi, gambar=gambar, disetujui=False,
            )
            if request.user.is_authenticated:
                obj.diunggah_oleh = request.user
                obj.nama_pengunggah = request.user.get_full_name() or request.user.username
            else:
                obj.nama_pengunggah = nama_input or 'Anonim'
            obj.save()
            messages.success(request,'Foto berhasil dikirim! Menunggu persetujuan admin.')
            return redirect('galeri_list')
    return render(request,'galeri_upload.html',{
        'kondisi_choices':kondisi_choices,'kategori_list':kategori_list,
    })


def weather_highlights(request):
    kategori_id  = request.GET.get('kategori','')
    tips_list    = TipsCuaca.objects.all().order_by('-dibuat')
    galeri_list  = Galeri.objects.filter(disetujui=True).order_by('-dibuat')
    kategori_list= Kategori.objects.all()
    if kategori_id:
        tips_list  = tips_list.filter(kategori_id=kategori_id)
        galeri_list= galeri_list.filter(kategori_id=kategori_id)
    phenomena = [
        {'title':p[0],'description':p[1],'emoji':p[2],'detail':p[3],
         'gradient':p[4],'badge_class':p[5],'category':p[6]} for p in PHENOMENA
    ]
    return render(request,'weather_highlights.html',{
        'phenomena':phenomena,'tips_list':tips_list,
        'galeri_list':galeri_list[:9],
        'kategori_list':kategori_list,'kategori_aktif':kategori_id,
    })


def about_us(request):
    return render(request,'about_us.html')


def feedback(request):
    feedbacks = Feedback.objects.all().order_by('-dibuat')
    if request.method == 'POST':
        nama       = request.POST.get('nama','').strip()
        pesan      = request.POST.get('pesan','').strip()
        rating     = request.POST.get('rating','0')
        pengalaman = request.POST.get('pengalaman','')
        if not nama or not pesan or not rating or rating=='0':
            messages.error(request,'Harap isi semua field termasuk rating bintang!')
        else:
            fb = Feedback.objects.create(nama=nama,pesan=pesan,rating=int(rating),pengalaman=pengalaman)
            return render(request,'feedback.html',{'sukses':True,'feedback_baru':fb,'feedbacks':Feedback.objects.all().order_by('-dibuat')})
    return render(request,'feedback.html',{'feedbacks':feedbacks})


def tips_list_view(request):
    kategori_list = Kategori.objects.all()
    kategori_id   = request.GET.get('kategori')
    tips = TipsCuaca.objects.filter(kategori_id=kategori_id).order_by('-dibuat') if kategori_id else TipsCuaca.objects.all().order_by('-dibuat')
    return render(request,'tips_list.html',{'tips':tips,'kategori_list':kategori_list,'kategori_aktif':kategori_id})


def tips_detail(request, pk):
    tips = get_object_or_404(TipsCuaca, pk=pk)
    return render(request,'tips_detail.html',{'tips':tips})


@login_required
def profil(request):
    galeri_upload_list = Galeri.objects.filter(diunggah_oleh=request.user).order_by('-dibuat')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profil':
            request.user.first_name = request.POST.get('first_name','').strip()
            request.user.email      = request.POST.get('email','').strip()
            request.user.save()
            messages.success(request,'Profil berhasil diperbarui!')
        elif action == 'ganti_password':
            from django.contrib.auth import update_session_auth_hash
            old = request.POST.get('old_password','')
            new = request.POST.get('new_password','')
            if request.user.check_password(old):
                if len(new) >= 8:
                    request.user.set_password(new)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request,'Password berhasil diperbarui!')
                else:
                    messages.error(request,'Password baru minimal 8 karakter!')
            else:
                messages.error(request,'Password lama salah!')
        return redirect('profil')
    return render(request,'profil.html',{
        'galeri_upload_list':galeri_upload_list,
    })


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    from django.db.models import Avg
    total_tips       = TipsCuaca.objects.count()
    total_feedback   = Feedback.objects.count()
    total_kategori   = Kategori.objects.count()
    total_users      = User.objects.count()
    total_galeri     = Galeri.objects.filter(disetujui=True).count()
    pending_galeri   = Galeri.objects.filter(disetujui=False).count()
    avg_rating       = Feedback.objects.aggregate(a=Avg('rating'))['a'] or 0
    feedback_terbaru = Feedback.objects.order_by('-dibuat')[:6]
    tips_terbaru     = TipsCuaca.objects.order_by('-dibuat')[:5]
    rating_dist = [{'bintang':i,'jumlah':Feedback.objects.filter(rating=i).count()} for i in range(1,6)]
    return render(request,'dashboard/index.html',{
        'total_tips':total_tips,'total_feedback':total_feedback,
        'total_kategori':total_kategori,'total_users':total_users,
        'avg_rating':round(avg_rating,1),'feedback_terbaru':feedback_terbaru,
        'tips_terbaru':tips_terbaru,'rating_dist':rating_dist,
        'total_galeri':total_galeri,'pending_galeri':pending_galeri,
    })


from django.core.paginator import Paginator

@login_required
@user_passes_test(is_admin)
def tips_list_dashboard(request):
    q = request.GET.get('q', '')
    tips_qs = TipsCuaca.objects.select_related('kategori', 'penulis').order_by('-dibuat')
    if q:
        tips_qs = tips_qs.filter(judul__icontains=q)

    paginator = Paginator(tips_qs, 10)
    page_number = request.GET.get('page')
    tips = paginator.get_page(page_number)

    return render(request, 'dashboard/tips_list.html', {'tips': tips, 'q': q})

@login_required
@user_passes_test(is_admin)
def tips_create(request):
    kategori_list = Kategori.objects.all()
    if request.method == 'POST':
        TipsCuaca.objects.create(
            judul=request.POST.get('judul'),isi=request.POST.get('isi'),
            kategori_id=request.POST.get('kategori'),
            gambar=request.FILES.get('gambar'),penulis=request.user,
        )
        messages.success(request,'Tips berhasil ditambahkan!')
        return redirect('tips_list_dashboard')
    return render(request,'dashboard/tips_form.html',{'kategori_list':kategori_list,'action':'Tambah'})


@login_required
@user_passes_test(is_admin)
def tips_edit(request, pk):
    tips = get_object_or_404(TipsCuaca, pk=pk)
    kategori_list = Kategori.objects.all()
    if request.method == 'POST':
        tips.judul=request.POST.get('judul'); tips.isi=request.POST.get('isi')
        tips.kategori_id=request.POST.get('kategori')
        if request.FILES.get('gambar'): tips.gambar=request.FILES.get('gambar')
        tips.save()
        messages.success(request,'Tips berhasil diupdate!')
        return redirect('tips_list_dashboard')
    return render(request,'dashboard/tips_form.html',{'tips':tips,'kategori_list':kategori_list,'action':'Edit'})


@login_required
@user_passes_test(is_admin)
def tips_delete(request, pk):
    get_object_or_404(TipsCuaca, pk=pk).delete()
    messages.success(request,'Tips berhasil dihapus!')
    return redirect('tips_list_dashboard')

@login_required
@user_passes_test(is_admin)
def feedback_dashboard(request):
    q=request.GET.get('q',''); rating=request.GET.get('rating','')
    fbs=Feedback.objects.order_by('-dibuat')
    if q: fbs=fbs.filter(nama__icontains=q)
    if rating: fbs=fbs.filter(rating=rating)

    paginator = Paginator(fbs, 10)
    page_number = request.GET.get('page')
    feedbacks = paginator.get_page(page_number)

    return render(request,'dashboard/feedback_list.html',{'feedbacks':feedbacks,'q':q,'rating_filter':rating})


@login_required
@user_passes_test(is_admin)
def feedback_delete(request, pk):
    get_object_or_404(Feedback, pk=pk).delete()
    messages.success(request,'Feedback berhasil dihapus!')
    return redirect('feedback_dashboard')

@login_required
@user_passes_test(is_admin)
def feedback_balas(request, pk):
    fb = get_object_or_404(Feedback, pk=pk)
    if request.method == 'POST':
        fb.balasan_admin = request.POST.get('balasan_admin', '').strip()
        fb.save()
        messages.success(request, 'Balasan berhasil disimpan!')
    return redirect('feedback_dashboard')

@login_required
@user_passes_test(is_admin)
def users_dashboard(request):
    users=User.objects.all().order_by('-date_joined')
    return render(request,'dashboard/users_list.html',{'users':users})


@login_required
@user_passes_test(is_admin)
def kategori_dashboard(request):
    kategori = Kategori.objects.all()
    return render(request, 'dashboard/kategori_list.html', {'kategori': kategori})


@login_required
@user_passes_test(is_admin)
def kategori_tambah(request):
    kategori = Kategori.objects.all()
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        if nama:
            Kategori.objects.create(
                nama=nama,
                icon='',
                warna='blue',
                deskripsi='',
            )
            messages.success(request, f'Kategori "{nama}" berhasil ditambahkan!')
            return redirect('kategori_dashboard')
        else:
            messages.error(request, 'Nama kategori tidak boleh kosong!')
    return render(request, 'dashboard/kategori_form.html', {'kategori': kategori})

@login_required
@user_passes_test(is_admin)
def kategori_edit(request, pk):
    kat = get_object_or_404(Kategori, pk=pk)
    kategori = Kategori.objects.exclude(pk=pk)
    if request.method == 'POST':
        nama = request.POST.get('nama', '').strip()
        if nama:
            kat.nama = nama
            kat.save()
            messages.success(request, f'Kategori berhasil diubah menjadi "{nama}"!')
            return redirect('kategori_dashboard')
        else:
            messages.error(request, 'Nama kategori tidak boleh kosong!')
    return render(request, 'dashboard/kategori_form.html', {
        'kategori': kategori, 'edit_kategori': kat, 'action': 'Edit',
    })

@login_required
@user_passes_test(is_admin)
def kategori_delete(request, pk):
    get_object_or_404(Kategori, pk=pk).delete()
    messages.success(request, 'Kategori dihapus!')
    return redirect('kategori_dashboard')


@login_required
@user_passes_test(is_admin)
def galeri_dashboard(request):
    filter_status = request.GET.get('status','semua')
    galeri = Galeri.objects.select_related('diunggah_oleh','kategori').order_by('-dibuat')
    if filter_status == 'pending':
        galeri = galeri.filter(disetujui=False)
    elif filter_status == 'approved':
        galeri = galeri.filter(disetujui=True)
    return render(request,'dashboard/galeri_list.html',{
        'galeri':galeri,'filter_status':filter_status,
        'pending_count':Galeri.objects.filter(disetujui=False).count(),
    })


@login_required
@user_passes_test(is_admin)
def galeri_approve(request, pk):
    g = get_object_or_404(Galeri, pk=pk)
    g.disetujui = True; g.save()
    messages.success(request,f'Foto "{g.judul}" disetujui!')
    return redirect('galeri_dashboard')


@login_required
@user_passes_test(is_admin)
def galeri_reject(request, pk):
    g = get_object_or_404(Galeri, pk=pk)
    g.delete()
    messages.success(request,'Foto ditolak dan dihapus.')
    return redirect('galeri_dashboard')


@login_required
@user_passes_test(is_admin)
def galeri_delete_admin(request, pk):
    get_object_or_404(Galeri, pk=pk).delete()
    messages.success(request,'Foto berhasil dihapus!')
    return redirect('galeri_dashboard')


def peta_cuaca(request):
    return render(request, 'peta_cuaca.html', {
        'OPENWEATHER_API_KEY': settings.OPENWEATHER_API_KEY,
    })


def api_cuaca_lokasi(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    nama_override = request.GET.get('nama', '').strip()

    if not lat or not lon:
        return JsonResponse({'error': 'Parameter lat dan lon wajib.'}, status=400)

    API = settings.OPENWEATHER_API_KEY
    try:
        url = (
            f'https://api.openweathermap.org/data/2.5/weather'
            f'?lat={lat}&lon={lon}&appid={API}&units=metric&lang=id'
        )
        resp = requests.get(url, timeout=8)
        data = resp.json()

        try:
            cod = int(data.get('cod', 0))
        except (ValueError, TypeError):
            cod = 0
        if cod != 200:
            return JsonResponse({'error': 'Lokasi tidak ditemukan.'}, status=404)

        main_raw = data['weather'][0]['main'].lower()
        desc_raw = data['weather'][0]['description'].lower()
        sunrise  = data['sys']['sunrise']
        sunset   = data['sys']['sunset']
        now_ts   = data['dt']
        is_day   = 1 if sunrise < now_ts < sunset else 0

        emoji = WEATHER_EMOJI.get(desc_raw, '🌤️')

        aqi_data = None
        try:
            url_aq = (
                f'https://api.openweathermap.org/data/2.5/air_pollution'
                f'?lat={lat}&lon={lon}&appid={API}'
            )
            raq = requests.get(url_aq, timeout=6).json()
            aqi_val = raq['list'][0]['main']['aqi']
            aqi_data = aqi_info(aqi_val)
        except Exception:
            pass

        result = {
            'kota': nama_override if nama_override else data['name'],
            'negara':    data['sys']['country'],
            'lat':       float(lat),
            'lon':       float(lon),
            'suhu':      round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'suhu_min':  round(data['main']['temp_min']),
            'suhu_max':  round(data['main']['temp_max']),
            'deskripsi': data['weather'][0]['description'].title(),
            'kelembaban': data['main']['humidity'],
            'angin':     round(data['wind']['speed'] * 3.6, 1),
            'wind_dir':  wind_direction(data['wind'].get('deg')),
            'visibilitas': round(data.get('visibility', 0) / 1000, 1),
            'tekanan':   data['main']['pressure'],
            'icon':      data['weather'][0]['icon'],
            'emoji':     emoji,
            'main_raw':  main_raw,
            'is_day':    is_day,
            'aqi':       aqi_data,
        }
        return JsonResponse(result)

    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Koneksi ke server cuaca timeout.'}, status=503)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_autocomplete_kota(request):
    """
    Endpoint autocomplete — Nominatim (OSM).
    Indonesia diprioritaskan, tanpa duplikat.

    Satu-satunya tambahan dari versi awal: CACHE hasil per query
    selama 5 menit, supaya ketikan berulang dalam rentang waktu
    dekat tidak menembak ulang ke Nominatim. Ini murni mengurangi
    delay & jumlah request — urutan, filter, dan dedup TIDAK diubah.
    """
    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'results': []})

    from django.core.cache import cache
    cache_key = f"ac_kota_{q.lower()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return JsonResponse({'results': cached})

    try:
        COUNTRY_NAMES = {
            'ID': 'Indonesia',
            'US': 'Amerika Serikat', 'GB': 'Inggris', 'AU': 'Australia',
            'MY': 'Malaysia', 'SG': 'Singapura', 'PH': 'Filipina',
            'TH': 'Thailand', 'VN': 'Vietnam', 'JP': 'Jepang',
            'CN': 'China', 'IN': 'India', 'KR': 'Korea Selatan',
            'DE': 'Jerman', 'FR': 'Prancis', 'IT': 'Italia',
            'BR': 'Brasil', 'CA': 'Kanada', 'MX': 'Meksiko',
            'NL': 'Belanda', 'ES': 'Spanyol', 'PT': 'Portugal',
            'RU': 'Rusia', 'TR': 'Turki', 'EG': 'Mesir',
            'SA': 'Arab Saudi', 'AE': 'UEA', 'ZA': 'Afrika Selatan',
            'NZ': 'Selandia Baru', 'AR': 'Argentina', 'CL': 'Cile',
            'PK': 'Pakistan', 'BD': 'Bangladesh', 'NG': 'Nigeria',
            'KE': 'Kenya', 'GH': 'Ghana', 'ET': 'Ethiopia',
        }

        headers = {'User-Agent': 'SkyWise/1.0 (weather app)'}

        url_id = (
            f'https://nominatim.openstreetmap.org/search'
            f'?q={q}&countrycodes=ID&format=json&limit=5&addressdetails=1&accept-language=id'
        )
        data_id = requests.get(url_id, timeout=5, headers=headers).json() or []

        url_global = (
            f'https://nominatim.openstreetmap.org/search'
            f'?q={q}&format=json&limit=10&addressdetails=1&accept-language=id'
        )
        data_global = requests.get(url_global, timeout=5, headers=headers).json() or []

        combined = []
        seen_identity = set()

        def identity_key(item):
            name = item.get('display_name', '').lower().strip()[:40]
            lat  = round(float(item.get('lat', 0)), 2)
            lon  = round(float(item.get('lon', 0)), 2)
            return (name, lat, lon)

        for item in data_id:
            ik = identity_key(item)
            if ik not in seen_identity:
                seen_identity.add(ik)
                combined.append(item)

        for item in data_global:
            ik = identity_key(item)
            if ik not in seen_identity:
                seen_identity.add(ik)
                combined.append(item)

        results = []
        for item in combined[:8]:
            address = item.get('address', {})
            lat     = item.get('lat')
            lon     = item.get('lon')
            osm_type = item.get('type', '')

            is_subcity = osm_type in OSM_SUBCITY_TYPES

            nama = (
                address.get('city') or
                address.get('town') or
                address.get('village') or
                address.get('suburb') or
                address.get('county') or
                address.get('state') or
                address.get('country') or
                item.get('name') or
                item.get('display_name', '').split(',')[0]
            )

            state        = address.get('state', '')
            country_code = address.get('country_code', '').upper()
            negara_nama  = COUNTRY_NAMES.get(country_code, address.get('country', country_code))

            parts = [p for p in [nama, state, negara_nama] if p and p.lower() != nama.lower()]
            label = f"{nama}, {' — '.join(parts)}" if parts else nama

            if is_subcity:
                label += ' ⚠️'

            results.append({
                'kota':       nama,
                'negara':     country_code,
                'state':      state,
                'display':    label,
                'lat':        float(lat),
                'lon':        float(lon),
                'tipe':       osm_type,
                'is_subcity': is_subcity,
            })

        cache.set(cache_key, results, timeout=300)

        return JsonResponse({'results': results})

    except Exception as e:
        return JsonResponse({'results': [], 'error': str(e)})
    
import re

def api_rekomendasi_ai(request):
    kota = request.GET.get('kota', '').strip()
    suhu = request.GET.get('suhu', '0')
    feels_like = request.GET.get('feels_like', '0')
    kelembaban = request.GET.get('kelembaban', '0')
    angin = request.GET.get('angin', '0').replace(',', '.')
    deskripsi = request.GET.get('deskripsi', '')
    negara = request.GET.get('negara', '')
    clouds = request.GET.get('clouds', '0')
    aqi_label = request.GET.get('aqi_label', '')
    aqi_val = request.GET.get('aqi_val', '')

    if not kota:
        return JsonResponse({'error': 'Parameter kota wajib.'}, status=400)

    from django.core.cache import cache
    feels_int_for_cache = int(float(feels_like))
    cache_key = re.sub(r'[^a-z0-9_]', '_', f"ai_v3_{kota.lower()}_{deskripsi.lower()}_{feels_int_for_cache}")
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse({'result': cached})

    try:
        aqi_text = f", kualitas udara AQI {aqi_val} ({aqi_label})" if aqi_val else ""
        prompt = (
            f"Balas HANYA JSON valid, tanpa markdown:\n"
            f'{{"aktivitas": ["...","...","..."], "tips_pakaian": ["...","..."]}}\n\n'
            f"Cuaca {kota}, {negara}: {deskripsi}, {suhu}°C (terasa {feels_like}°C), "
            f"kelembapan {kelembaban}%, angin {angin} km/h{aqi_text}.\n\n"
            f"aktivitas: spesifik dengan jam aman (contoh: 'Jogging sebelum 07.00 — suhu masih {feels_like}°C'). "
            f"tips_pakaian: berdasarkan suhu terasa dan kelembapan. Singkat, 2 item saja."
        )
        ai_resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Kamu adalah asisten cuaca profesional SkyWise AI. Selalu balas dalam format JSON valid saja, tanpa markdown."},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "max_tokens": 200
            },
            timeout=15
        )
        resp_json = ai_resp.json()
        if "error" in resp_json:
            raise Exception(resp_json["error"].get("message", "API Error"))

        raw_content = resp_json["choices"][0]["message"]["content"].strip()
        if raw_content.startswith("```"):
            raw_content = re.sub(r'^```(?:json)?\s*', '', raw_content)
            raw_content = re.sub(r'\s*```$', '', raw_content)
            raw_content = raw_content.strip()

        try:
            result = json.loads(raw_content)
        except json.JSONDecodeError as e:
            raise Exception(f"Format JSON tidak valid dari AI: {e}")

        cache.set(cache_key, result, timeout=3600)
        return JsonResponse({'result': result})

    except Exception as e:
        suhu_int      = int(float(suhu))
        feels_int     = int(float(feels_like))
        kelembaban_int= int(float(kelembaban))
        angin_float   = float(angin)
        clouds_int    = int(float(clouds))
        desc_lower    = deskripsi.lower()

        is_hujan      = any(k in desc_lower for k in ['hujan', 'rain', 'drizzle', 'gerimis'])
        is_badai      = any(k in desc_lower for k in ['badai', 'thunder', 'storm', 'petir'])
        is_berkabut   = any(k in desc_lower for k in ['kabut', 'mist', 'fog', 'haze', 'asap'])
        is_berawan    = any(k in desc_lower for k in ['berawan', 'cloud', 'mendung', 'overcast'])
        is_cerah      = any(k in desc_lower for k in ['cerah', 'clear', 'sunny'])
        is_salju      = any(k in desc_lower for k in ['salju', 'snow'])
        is_angin      = angin_float >= 40

        if is_badai:
            akt = [
                "Tetap di dalam ruangan — badai petir aktif sangat berbahaya",
                "Jauhi jendela, pintu, dan benda logam selama badai berlangsung",
                "Matikan peralatan elektronik yang tidak digunakan",
            ]
        elif is_hujan:
            if feels_int >= 30:
                akt = [
                    f"Hujan turun — hindari aktivitas outdoor meski terasa {feels_int}°C",
                    "Jika terpaksa keluar, siapkan jas hujan dan waspadai jalan licin",
                    "Manfaatkan waktu untuk aktivitas indoor yang produktif",
                ]
            else:
                akt = [
                    "Hujan aktif — tunda aktivitas outdoor hingga reda",
                    "Siapkan jas hujan atau payung jika harus keluar",
                    "Hindari area rawan banjir dan jalanan licin",
                ]
        elif is_berkabut:
            akt = [
                "Visibilitas rendah — kurangi kecepatan berkendara dan nyalakan lampu",
                "Tunda aktivitas outdoor jika kabut masih tebal",
                "Gunakan masker jika kualitas udara buruk akibat kabut asap",
            ]
        elif is_salju:
            akt = [
                "Salju turun — hindari berkendara jika tidak perlu",
                "Waspadai permukaan beku dan jalanan licin",
                "Aktivitas indoor lebih disarankan dalam kondisi ini",
            ]
        elif is_angin:
            akt = [
                f"Angin kencang {angin_float:.0f} km/h — hindari aktivitas di area terbuka",
                "Amankan benda-benda ringan di luar rumah",
                "Waspada di daerah pesisir dan dataran tinggi",
            ]
        elif is_berawan:
            if feels_int >= 32:
                akt = [
                    f"Mendung tapi terasa panas {feels_int}°C — aman outdoor pagi dan sore",
                    "Jogging atau bersepeda sebelum 08.00 atau setelah 16.00",
                    "Siang hari lebih nyaman beraktivitas di dalam ruangan",
                ]
            else:
                akt = [
                    f"Berawan nyaman {feels_int}°C — cocok untuk aktivitas outdoor",
                    "Jogging, bersepeda, atau piknik bisa dilakukan sepanjang hari",
                    "Pantau potensi hujan jika awan semakin gelap",
                ]
        elif is_cerah:
            if feels_int >= 36:
                akt = [
                    f"Cerah tapi sangat terik {feels_int}°C — hindari outdoor 10.00–16.00",
                    "Olahraga hanya sebelum 07.00 atau setelah 17.00",
                    "Gunakan tabir surya SPF 30+ dan perbanyak minum air putih",
                ]
            elif feels_int >= 30:
                akt = [
                    f"Cerah {feels_int}°C — aman outdoor di pagi dan sore hari",
                    "Waktu terbaik: 06.00–09.00 atau 15.30–18.00",
                    "Siang hari istirahat di tempat teduh atau indoor",
                ]
            else:
                akt = [
                    f"Cuaca cerah dan nyaman {feels_int}°C — ideal untuk aktivitas luar ruangan",
                    "Cocok untuk jogging, bersepeda, hiking, atau piknik",
                    "Nikmati sinar matahari pagi antara 07.00–10.00",
                ]
        else:
            if feels_int >= 35:
                akt = [
                    f"Suhu terasa sangat panas {feels_int}°C — hindari outdoor siang hari",
                    "Aktivitas ringan hanya sebelum 07.00 atau setelah 17.00",
                    "Prioritaskan aktivitas indoor ber-AC sepanjang siang",
                ]
            elif feels_int >= 28:
                akt = [
                    f"Terasa hangat {feels_int}°C — aman outdoor pagi dan sore",
                    "Jogging atau bersepeda lebih nyaman sebelum 08.00",
                    "Siang hari cocok untuk aktivitas indoor atau teduh",
                ]
            else:
                akt = [
                    f"Suhu sejuk {feels_int}°C — nyaman untuk berbagai aktivitas",
                    "Cocok untuk olahraga outdoor kapan saja",
                    "Pantau prakiraan cuaca berkala untuk antisipasi perubahan",
                ]

        if is_badai or is_hujan:
            tips = [
                "Wajib bawa jas hujan atau payung yang kuat",
                "Hindari pakaian berbahan katun tipis — cepat basah dan lama kering",
            ]
        elif is_berkabut:
            tips = [
                "Gunakan masker N95 jika kualitas udara buruk",
                "Jaket tipis disarankan — kabut biasanya disertai suhu lebih rendah",
            ]
        elif is_salju:
            tips = [
                "Pakaian berlapis wajib: thermal, sweater, jaket tebal",
                "Kenakan boots anti-selip dan sarung tangan untuk perlindungan ekstra",
            ]
        elif suhu_int >= 32 and kelembaban_int >= 70:
            tips = [
                "Pakaian katun tipis berwarna terang — menyerap keringat dan memantulkan panas",
                f"Kelembapan {kelembaban_int}% — tubuh sulit berkeringat, perbanyak minum air putih",
            ]
        elif suhu_int >= 32:
            tips = [
                "Pakaian tipis berbahan katun atau linen, hindari warna gelap",
                "Gunakan tabir surya SPF 30+ jika beraktivitas di luar ruangan",
            ]
        elif suhu_int >= 20:
            tips = [
                "Pakaian ringan sudah cukup, siapkan jaket tipis untuk malam",
                f"Kelembapan {kelembaban_int}% — kondisi cukup nyaman di kulit",
            ]
        else:
            tips = [
                "Pakaian berlapis — bisa dilepas satu per satu saat suhu naik",
                "Jaket atau sweater wajib, terutama pagi dan malam hari",
            ]

        return JsonResponse({'result': {'aktivitas': akt, 'tips_pakaian': tips}})

def api_geocode(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'results': []})
    try:
        headers = {'User-Agent': 'SkyWise/1.0'}
        url = (
            f'https://nominatim.openstreetmap.org/search'
            f'?q={q}&format=json&limit=5&addressdetails=1&accept-language=id'
        )
        resp = requests.get(url, timeout=8, headers=headers).json()
        return JsonResponse({'results': resp})
    except Exception as e:
        return JsonResponse({'results': [], 'error': str(e)})