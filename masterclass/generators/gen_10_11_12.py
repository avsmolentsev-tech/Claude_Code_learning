# -*- coding: utf-8 -*-
"""Кейсы 10 (Voice of Customer), 11 (AI-CFO), 12 (AI-аудитор команды)."""
import csv, random, datetime as dt, os, collections
random.seed(101112)

# ─────────────────────────── 10. VOICE OF CUSTOMER: 200 отзывов ───────────────────────────
OUT10='site/cases/10-voc'; os.makedirs(OUT10, exist_ok=True)
COMPANY='ООО «ГидроТерм»'; COMP=['ООО «АкваЛайн»','АО «ТермоПро»']
SRC=['Яндекс.Карты','Отзовик','Письмо в поддержку','NPS-опрос','Telegram-чат','2ГИС','Претензия']
# Заложенные паттерны: главная боль — сроки доставки; вторая — качество сервисного выезда;
# главная любовь — техподдержка инженеров; у конкурента А та же боль сильнее, у Б — цены.
PAIN = {
 'сроки поставки':['Обещали 2 недели — привезли через полтора месяца','Сроки сорваны второй раз подряд',
   'Пришлось останавливать участок, ждали насос 5 недель','Менеджер не предупредил о задержке'],
 'сервисный выезд':['Инженер приехал без нужной детали','Ждали выезда 9 дней','Приехали, посмотрели, уехали — проблема осталась'],
 'документы':['Долго не присылали закрывающие документы','В счёте ошиблись в реквизитах','УПД пришёл с опозданием на месяц'],
 'цена':['Дороже конкурентов на 15%','Подняли цену без предупреждения','Скидку так и не согласовали'],
 'комплектация':['Прислали не ту модификацию','В комплекте не было ответных фланцев','Пересорт по крепежу'],
}
LOVE = {
 'техподдержка':['Инженер по телефону помог решить за 10 минут','Отвечают быстро и по делу','Подобрали замену снятой с производства модели'],
 'качество оборудования':['Насос работает третий год без нареканий','Качество сборки заметно выше китайских аналогов'],
 'менеджер':['Менеджер ведёт до конца, не бросает','Всегда на связи, даже в выходные'],
}
rows=[]
def add(company, theme, text, tone, src=None, d=None):
    rows.append({'Дата': (d or dt.date(2026,9,13)-dt.timedelta(days=random.randint(0,400))).isoformat(),
      'Компания':company,'Источник':src or random.choice(SRC),'Оценка':(random.randint(1,3) if tone=='негатив' else random.randint(4,5)),
      'Тональность':tone,'Тема (учебная метка)':theme,'Текст отзыва':text})
