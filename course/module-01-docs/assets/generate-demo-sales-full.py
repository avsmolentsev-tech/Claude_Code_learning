# Генератор «взрослой» учебной выгрузки demo-sales-full.csv
# Тот же вымышленный бизнес (офисная мебель, Казань), что и demo-orders.csv,
# но масштаб реального малого бизнеса: ~2 года, ~200 клиентов, ~2300 заказов.
#
# В данные сознательно заложены находки для уроков М1-01 и М4-02:
#   1. Менеджер Козлов раздаёт скидки заметно выше регламента (маржа тает).
#   2. Канал «Тендеры» растёт по выручке, но маржа в нём падает.
#   3. Три крупных клиента «заснули» весной 2026 (риск оттока «чемпионов»).
#   4. Сезонность: пики сентябрь–октябрь и декабрь, провалы январь и лето.
# Всё остальное — правдоподобный шум. Запуск: python3 generate-demo-sales-full.py

import csv
import random
from datetime import date, timedelta

random.seed(42)

TODAY = date(2026, 7, 24)
START = date(2024, 8, 1)
END = date(2026, 7, 20)

FIRST = ["Альфа", "Вектор", "Гранит", "Дельта", "Восход", "Меридиан", "Салют",
         "Прогресс", "Орион", "Спектр", "Форум", "Базис", "Квант", "Титан",
         "Полюс", "Штандарт", "Регион", "Капитал", "Атлант", "Импульс",
         "契", "Люмен", "Синтез", "Модуль", "Крона", "Пилот", "Зенит",
         "Ресурс", "Тандем", "Эталон", "Формат", "Статус", "Ландшафт",
         "Феникс", "Родник", "Каскад", "Мастер", "Профиль", "Гарант", "Актив"]
SECOND = ["", "-Строй", "-Трейд", "-Сервис", "-Групп", "-Пром", "-Волга",
          "-Казань", "-Офис", "-Консалт", "-Лизинг", "-Медиа", "-Лаб"]
IP_NAMES = ["Сидоров", "Кузнецова", "Мельник", "Хайруллин", "Петрова",
            "Гарипов", "Осипова", "Валиев", "Соколова", "Ершов", "Набиуллина",
            "Черкасов", "Юсупова", "Логинов", "Баранова", "Тихонов",
            "Сафина", "Демидов", "Крылова", "Ахметов"]

MANAGERS = ["Волкова", "Громов", "Ефимова", "Козлов", "Лебедев"]
CHANNELS = ["Сайт", "Входящие", "Тендеры", "Партнёры"]

# (товар, категория, базовая цена, доля себестоимости)
PRODUCTS = [
    ("Стол рабочий", "Эконом", 9000, 0.74),
    ("Кресло офисное", "Эконом", 7500, 0.72),
    ("Тумба подкатная", "Эконом", 4500, 0.75),
    ("Стеллаж архивный", "Эконом", 6800, 0.73),
    ("Стол рабочий", "Стандарт", 15000, 0.66),
    ("Кресло офисное", "Стандарт", 14000, 0.64),
    ("Шкаф для документов", "Стандарт", 18500, 0.65),
    ("Стойка ресепшн", "Стандарт", 46000, 0.63),
    ("Стол переговорный", "Премиум", 78000, 0.57),
    ("Кресло руководителя", "Премиум", 38000, 0.56),
    ("Кабинет руководителя (комплект)", "Премиум", 210000, 0.58),
]

SEASON = {1: 0.65, 2: 0.85, 3: 1.0, 4: 1.0, 5: 1.05, 6: 0.8,
          7: 0.75, 8: 0.9, 9: 1.3, 10: 1.35, 11: 1.1, 12: 1.4}


