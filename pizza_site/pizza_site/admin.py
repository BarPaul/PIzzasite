from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, HttpResponse
from . import pizzas
from csv import writer
from os.path import getsize
from pytz import timezone
from datetime import datetime
from .models import get_clients, update_state

def get_formmated(skip_uid=False):
    clients = get_clients("price")
    formatted_clients = []
    for (uid, name, phone, mpizzas, is_completed, timestamp, price) in clients:
        seconds = int(datetime.now(timezone('Europe/Moscow')).timestamp() - timestamp)
        days, hours, minutes = seconds // 3600 // 24, seconds // 3600 % 24, seconds // 60 % 60
        data = [name, "+" + phone, '\n'.join([f'{pizzas['rows'][i]['name']} - {pizza} шт.'
                                                        for i, pizza in enumerate(mpizzas.split(" ")) if int(pizza) > 0]), 
                            bool(is_completed), f'{hours} ч. {minutes} мин.\nназад', f'{price} ₽']
        data.insert(0, uid) if not skip_uid else None
        formatted_clients.append(data)
    return formatted_clients

def dashboard(request):
    return render(request, 'dashboard.html', {
                "columns": ["Имя", "Телефон", "Пиццы", "Выполнен?", "Создан", "Цена"],
                "rows": get_formmated()
    })
    
LOGIN, PASSWORD = '', ''

def admin(request: WSGIRequest):
    if request.method == 'POST':
        if request.POST.get('type') == 'login':
            login, password = request.POST.get('login'), request.POST.get('password')
            if login == LOGIN and password == PASSWORD:
                return dashboard(request)
            return render(request, 'admin.html', {"error": True})
        elif request.POST.get('type') == 'dashboard':
            uid, state = int(request.POST.get('uid')), not request.POST.get('state') == 'True'
            update_state(uid, state)
            return dashboard(request)
        elif request.POST.get('type') == 'download_table':
            with open('temp_table.csv', 'w', encoding='UTF-8-sig', newline='') as f:
                w = writer(f)
                w.writerow(["Имя", "Телефон", "Пиццы", "Выполнен?", "Создан", "Цена"])
                w.writerows(get_formmated(True))
            with open('temp_table.csv', 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/vnd.ms-excel', charset='utf-8')
                response['Content-Disposition'] = 'attachment; filename=temp_table.csv'
                response['Content-Length'] = getsize('temp_table.csv')
            return response
        
    return render(request, 'admin.html', {"error": False})
