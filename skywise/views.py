import requests
from django.shortcuts import render

API_KEY = 'caae0a155c936fa0b14394fcd42035dc'  

def index(request):
    return render(request, 'base.html')

def cek_cuaca(request):
    cuaca = None
    forecast = None
    error = None
    kota = ''

    if request.method == 'POST':
        kota = request.POST.get('kota', '')
        
        # Current weather
        url = f'https://api.openweathermap.org/data/2.5/weather?q={kota}&appid={API_KEY}&units=metric&lang=id'
        response = requests.get(url)
        data = response.json()

        if data['cod'] == 200:
            cuaca = {
                'kota': data['name'],
                'negara': data['sys']['country'],
                'suhu': round(data['main']['temp']),
                'deskripsi': data['weather'][0]['description'].title(),
                'kelembaban': data['main']['humidity'],
                'angin': round(data['wind']['speed'] * 3.6, 1),
                'visibilitas': round(data.get('visibility', 0) / 1000, 1),
                'icon': data['weather'][0]['icon'],
            }

            # Forecast 5 hari
            url_forecast = f'https://api.openweathermap.org/data/2.5/forecast?q={kota}&appid={API_KEY}&units=metric&lang=id'
            res_forecast = requests.get(url_forecast)
            data_forecast = res_forecast.json()

            forecast = []
            seen_dates = []
            for item in data_forecast['list']:
                tanggal = item['dt_txt'].split(' ')[0]
                if tanggal not in seen_dates and len(forecast) < 5:
                    seen_dates.append(tanggal)
                    forecast.append({
                        'tanggal': tanggal,
                        'suhu_min': round(item['main']['temp_min']),
                        'suhu_max': round(item['main']['temp_max']),
                        'icon': item['weather'][0]['icon'],
                        'deskripsi': item['weather'][0]['description'].title(),
                    })
        else:
            error = 'Kota tidak ditemukan. Coba cek ejaan kota kamu.'

    return render(request, 'cek_cuaca.html', {
        'cuaca': cuaca,
        'forecast': forecast,
        'error': error,
        'kota': kota,
    })

def galeri(request):
    return render(request, 'galeri.html')

def about_us(request):
    return render(request, 'about_us.html')

def feedback(request):
    return render(request, 'feedback.html')