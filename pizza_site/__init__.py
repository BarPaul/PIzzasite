from json import load
from django.core.handlers.wsgi import WSGIRequest
from requests import get
from re import search
from .models import save_client
from django.shortcuts import render

pizzas = load(open('pizza_site/pizzas.json', encoding='utf-8'))

def check_phone(phone):
    clear_phone = ''.join(filter(str.isdigit, phone))
    return search(r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$', clear_phone)

TOKEN = ""

def on_post(request):
    name, phone = request.POST.get("name"), request.POST.get("phone")
    piccas = [v for k, v in request.POST.items() if k.startswith('pizza_')]
    if not check_phone(phone):
        pizzas['is_error'] = True
        pizzas['error_message'] = "Неккоректный телефон!"
        return
    if any(picca.startswith("-") for picca in piccas) or all(int(picca) == 0 for picca in piccas):
        pizzas['is_error'] = True
        pizzas['error_message'] = "Выберите какую пиццу заказать!"
        return
    formatted_text, total = f'Имя: {name}\nТелефон: +{phone.replace("+", "")}\nПиццы:\n', 0 
    for i, picca in enumerate(piccas):
        formatted_text += f'{pizzas['rows'][i]['name']} - {picca} шт. - {int(picca) * pizzas['rows'][i]['price']} рублей\n'
        total += int(picca) * pizzas['rows'][i]['price']
    formatted_text += f"Всего: {total} рублей"
    get(f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=1843313209&text={formatted_text}')
    save_client(name, phone, total, *piccas)
    pizzas['is_error'] = False

def index(request: WSGIRequest):
    if request.method == 'POST':
        on_post(request)
    return render(request, 'index.html', pizzas)
