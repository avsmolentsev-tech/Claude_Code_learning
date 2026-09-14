# -*- coding: utf-8 -*-
"""Кейс 01 «Пульт управления бизнесом»: demo_sales_12_months.
ТЗ: >=1500 строк, 12 месяцев, 5 менеджеров, 20 продуктов, 4 канала, регионы.
Заложенные паттерны (каждый проверяется ассертом в конце):
  A. падение продукта          — у одного продукта выручка 2-го полугодия < 45% первого
  B. менеджер «объём без маржи» — топ-1 по выручке, но маржа ниже среднего на >6 п.п.
  C. дорогой канал             — у одного канала маржа ниже средней на >8 п.п.
  D. сезонность                — декабрь/ноябрь выше июльского провала в >1.6 раза
  E. скачок себестоимости      — у одной группы товаров себестоимость +18% с августа
  F. концентрация на клиентах  — топ-5 клиентов дают >35% выручки
"""
import csv, random, datetime as dt, os, collections

random.seed(20260913)
OUT = 'site/cases/01-dashboard'
os.makedirs(OUT, exist_ok=True)

MANAGERS = ['Астахов И.', 'Белова М.', 'Гурьев П.', 'Дорохина Е.', 'Ким А.']
CHANNELS = ['Прямые продажи', 'Тендеры', 'Маркетплейс', 'Дилеры']
REGIONS  = ['Москва и МО', 'Санкт-Петербург', 'Поволжье', 'Урал', 'Сибирь', 'Юг']
STATUSES = ['Оплачен', 'Оплачен', 'Оплачен', 'Оплачен', 'Частично', 'Ожидает оплаты']

# 20 продуктов: (название, группа, базовая цена, базовая маржа)
PRODUCTS = [
    ('Насос НЦ-50',         'Насосное',    48000,  0.31), ('Насос НЦ-80', 'Насосное', 74000, 0.29),
    ('Насос НЦ-120',        'Насосное',   118000,  0.27), ('Мотор-редуктор МР-3', 'Привод', 39000, 0.34),
    ('Мотор-редуктор МР-7', 'Привод',      61000,  0.32), ('Частотник ЧП-11', 'Привод', 87000, 0.26),
    ('Частотник ЧП-22',     'Привод',     134000,  0.24), ('Задвижка ЗД-100', 'Трубопровод', 22000, 0.38),
    ('Задвижка ЗД-200',     'Трубопровод', 41000,  0.36), ('Клапан КО-50', 'Трубопровод', 15000, 0.40),
    ('Фильтр ФМ-80',        'Трубопровод', 27000,  0.35), ('Теплообменник ТО-40', 'Теплообмен', 156000, 0.22),
    ('Теплообменник ТО-90', 'Теплообмен', 243000,  0.21), ('Градирня ГР-15', 'Теплообмен', 310000, 0.19),
    ('Шкаф управления ШУ-1','Автоматика',  95000,  0.33), ('Шкаф управления ШУ-3', 'Автоматика', 168000, 0.30),
    ('Датчик давления ДД-10','Автоматика',   8500,  0.44), ('Расходомер РМ-5', 'Автоматика', 62000, 0.37),
    ('Сервис: пусконаладка','Услуги',       45000,  0.52), ('Сервис: ТО годовое', 'Услуги', 120000, 0.48),
]
FADING = 'Теплообменник ТО-40'     # паттерн A
VOLUME_MGR = 'Гурьев П.'           # паттерн B
EXPENSIVE_CH = 'Маркетплейс'       # паттерн C
COST_SPIKE_GROUP = 'Привод'        # паттерн E

CLIENTS_BIG = ['АО «Волгаэнерго»', 'ПАО «Северсталь-Ремонт»', 'ООО «ТеплоСеть-Урал»',
               'АО «Сибнефтемаш»', 'ООО «ГК Промальянс»']
CLIENTS_MID = [f'ООО «{n}»' for n in ['Ремстрой', 'Энергопоток', 'ТехноЛайн', 'Гидромаш', 'Аквасервис',
               'Промкомплект', 'СтройИнвест', 'Северный ветер', 'Химпром-Н', 'Агроресурс',
               'Мехзавод №4', 'ТеплоДом', 'Уралснаб', 'Волга-Трейд', 'Энергомонтаж']]