# наша компания: 120 отзывов с перекосом в сроки
for _ in range(46): add(COMPANY,'сроки поставки',random.choice(PAIN['сроки поставки']),'негатив')
for _ in range(24): add(COMPANY,'сервисный выезд',random.choice(PAIN['сервисный выезд']),'негатив')
for _ in range(10): add(COMPANY,'документы',random.choice(PAIN['документы']),'негатив')
for _ in range(8):  add(COMPANY,'комплектация',random.choice(PAIN['комплектация']),'негатив')
for _ in range(20): add(COMPANY,'техподдержка',random.choice(LOVE['техподдержка']),'позитив')
for _ in range(12): add(COMPANY,'качество оборудования',random.choice(LOVE['качество оборудования']),'позитив')
# конкурент А: сроки ещё хуже; конкурент Б: главная боль — цена
for _ in range(28): add(COMP[0],'сроки поставки',random.choice(PAIN['сроки поставки']),'негатив')
for _ in range(6):  add(COMP[0],'техподдержка',random.choice(LOVE['техподдержка']),'позитив')
for _ in range(6):  add(COMP[0],'цена','У них дешевле, но ждать долго','позитив')
for _ in range(22): add(COMP[1],'цена',random.choice(PAIN['цена']),'негатив')
for _ in range(12): add(COMP[1],'качество оборудования',random.choice(LOVE['качество оборудования']),'позитив')
for _ in range(6):  add(COMP[1],'сроки поставки','Привезли точно в срок','позитив')
random.shuffle(rows)
our=[r for r in rows if r['Компания']==COMPANY]
th=collections.Counter(r['Тема (учебная метка)'] for r in our if r['Тональность']=='негатив')
assert len(rows)>=200, f'нужно >=200 отзывов, получилось {len(rows)}'
assert th.most_common(1)[0][0]=='сроки поставки', 'главная боль должна быть про сроки'
assert th.most_common(1)[0][1] > th.most_common(2)[1][1]*1.5, 'боль должна доминировать явно'
cols=list(rows[0].keys())
with open(f'{OUT10}/demo_reviews_200.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
print(f'10. отзывов: {len(rows)} (наших {len(our)}), главная боль: {th.most_common(3)}')

# ─────────────────────────── 11. AI-CFO: P&L + движение денег + выписка ───────────────────────────
# Учебный сюжет: компания ПРИБЫЛЬНА (≈7% годовых), но летом уходит в кассовый разрыв.
# Причина не в убытке, а в деньгах: отсрочка платежей + дивиденды в мае + крупный клиент
# задержал 9 млн на два месяца. Это главный смысл кейса — прибыль и деньги это разные вещи.
OUT11='site/cases/11-cfo'; os.makedirs(OUT11, exist_ok=True)
SEASON={1:.72,2:.85,3:1.05,4:1.02,5:.95,6:.92,7:.62,8:.80,9:1.10,10:1.18,11:1.32,12:1.45}
BUY, DIV, START = 0.355, 6_000_000, 1_200_000
LATE_CLIENT, LATE_SUM = 'АО «Волгаэнерго»', 4_500_000   # просрочка в июне и июле, приходит в сентябре

months=[dt.date(2025+(8+m)//12,(8+m)%12+1,1) for m in range(14)]
rev={d:int(9_800_000*SEASON[d.month]) for d in months}
pnl=[]; cashflow=[]; bank=[]; bal=START
for i,d in enumerate(months[2:],2):
    r=rev[d]; exp={}
    for name,share in [('Закупка товаров и материалов',BUY),('Логистика',0.09),('Аренда',0.05),
                       ('Реклама',0.05),('Налоги',0.07),('Прочее',0.03)]:
        v=r*share
        if name=='Логистика': v*=1.35          # аномалия: логистика дороже рынка
        exp[name]=int(v)
    exp['ФОТ']=int(2_050_000*(1+0.022*(i-2)))   # аномалия: ползучий рост ФОТ
    exp['Подписки и ПО']=96_000+14_000*(i-2)    # аномалия: разрастание подписок
    tot=sum(exp.values())
    receipts=int(0.10*r + 0.45*rev[months[i-1]] + 0.45*rev[months[i-2]])
    note=''
    if d.month in (6,7):  receipts-=LATE_SUM; note=f'{LATE_CLIENT} задержал оплату {LATE_SUM:,} ₽'.replace(',',' ')
    if d.month==9:        receipts+=LATE_SUM*2; note=f'{LATE_CLIENT} погасил просроченную задолженность'
    payments=tot+(DIV if d.month==5 else 0)
    if d.month==5: note='Выплата дивидендов собственнику'
    bal+=receipts-payments
    pnl.append({'Месяц':d.strftime('%Y-%m'),'Выручка':r,**exp,'Итого расходы':tot,'Прибыль':r-tot,
                'Рентабельность, %':round((r-tot)/r*100,1)})
    cashflow.append({'Месяц':d.strftime('%Y-%m'),'Поступления':receipts,'Платежи':payments,
                     'Движение за месяц':receipts-payments,'Остаток на конец месяца':int(bal),'Событие':note})
    for name,v in exp.items():
        for _ in range(random.randint(2,4)):
            bank.append({'Дата':(d+dt.timedelta(days=random.randint(0,27))).isoformat(),
              'Контрагент':f'{random.choice(["ООО","АО","ИП"])} «{random.choice(["Поставщик-Н","ТехСнаб","ЛогистикПро","Арендодатель","МедиаПлюс","Сервис-Т"])}»',
              'Назначение платежа':f'Оплата: {name.lower()}','Статья':name,'Тип':'Расход','Сумма':int(v/3)})
    if d.month==5:
        bank.append({'Дата':d.replace(day=20).isoformat(),'Контрагент':'Смирнов А. (учредитель)',
          'Назначение платежа':'Выплата дивидендов','Статья':'Дивиденды','Тип':'Расход','Сумма':DIV})
    for _ in range(random.randint(6,9)):
        bank.append({'Дата':(d+dt.timedelta(days=random.randint(0,27))).isoformat(),
          'Контрагент':random.choice([LATE_CLIENT,'ПАО «Северсталь-Ремонт»','ООО «ТеплоСеть-Урал»','АО «Сибнефтемаш»','ООО «ГК Промальянс»']),
          'Назначение платежа':'Оплата по счёту','Статья':'Выручка','Тип':'Приход','Сумма':int(max(receipts,0)/7)})

yr_rev=sum(p['Выручка'] for p in pnl); yr_pr=sum(p['Прибыль'] for p in pnl)
neg=[c['Месяц'] for c in cashflow if c['Остаток на конец месяца']<0]
assert 0.04 < yr_pr/yr_rev < 0.12, f'нереалистичная годовая маржа: {yr_pr/yr_rev*100:.1f}%'
assert neg, 'должен быть кассовый разрыв'
assert all(p['Прибыль']>0 for p in pnl[:4]), 'в сезон компания должна быть прибыльной'
fot=[p['ФОТ'] for p in pnl]; assert fot[-1]/fot[0] > 1.2, 'ФОТ должен заметно вырасти'
bank.sort(key=lambda r:r['Дата'])
for fn,data in [('demo_pnl_12_months.csv',pnl),('demo_cashflow_12_months.csv',cashflow),('demo_bank_statement.csv',bank)]:
    with open(f'{OUT11}/{fn}','w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)
print(f'11. год: выручка {yr_rev:,.0f}, прибыль {yr_pr:,.0f} ({yr_pr/yr_rev*100:.1f}%)'.replace(',',' '))
print(f'    кассовый разрыв: {neg}, дно {min(c["Остаток на конец месяца"] for c in cashflow):,.0f} ₽'.replace(',',' '))
print(f'    рост ФОТ ×{fot[-1]/fot[0]:.2f}; операций в выписке: {len(bank)}')

# ─────────────────────────── 12. АУДИТОР КОМАНДЫ: 12 сотрудников ───────────────────────────
OUT12='site/cases/12-team'; os.makedirs(OUT12, exist_ok=True)
PEOPLE=[('Смирнов А.','Собственник'),('Ковалёва Н.','Руководитель отдела продаж'),('Титов Р.','Менеджер по продажам'),
 ('Лапина О.','Менеджер по продажам'),('Морозов В.','Главный инженер'),('Егорова С.','Инженер-конструктор'),
 ('Зайцев Д.','Снабжение'),('Никитина П.','Бухгалтер'),('Орлов К.','Мастер участка'),('Родин М.','Мастер участка'),
 ('Фомина Ю.','Маркетолог'),('Шилов Т.','IT-специалист')]
TASK_T=['Согласовать КП','Подготовить расчёт','Заказать материалы','Ответить клиенту','Настроить отчёт',
 'Проверить документы','Составить график','Согласовать бюджет','Утвердить макет','Разобрать рекламацию']
tasks=[]; tid=0
for i in range(260):
    tid+=1
    who,role=random.choice(PEOPLE)
    # перегруз: собственник и главный инженер держат на себе согласования
    if random.random()<0.30: who,role=random.choice([('Смирнов А.','Собственник'),('Морозов В.','Главный инженер')])
    created=dt.date(2026,9,13)-dt.timedelta(days=random.randint(1,120))
    due=created+dt.timedelta(days=random.randint(2,21))
    done_prob=0.55 if who in ('Смирнов А.','Морозов В.') else 0.8
    done = random.random()<done_prob
    closed = due+dt.timedelta(days=random.randint(-4,14)) if done else None
    no_owner = random.random()<0.07
    tasks.append({'ID':f'T-{1000+tid}','Задача':random.choice(TASK_T),
      'Ответственный':('' if no_owner else who),'Роль':('' if no_owner else role),
      'Создана':created.isoformat(),'Срок':due.isoformat(),
      'Статус':('Выполнена' if done else random.choice(['В работе','Ожидает решения','Просрочена'])),
      'Закрыта':(closed.isoformat() if closed else ''),
      'Ждёт решения от':random.choice(['','','','Смирнов А.','Морозов В.']),
      'Возвратов на доработку':random.choices([0,0,0,1,2,3],weights=[50,20,10,10,7,3])[0],
      'Отдел':random.choice(['Продажи','Производство','Снабжение','Финансы','Маркетинг','IT'])})
cnt=collections.Counter(t['Ответственный'] for t in tasks if t['Ответственный'])
waits=collections.Counter(t['Ждёт решения от'] for t in tasks if t['Ждёт решения от'])
no_owner_n=sum(1 for t in tasks if not t['Ответственный'])
assert cnt.most_common(1)[0][0] in ('Смирнов А.','Морозов В.'), 'перегруз должен быть на собственнике/главинженере'
assert no_owner_n>=8, 'должны быть задачи без ответственного'
assert waits['Смирнов А.']>=20, 'должна быть заметная зависимость решений от собственника'
with open(f'{OUT12}/demo_tasks_export.csv','w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(tasks[0].keys())); w.writeheader(); w.writerows(tasks)
print(f'12. задач: {len(tasks)}, перегруз: {cnt.most_common(2)}, без ответственного: {no_owner_n}, ждут собственника: {waits["Смирнов А."]}')