def make_clients():
    clients, used = [], set()
    while len(clients) < 200:
        if random.random() < 0.72:
            name = "ООО «" + random.choice(FIRST).replace("契", "Сириус") + \
                random.choice(SECOND) + "»"
        elif random.random() < 0.6:
            name = "ИП " + random.choice(IP_NAMES)
        else:
            name = "АО «" + random.choice(FIRST).replace("契", "Сириус") + \
                random.choice(SECOND) + "»"
        if name in used:
            continue
        used.add(name)
        size = random.lognormvariate(0, 1.7)           # перекос размеров → честный ABC
        channel = random.choices(CHANNELS, weights=[38, 30, 14, 18])[0]
        # тендерные клиенты чаще появляются во второй половине периода
        if channel == "Тендеры":
            start_offset = random.randint(200, 640)
        else:
            start_offset = random.randint(0, 560)
        manager = random.choices(MANAGERS, weights=[22, 20, 18, 22, 18])[0]
        clients.append({
            "name": name, "size": size, "channel": channel,
            "manager": manager,
            "start": START + timedelta(days=start_offset),
            "rate": min(2.4, 0.16 + size * 0.5),        # заказов в месяц
        })
    return clients


def month_iter():
    d = date(START.year, START.month, 1)
    while d <= END:
        yield d
        d = date(d.year + d.month // 12, d.month % 12 + 1, 1)


clients = make_clients()

# «заснувшие чемпионы»: три клиента из верхушки перестают покупать весной 2026
champions_sleeping = sorted(clients, key=lambda c: -c["size"])[2:7:2]
for i, c in enumerate(champions_sleeping):
    c["sleep_after"] = [date(2026, 3, 15), date(2026, 4, 1), date(2026, 4, 20)][i]

rows = []
oid = 1000
for m in month_iter():
    for c in clients:
        if m < date(c["start"].year, c["start"].month, 1):
            continue
        sleep = c.get("sleep_after")
        expect = c["rate"] * SEASON[m.month]
        n = 0
        r = random.random()
        # пуассон на коленке
        import math
        p = math.exp(-expect)
        cum, k = p, 0
        while r > cum and k < 6:
            k += 1
            p *= expect / k
            cum += p
        n = k
        for _ in range(n):
            day = min(END, date(m.year, m.month, random.randint(1, 28)))
            if sleep and day > sleep:
                continue
            prod = random.choices(
                PRODUCTS,
                weights=[3, 3, 2, 2, 4, 4, 3, 1, 0.8, 1.2, 0.35]
                if c["channel"] != "Тендеры"
                else [6, 6, 3, 4, 3, 3, 2, 0.7, 0.3, 0.5, 0.1])[0]
            name, cat, price, cost_ratio = prod
            qty = max(1, round(random.lognormvariate(0.9, 0.7) *
                               (1.6 if c["channel"] == "Тендеры" else 1.0) *
                               max(0.6, c["size"] ** 0.45)))
            qty = min(qty, 80)
            # скидки: Козлов щедрее регламента; тендеры давят на цену;
            # с 2026 тендерные скидки ещё глубже (маржа канала падает)
            if c["manager"] == "Козлов":
                disc = random.uniform(8, 18)
            else:
                disc = random.uniform(0, 7)
            if qty >= 10:
                disc += 2
            if c["channel"] == "Тендеры":
                disc += 4 + (6.5 if m >= date(2026, 1, 1) else 0)
            disc = round(min(disc, 25), 1)
            total = round(qty * price * (1 - disc / 100))
            cost = round(qty * price * cost_ratio)
            age = (TODAY - day).days
            r2 = random.random()
            if r2 < 0.07:
                status = "Отменён"
            elif age < 30 and r2 < 0.35:
                status = "Ожидает оплаты"
            else:
                status = "Оплачен"
            rows.append([oid, day.isoformat(), c["name"], c["manager"],
                         c["channel"], name, cat, qty, price, disc,
                         total, cost, status])
            oid += 1

rows.sort(key=lambda r: r[1])
for i, r in enumerate(rows):
    r[0] = i + 1

out = "demo-sales-full.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "date", "client", "manager", "channel", "product",
                "category", "qty", "price", "discount_pct", "total",
                "cost", "status"])
    w.writerows(rows)

print(f"{out}: {len(rows)} строк, {len(clients)} клиентов, "
      f"{rows[0][1]} — {rows[-1][1]}")
print("Заснувшие чемпионы:", [c["name"] for c in champions_sleeping])