CLIENTS_SMALL = [f'ИП {n}' for n in ['Круглов', 'Матвеев', 'Сазонова', 'Терентьев', 'Юсупов',
                 'Панкратов', 'Ильина', 'Жуков', 'Носов', 'Абрамян']]

MONTH_SEASON = {1:0.72, 2:0.85, 3:1.05, 4:1.02, 5:0.95, 6:0.92,
                7:0.62, 8:0.80, 9:1.10, 10:1.18, 11:1.32, 12:1.45}   # паттерн D

START = dt.date(2025, 9, 1)
rows = []
order_no = 4100

def month_index(d):
    return (d.year - START.year) * 12 + (d.month - START.month)

for m in range(12):
    d0 = dt.date(START.year + (START.month - 1 + m) // 12, (START.month - 1 + m) % 12 + 1, 1)
    season = MONTH_SEASON[d0.month]
    n_orders = int(random.uniform(132, 162) * season)
    for _ in range(n_orders):
        day = random.randint(1, 28)
        date = dt.date(d0.year, d0.month, day)
        # клиент: концентрация на крупных (паттерн F)
        r = random.random()
        if r < 0.42:   client, size = random.choice(CLIENTS_BIG), 'крупный'
        elif r < 0.85: client, size = random.choice(CLIENTS_MID), 'средний'
        else:          client, size = random.choice(CLIENTS_SMALL), 'малый'

        name, group, price, marg = random.choice(PRODUCTS)
        # паттерн A: продукт угасает во втором полугодии
        if name == FADING and m >= 6 and random.random() < 0.78:
            continue
        channel = random.choices(CHANNELS, weights=[0.38, 0.22, 0.24, 0.16])[0]
        # объёмщик берёт ~30% заказов — иначе он не выйдет в топ-1 по выручке со скидками
        manager = random.choices(MANAGERS, weights=[0.18, 0.17, 0.30, 0.18, 0.17])[0]
        # паттерн B: менеджер гонит объём со скидками
        disc = random.uniform(0.0, 0.06)
        if manager == VOLUME_MGR:
            disc = random.uniform(0.10, 0.22)
        # паттерн C: дорогой канал — комиссия съедает маржу
        ch_cost = 0.14 if channel == EXPENSIVE_CH else (0.03 if channel == 'Дилеры' else 0.0)
        qty = random.choices([1,1,1,2,2,3,4,6,10], weights=[30,20,12,12,9,7,5,3,2])[0]
        if size == 'крупный': qty = max(qty, random.choice([2,3,5,8]))

        unit_price = round(price * (1 - disc) * random.uniform(0.98, 1.03))
        revenue = unit_price * qty
        # Себестоимость привязана к ТОВАРУ, а не к выручке: иначе скидка не бьёт по марже
        # (это и есть механика паттерна B — объём даётся ценой, а закупка не дешевеет).
        unit_cost = price * (1 - marg)
        # паттерн E: скачок себестоимости с августа по группе «Привод»
        if group == COST_SPIKE_GROUP and date >= dt.date(2026, 8, 1):
            unit_cost *= 1.18
        cost = round(unit_cost * qty * random.uniform(0.98, 1.02))
        cost += round(revenue * ch_cost)          # комиссия канала
        profit = revenue - cost
        order_no += 1
        rows.append({
            'Дата': date.isoformat(), 'Номер заказа': f'З-{order_no}', 'Клиент': client,
            'Размер клиента': size, 'Менеджер': manager, 'Продукт': name, 'Группа': group,
            'Канал': channel, 'Регион': random.choice(REGIONS), 'Количество': qty,
            'Цена за единицу': unit_price, 'Выручка': revenue, 'Себестоимость': cost,
            'Прибыль': profit, 'Статус оплаты': random.choice(STATUSES),
        })

rows.sort(key=lambda r: r['Дата'])

# ── ПРОВЕРКА ЗАЛОЖЕННЫХ ПАТТЕРНОВ ─────────────────────────────────────────
def agg(key, field='Выручка'):
    d = collections.defaultdict(float)
    for r in rows: d[r[key]] += r[field]
    return d

total_rev = sum(r['Выручка'] for r in rows)
checks = []

h1 = sum(r['Выручка'] for r in rows if r['Продукт']==FADING and month_index(dt.date.fromisoformat(r['Дата']))<6)
h2 = sum(r['Выручка'] for r in rows if r['Продукт']==FADING and month_index(dt.date.fromisoformat(r['Дата']))>=6)
checks.append(('A. падение продукта', h2/h1 < 0.45, f'{FADING}: 2-е полугодие = {h2/h1*100:.0f}% от 1-го'))

mgr_rev = agg('Менеджер'); mgr_prof = agg('Менеджер','Прибыль')
marg = {m: mgr_prof[m]/mgr_rev[m] for m in mgr_rev}
avg_marg = sum(r['Прибыль'] for r in rows)/total_rev
top_mgr = max(mgr_rev, key=mgr_rev.get)
checks.append(('B. объём без маржи', top_mgr==VOLUME_MGR and (avg_marg-marg[top_mgr])>0.06,
               f'{top_mgr}: топ-1 по выручке, маржа {marg[top_mgr]*100:.1f}% против средней {avg_marg*100:.1f}%'))

ch_rev = agg('Канал'); ch_prof = agg('Канал','Прибыль')
ch_marg = {c: ch_prof[c]/ch_rev[c] for c in ch_rev}
checks.append(('C. дорогой канал', (avg_marg-ch_marg[EXPENSIVE_CH])>0.08,
               f'{EXPENSIVE_CH}: маржа {ch_marg[EXPENSIVE_CH]*100:.1f}% против средней {avg_marg*100:.1f}%'))

by_month = collections.defaultdict(float)
for r in rows: by_month[r['Дата'][:7]] += r['Выручка']
jul = min(by_month.values()); peak = max(by_month.values())
checks.append(('D. сезонность', peak/jul > 1.6, f'пик/провал = {peak/jul:.2f}×'))

pre = [r for r in rows if r['Группа']==COST_SPIKE_GROUP and r['Дата'] < '2026-08-01']
post= [r for r in rows if r['Группа']==COST_SPIKE_GROUP and r['Дата'] >= '2026-08-01']
cs_pre = sum(r['Себестоимость'] for r in pre)/sum(r['Выручка'] for r in pre)
cs_post= sum(r['Себестоимость'] for r in post)/sum(r['Выручка'] for r in post)
checks.append(('E. скачок себестоимости', cs_post/cs_pre > 1.12,
               f'{COST_SPIKE_GROUP}: доля себестоимости {cs_pre*100:.1f}% → {cs_post*100:.1f}%'))

cl = agg('Клиент'); top5 = sorted(cl.values(), reverse=True)[:5]
checks.append(('F. концентрация клиентов', sum(top5)/total_rev > 0.35,
               f'топ-5 клиентов = {sum(top5)/total_rev*100:.0f}% выручки'))

print(f'строк: {len(rows)}, месяцев: {len(by_month)}, выручка: {total_rev:,.0f} ₽'.replace(',',' '))
ok = True
for name, passed, detail in checks:
    print(f'  {"OK " if passed else "ПРОВАЛ"} {name}: {detail}')
    ok &= passed
assert ok, 'не все паттерны заложены'

# ── ЗАПИСЬ ────────────────────────────────────────────────────────────────
cols = list(rows[0].keys())
with open(f'{OUT}/demo_sales_12_months.csv','w',newline='',encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

from openpyxl import Workbook
from openpyxl.styles import Font
wb = Workbook(); ws = wb.active; ws.title = 'Продажи'
ws.append(cols)
for c in ws[1]: c.font = Font(bold=True)
for r in rows: ws.append([r[c] for c in cols])
ws.freeze_panes = 'A2'
for i, c in enumerate(cols, 1):
    ws.column_dimensions[ws.cell(1,i).column_letter].width = max(12, min(22, len(c)+4))
wb.save(f'{OUT}/demo_sales_12_months.xlsx')
print(f'записано: {OUT}/demo_sales_12_months.csv + .xlsx')
