# -*- coding: utf-8 -*-
"""Сборка комплекта из реестра cases.py: README, промпты, шпаргалка, архивы, страница сайта."""
import os, sys, html, zipfile, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cases import CASES, COMMON_RULES, DEPTS

ROOT='site/cases'
def prompt_body(c):
    """Промпт, который участник копирует целиком. Всё, что нужно подставить руками,
    вынесено наверх в квадратные скобки — иначе человек не понимает, куда вставлять свои данные."""
    steps='\n'.join(f'{i}. {b}' for i,b in enumerate(c['build'],1))
    files='\n'.join(f'   - {f} — {d}' for f,d in c['files'])
    if c.get('slots'):
        slot_lines='\n'.join(f'{label}: [{hint}]' for label,hint in c['slots'])
        inputs = f"""МОИ ДАННЫЕ (замените текст в квадратных скобках, скобки уберите):
{slot_lines}

Учебные файлы для этой практики лежат в той же папке, где ты запущен:
{files}"""
    else:
        inputs = f"""МОИ ДАННЫЕ: подставлять ничего не нужно — файлы уже лежат в той папке, где ты запущен:
{files}
Если хочешь работать на своих данных, положи свой файл в эту же папку и скажи агенту его имя."""
    return f"""Ты — lead developer и product manager. Собери работающий прототип, а не описание.

ЗАДАЧА: {c['title']}. {c['sub']}.
ЦЕЛЬ: {c['goal']}

{inputs}

ЧТО НУЖНО СОБРАТЬ:
{steps}

РЕЗУЛЬТАТ: {c['result']}

КАК РАБОТАТЬ:
1. Сначала выдай короткий план и список файлов, которые создашь.
2. Сразу после плана начинай создавать файлы — не жди отдельной команды и не останавливайся на плане.
3. Запусти решение и покажи мне, как его открыть.
4. Проведи smoke-test: загрузка файла, основные расчёты, нажатие кнопок, поведение на пустых
   данных, поведение на неправильном файле, повторный запуск. Исправь то, что сломалось.
5. Запиши результат проверки в файл TEST_REPORT.md рядом с решением.

ТРЕБОВАНИЯ К РЕШЕНИЮ:
- Работает локально, без обязательных API-ключей. Стек — простой и надёжный.
- Интерфейс на русском: понятные кнопки, перетаскивание файлов мышью, внятные подсказки
  на пустом экране, понятные сообщения об ошибках, кнопка «Начать заново».
- Ничего не выдумывай. Если данных не хватает — скажи об этом прямо и спроси, а не подставляй
  правдоподобные цифры.{(chr(10) + '- ОСОБОЕ ТРЕБОВАНИЕ: ' + c['warn']) if c.get('warn') else ''}"""

def build_readme(c):
    hid='\n'.join(f'- {h}' for h in c['hidden'])
    # Каждый файл — кликабельная ссылка: README.html лежит в той же папке,
    # поэтому относительный путь работает и на сайте, и в распакованном архиве.
    def link(name, folder=''):
        href=(folder+name).replace(' ','%20')
        return f'[{name}]({href})'
    rows=[]
    for f,d in c['files']:
        if f.endswith('/'):
            sub=sorted(os.listdir(f"{ROOT}/{c['slug']}/{f.rstrip('/')}"))
            if len(sub)<=10:
                lst=', '.join(link(x, f) for x in sub)
                rows.append(f'| **{f}** | {d}<br>Файлы ({len(sub)}): {lst} |')
            else:
                head=', '.join(link(x, f) for x in sub[:4])
                rows.append(f'| **{f}** | {d}<br>{len(sub)} файлов, например: {head} … Остальные — в архиве практики. |')
        else:
            rows.append(f'| {link(f)} | {d} |')
    files='\n'.join(rows)
    depts=' · '.join(c['depts'])
    diff={1:'1/3 — простая',2:'2/3 — средняя',3:'3/3 — сложная'}[c['diff']]
    slots_note = ''
    if c.get('slots'):
        slots_note = ('\n> **В промпте есть места, которые нужно заполнить.** Они помечены квадратными скобками: '
                      + ', '.join(f'`{l}`' for l,_ in c['slots'])
                      + '. Замените текст внутри скобок на свои данные и уберите сами скобки.\n')
    else:
        slots_note = ('\n> **Подставлять в промпт ничего не нужно.** Все учебные файлы уже лежат в этой папке, '
                      'агент найдёт их сам — главное запустить его именно здесь.\n')
    return f"""# Практика {c['n']}. {c['title']}

**{c['sub']}**

| | |
|---|---|
| **Для кого** | {depts} |
| **Сложность** | {diff} |
| **Время** | {c['time']} |
| **Что принести** | {c['bring']} |

**Зачем это.** {c['goal']}
**Что получится на выходе.** {c['result']}

---

# Для участника

## Шаг 1. Скачайте и откройте папку практики

**[⬇ Скачать все файлы этой практики одним архивом]({c['slug']}.zip)**

Распакуйте и откройте папку в терминале — или в VS Code через «Файл → Открыть папку».
Запускать агента нужно **именно в этой папке**: так он увидит учебные файлы.
Отдельные файлы можно скачать и по одному — список ниже, в разделе «Что в этой папке».

## Шаг 2. Запустите агента

`claude` — если работаете в Claude Code. `codex` — если в Codex. Промпт для обоих одинаковый.

## Шаг 3. Вставьте промпт
{slots_note}
```
{prompt_body(c)}
```

## Шаг 4. Дальше агент работает сам

Он покажет план и сразу начнёт создавать файлы. Ваше дело — подтверждать действия и читать,
что он делает. Если агент остановился на плане и ждёт — напишите «продолжай, создавай файлы».

## Шаг 5. Проверьте результат

Задание считается выполненным, когда:

- [ ] решение **запущено** и открывается, а не описано словами;
- [ ] основные кнопки и расчёты работают на учебных данных;
- [ ] приложение не падает на пустых данных и на неправильном файле;
- [ ] рядом лежит файл `TEST_REPORT.md` с результатами проверки;
- [ ] вы понимаете, что именно показывает результат, и можете объяснить это вслух за минуту.

## Что в этой папке

| Файл | Что это |
|---|---|
{files}

## Если времени мало или наоборот много

- **Быстрый режим, 10–15 минут.** {c['quick']}
- **Основной режим, {c['time']}.** Всё, что описано выше.
- **Усиленный режим.** {c['strong']}
{('''
## Важное ограничение

''' + c['warn']) if c.get('warn') else ''}
---

# Что искать в данных

## Находки, которые заложены специально

Учебные данные сгенерированы так, что в них заложены конкретные находки. Хороший результат —
тот, где агент вытащил их сам. Если не вытащил, задайте наводящий вопрос.

{hid}

## Частые сбои и как их лечить

- **Главный признак провала** — агент выдал текст «как можно сделать» вместо файлов.
  Лечится фразой «не описывай, создавай файлы и запускай».
- **Второй типичный сбой** — агент придумывает данные, которых нет. Спросите: «откуда это число?»
- Застряли дольше пяти минут — прочитайте последний ответ агента вслух. Причина обычно видна сразу.

## Как устроено занятие

Сначала показывают готовый результат — 3–5 минут, чтобы было видно, к чему идём. Потом общий
паттерн работы: данные → промпт → агент пишет код → запуск → проверка. Дальше сама практика,
а в конце каждый показывает «до → после» за две минуты.
"""

# ── README по каждому кейсу ─────────────────────────────────────────────

for c in CASES:
    open(f"{ROOT}/{c['slug']}/README.md",'w',encoding='utf-8').write(build_readme(c))

# ── MASTERCLASS_PROMPTS.md ──────────────────────────────────────────────
p=['# Промпты мастер-класса «AI-компания»','',
   'Скопируйте промпт целиком и вставьте агенту в папке нужной практики.','',
   '> **Claude Code и Codex.** Промпт один и тот же — намеренно. Различие только в файле настроек проекта:',
   '> Claude Code читает `CLAUDE.md`, Codex — `AGENTS.md`. Если работаете обоими агентами, положите в папку',
   '> оба файла с одинаковым содержимым. Система разрешений тоже своя у каждого: в Claude Code подтверждайте',
   '> действия по ходу, в Codex посмотрите `/permissions` до старта.','','---','']
for c in CASES:
    p+=[f"## {c['n']}. {c['title']}",'',f"*{c['sub']}* · {c['time']}",'','```',prompt_body(c),'```','']
open('masterclass/MASTERCLASS_PROMPTS.md','w',encoding='utf-8').write('\n'.join(p))

# ── MASTERCLASS_CHEATSHEET.md ───────────────────────────────────────────
ch=['# Шпаргалка мастер-класса «AI-компания»','',
    '| № | Практика | Что на входе | Что на выходе | Время | WOW |','|---|---|---|---|---|---|']
for c in CASES:
    ch.append(f"| {c['n']} | **{c['title']}** | {c['inp'][:70]}… | {c['result'][:70]}… | {c['time']} | {c['wow'][:60]}… |")
ch+=['','## Драматургия дня','',
 '1. **5 минут** — показать 2–3 готовых WOW DEMO.',
 '2. **10 минут** — объяснить общий паттерн: данные → промпт → агент пишет код → запуск → проверка → улучшение.',
 '3. **30–45 минут** — первая общая практика для всех: «Пульт бизнеса» (01) или «Цифровой продукт» (03).',
 '4. Разделить по отделам и дать профильную практику.',
 '5. Каждая группа показывает за 2 минуты «до → после».',
 '6. Финал — «AI-штаб собственника» (08) как концепция соединения прототипов.','',
 '## Распределение по отделам','',
 '> Таблица собирается из того же реестра, что и бейджи на странице кейсов — расхождений быть не может.','',
 '| Отдел | Практики |','|---|---|'] + [
 f'| {d} | ' + ', '.join(f"{c['n']} {c['title']}" for c in CASES if d in c['depts']) + ' |'
 for d in DEPTS if any(d in c['depts'] for c in CASES)] + ['',
 COMMON_RULES]
open('masterclass/MASTERCLASS_CHEATSHEET.md','w',encoding='utf-8').write('\n'.join(ch))

# ── BRING_YOUR_OWN_DATA.md ──────────────────────────────────────────────
byo="""# Что принести с собой

Всё можно пройти на учебных данных из комплекта — они уже лежат в папках практик.
Но на своих данных результат интереснее, потому что вы сразу увидите свой бизнес.

| Данные | Для каких практик | Как обезличить |
|---|---|---|
| Excel/CSV продаж за 6–12 месяцев | 01 Пульт, 11 AI-CFO | ФИО физлиц → «Клиент N». Названия юрлиц и суммы — не персональные данные |
| URL своего сайта | 02 Сайт, 04 Выручка, 10 Голос клиента | ничего не нужно |
| Описание бизнеса и продуктов | почти все, в том числе 03 Цифровой продукт | — |
| Прайс и 2–3 старых КП | 05 Генератор КП | убрать персональные скидки конкретным лицам |
| 3–10 транскриптов встреч | 06 Мозг компании, 12 Аудитор | заменить имена на роли, если обсуждали людей |
| CRM-выгрузка | 07 Lead Intelligence | контакты физлиц → «Контакт N» |
| Резюме кандидатов, транскрипты интервью, описание вакансии | 13 AI-HR директор | **самые чувствительные данные в курсе.** Убрать ФИО, телефоны, почту, ссылки на соцсети; оставить только опыт и навыки. Пол, возраст и происхождение не приносить вовсе — они не должны участвовать в оценке |
| 3–5 КП поставщиков | 09 AI-закупщик | оставить как есть, это документы юрлиц |
| Банковская выписка, P&L | 11 AI-CFO | убрать номера счетов и карт |
| Экспорт задач | 12 Аудитор, 16 ОТ | имена сотрудников — по договорённости с ними |
| План/факт производства | 14 Production Intelligence | — |
| Нормы выработки и формула премии | 15 Премия | — |
| Инструкции ОТ, карты рисков, фото | 16 Охрана труда | убрать лица людей с фотографий |
| Ничего приносить не нужно | 08 AI-штаб собственника | собирается из результатов других практик |

## Безопасность данных — обязательно прочитать

- Обезличивайте персональные и конфиденциальные данные **до** загрузки в агента.
- Не загружайте пароли, банковские реквизиты, ключи доступа и данные, на обработку которых
  у вас нет разрешения.
- Следуйте политике своей компании и настройкам выбранного сервиса.
- Если сомневаетесь — берите учебные данные из комплекта, они для того и сделаны.
"""
open('masterclass/BRING_YOUR_OWN_DATA.md','w',encoding='utf-8').write(byo)

# копии общих документов в раздаточную папку
for fn in ['MASTERCLASS_PROMPTS.md','MASTERCLASS_CHEATSHEET.md','BRING_YOUR_OWN_DATA.md']:
    open(f'{ROOT}/{fn}','w',encoding='utf-8').write(open(f'masterclass/{fn}',encoding='utf-8').read())

# ── Архивы: по кейсу и общий ────────────────────────────────────────────
def zipdir(src, dst, arcbase):
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
        for root,_,files in os.walk(src):
            for f in files:
                if f.endswith('.zip'): continue
                full=os.path.join(root,f)
                z.write(full, os.path.join(arcbase, os.path.relpath(full,src)))
sizes={}
for c in CASES:
    d=f"{ROOT}/{c['slug']}"
    zp=f"{d}/{c['slug']}.zip"
    zipdir(d, zp, c['slug'])
    sizes[c['slug']]=os.path.getsize(zp)
with zipfile.ZipFile(f'{ROOT}/ai-company-kit.zip','w',zipfile.ZIP_DEFLATED) as z:
    for root,_,files in os.walk(ROOT):
        for f in files:
            if f.endswith('.zip'): continue
            full=os.path.join(root,f)
            z.write(full, os.path.join('ai-company-kit', os.path.relpath(full,ROOT)))
master=os.path.getsize(f'{ROOT}/ai-company-kit.zip')
print(f'README кейсов: {len(CASES)}')
print(f'архивов по кейсам: {len(sizes)}; общий архив: {master/1024:.0f} КБ')
print('промпты, шпаргалка и памятка по данным собраны')

# ── Страница сайта codex-cases.html ─────────────────────────────────────
def esc(s): return html.escape(s, quote=False)
def files_html(c):
    # Ссылку ставим только если файл реально есть на диске. Групповые записи
    # (папки, наборы файлов) показываем текстом — иначе получаем битую ссылку.
    out=[]
    for f,d in c['files']:
        path=f'site/cases/{c["slug"]}/{f}'
        if not f.endswith('/') and os.path.isfile(path):
            out.append(f'<li><a href="cases/{c["slug"]}/{f}">{esc(f)}</a> — {esc(d)}</li>')
        else:
            out.append(f'<li><strong>{esc(f)}</strong> — {esc(d)} <span class="muted small">(в архиве практики)</span></li>')
    return '\n        '.join(out)

import collections as _c
_cnt=_c.Counter(d for c in CASES for d in c['depts'])
chips='\n      '.join(
  [f'<button class="dept-btn is-on" data-dept="all">Все практики <span class="m">{len(CASES)}</span></button>'] +
  [f'<button class="dept-btn" data-dept="{esc(d)}">{esc(d)} <span class="m">{_cnt[d]}</span></button>'
   for d in DEPTS if _cnt[d]])

blocks=[]
for c in CASES:
    hid='\n        '.join(f'<li>{esc(h)}</li>' for h in c['hidden'])
    steps='\n        '.join(f'<li>{esc(b)}</li>' for b in c['build'])
    warn=(f'<div class="note">⚠️ <strong>Особое требование.</strong> {esc(c["warn"])}</div>'
          if c.get('warn') else '')
    diff_label = {1:'1/3 · простая', 2:'2/3 · средняя', 3:'3/3 · сложная'}[c['diff']]
    dept_badges = ''.join(f'<span class="tag tag-dept">{esc(d)}</span>' for d in c['depts'])
    blocks.append(f"""    <div class="card case" id="c{c['n']}" data-depts="{esc('|'.join(c['depts']))}" data-diff="{c['diff']}">
      <h3>{c['n']}. {esc(c['title'])}</h3>
      <p class="muted" style="margin-bottom:10px">{esc(c['sub'])}</p>
      <p class="tags">{dept_badges}<span class="tag tag-diff d{c['diff']}">Сложность {diff_label}</span><span class="tag">{esc(c['time'])}</span></p>
      <p class="bring"><strong>Что принести:</strong> {esc(c['bring'])}</p>
      <p><strong>Цель.</strong> {esc(c['goal'])}</p>
      <p><strong>Что на входе.</strong> {esc(c['inp'])}</p>
      <p><strong>Что должен собрать агент:</strong></p>
      <ol>
        {steps}
      </ol>
      <p><strong>Результат.</strong> {esc(c['result'])}</p>
      <p><strong>Раздатка:</strong></p>
      <ul>
        {files_html(c)}
      </ul>
      <p><strong>Что спрятано в данных</strong> — хороший результат тот, где агент это нашёл:</p>
      <ul>
        {hid}
      </ul>
      {warn}
      <p class="small muted"><strong>Быстрый режим:</strong> {esc(c['quick'])}<br>
      <strong>Усиленный:</strong> {esc(c['strong'])}</p>
      <p><a class="btn" href="cases/{c['slug']}/{c['slug']}.zip">Скачать практику {c['n']} ({sizes[c['slug']]//1024} КБ)</a>
         &nbsp; <a href="cases/{c['slug']}/README.html">Промпт и описание →</a></p>
    </div>""")

page=f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Практические кейсы в Codex — мастер-класс «AI-компания»</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<header class="site">
  <div class="container">
    <a class="logo" href="index.html">ИИ-агенты <span>для предпринимателей</span></a>
    <nav class="head-nav"><a class="to-index" href="index.html">← К программе</a><a class="skip" href="#kit">К раздатке →</a></nav>
  </div>
</header>

<section class="hero" style="padding-bottom:0">
  <div class="container">
    <span class="badge">Раздел · мастер-класс «AI-компания»</span>
    <h1>Практические кейсы в Codex</h1>
    <p class="lead">Шестнадцать практик, каждая из которых заканчивается не советом, а работающим прототипом:
    приложением, дашбордом, системой или документом. Ко всем — готовые учебные данные с заранее заложенными
    находками и стартовый промпт.</p>
    <div class="note">Раздел собран по ТЗ мастер-класса и живёт отдельно от модулей М0–М10 — нумерация уроков не меняется.
    Практики можно брать в любом порядке и раздавать по отделам.</div>
  </div>
</section>

<section id="kit">
  <div class="container">
    <h2>Скачать раздатку</h2>
    <p>Один архив со всеми шестнадцатью практиками: учебные данные, промпты, README, шпаргалка ведущего
    и памятка по своим данным.</p>
    <p><a class="btn" href="cases/ai-company-kit.zip">Скачать весь комплект ({master//1024} КБ)</a></p>
    <ul>
      <li><a href="cases/cheatsheet.html">Шпаргалка ведущего</a> — все практики одной таблицей, драматургия дня, распределение по отделам <span class="muted small">(<a href="cases/MASTERCLASS_CHEATSHEET.md" download>скачать .md</a>)</span></li>
      <li><a href="cases/prompts.html">Все промпты одним файлом</a> — копировать и вставлять <span class="muted small">(<a href="cases/MASTERCLASS_PROMPTS.md" download>скачать .md</a>)</span></li>
      <li><a href="cases/bring-your-own-data.html">Что принести с собой</a> — какие свои данные пригодятся и как их обезличить <span class="muted small">(<a href="cases/BRING_YOUR_OWN_DATA.md" download>скачать .md</a>)</span></li>
    </ul>
    <div class="note"><strong>Главное правило мастер-класса.</strong> Задание не считается выполненным, если агент
    только описал, «как можно сделать». Он должен создать файлы, запустить решение, проверить основные сценарии,
    исправить ошибки и показать работающую версию.</div>
  </div>
</section>

<section style="padding-top:0">
  <div class="container jump">
    <p class="jump-title">Выберите свой отдел — останутся только ваши практики</p>
    <div class="jump-grid dept-nav">
      {chips}
    </div>
    <p class="small muted" id="dept-hint" style="margin-top:12px">Показаны все {len(CASES)} практик. На один мастер-класс участник проходит три: одну общую, одну по своему отделу и финальный сквозной кейс.</p>
  </div>
</section>

<section>
  <div class="container">
    <h2>Практики</h2>
{chr(10).join(blocks)}

    <h2>Как это устроено технически</h2>
    <p>Промпт для Claude Code и для Codex — <strong>один и тот же</strong>, намеренно. Различаются только две вещи:</p>
    <ul>
      <li><strong>Файл настроек проекта.</strong> Claude Code читает <code>CLAUDE.md</code>, Codex — <code>AGENTS.md</code>.
      Работаете обоими — положите в папку оба файла с одинаковым содержимым.</li>
      <li><strong>Разрешения.</strong> В Claude Code подтверждаете действия по ходу, в Codex стоит заранее
      посмотреть <code>/permissions</code>. Как получить доступ к Codex — в <a href="codex-access.html">отдельной инструкции</a>.</li>
    </ul>
    <p>Учебные данные сгенерированы скриптами с проверкой: каждый заложенный сюжет подтверждён замером,
    а не «нарисован на глаз». Например, в продажах за 12 месяцев узкое место по марже, падение продукта
    и концентрация клиентов проверяются автоматически при каждой пересборке комплекта.</p>

    <nav class="lesson-nav">
      <a href="index.html">← К программе курса</a>
      <a href="cases/ai-company-kit.zip">Скачать комплект →</a>
    </nav>
  </div>
</section>

<footer class="site">
  <div class="container"><p><a href="index.html" style="color:#10A37F;text-decoration:none">← Вернуться к программе курса</a></p></div>
</footer>

<script>
// Фильтр по отделу. Без JS видны все карточки — это осознанно.
(function () {{
  var btns = document.querySelectorAll('.dept-btn');
  var cards = document.querySelectorAll('.case');
  var hint = document.getElementById('dept-hint');
  var total = cards.length;
  var allText = 'Показаны все ' + total + ' практик. На один мастер-класс участник проходит три: '
              + 'одну общую, одну по своему отделу и финальный сквозной кейс.';
  btns.forEach(function (b) {{
    b.addEventListener('click', function () {{
      var d = b.dataset.dept, shown = 0;
      btns.forEach(function (x) {{ x.classList.toggle('is-on', x === b); }});
      cards.forEach(function (card) {{
        var ok = d === 'all' || card.dataset.depts.split('|').indexOf(d) !== -1;
        card.style.display = ok ? '' : 'none';
        if (ok) shown++;
      }});
      hint.textContent = d === 'all' ? allText
        : 'Отдел «' + d + '»: практик — ' + shown + '. Нажмите «Все практики», чтобы снять фильтр.';
      document.querySelector('.dept-nav').scrollIntoView({{ block: 'start' }});
    }});
  }});
}})();
</script>
</body>
</html>
"""
open('site/codex-cases.html','w',encoding='utf-8').write(page)
print(f'страница site/codex-cases.html собрана: {len(page)//1024} КБ')

# ── Читаемые HTML-версии общих документов ───────────────────────────────
def md2html(md, title, back='../codex-cases.html'):
    """Мини-конвертер: заголовки, таблицы, списки, код, жирный. Достаточно для наших документов."""
    out=[]; in_tbl=False; in_code=False; in_ul=False; in_ol=False
    skipped_h1=False   # первый # заголовок дублирует title в шапке — пропускаем
    para=[]            # соседние строки текста — это ОДИН абзац, а не абзац на строку
    def flush_para():
        nonlocal para
        if para:
            out.append('<p>'+inline(' '.join(para))+'</p>'); para=[]
    def close_lists():
        nonlocal in_ul,in_ol
        flush_para()
        if in_ul: out.append('</ul>'); in_ul=False
        if in_ol: out.append('</ol>'); in_ol=False
    def inline(t):
        t=html.escape(t, quote=False)
        t=re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
        t=re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
        t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
        t=t.replace('&lt;br&gt;','<br>')   # перенос строки в ячейке таблицы — разрешаем
        return t
    for line in md.split('\n'):
        if line.strip().startswith('```'):
            close_lists()
            out.append('</code></pre>' if in_code else '<pre><code>'); in_code=not in_code; continue
        if in_code: out.append(html.escape(line, quote=False)); continue
        if line.startswith('|'):
            flush_para()
            cells=[c.strip() for c in line.strip('|').split('|')]
            if set(''.join(cells))<=set('-: '): continue
            if not in_tbl: close_lists(); out.append('<table>'); in_tbl=True; tag='th'
            else: tag='td'
            out.append('<tr>'+''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells)+'</tr>'); continue
        if in_tbl: out.append('</table>'); in_tbl=False
        if line.strip() in ('---','***','___'):
            close_lists(); out.append('<hr>'); continue
        if line.startswith('#'):
            close_lists(); lvl=len(line)-len(line.lstrip('#'))
            if lvl==1 and not skipped_h1:
                skipped_h1=True; continue
            out.append(f'<h{min(lvl,4)}>{inline(line.lstrip("# "))}</h{min(lvl,4)}>'); continue
        if line.strip().startswith('> '):
            close_lists(); out.append(f'<div class="note">{inline(line.strip()[2:])}</div>'); continue
        m=re.match(r'^(\d+)\. (.*)', line)
        if m:
            if in_ul: out.append('</ul>'); in_ul=False
            if not in_ol: out.append('<ol>'); in_ol=True
            out.append(f'<li>{inline(m.group(2))}</li>'); continue
        if line.strip().startswith('- '):
            if in_ol: out.append('</ol>'); in_ol=False
            if not in_ul: out.append('<ul>'); in_ul=True
            out.append(f'<li>{inline(line.strip()[2:])}</li>'); continue
        if line.strip():
            if (in_ul or in_ol) and out and out[-1].endswith('</li>'):
                # перенос строки внутри пункта списка — дописываем в тот же <li>
                out[-1] = out[-1][:-5] + ' ' + inline(line.strip()) + '</li>'
            elif in_ul or in_ol:
                out.append(f'<p>{inline(line)}</p>')
            else:
                para.append(line.strip())
        else:
            flush_para()
    close_lists()
    if in_tbl: out.append('</table>')
    body='\n'.join(out)
    return f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title><link rel="stylesheet" href="../style.css"></head><body>
<header class="site"><div class="container">
<a class="logo" href="../index.html">ИИ-агенты <span>для предпринимателей</span></a>
<nav class="head-nav"><a class="to-index" href="{back}">← К кейсам</a><a class="skip" href="../index.html">К программе →</a></nav>
</div></header>
<section class="hero" style="padding-bottom:0"><div class="container">
<span class="badge">Мастер-класс «AI-компания»</span><h1>{html.escape(title)}</h1></div></section>
<section><div class="container">
{body}
<nav class="lesson-nav"><a href="{back}">← К практическим кейсам</a><a href="../index.html">К программе курса →</a></nav>
</div></section>
<footer class="site"><div class="container"><p><a href="../index.html" style="color:#10A37F;text-decoration:none">← Вернуться к программе курса</a></p></div></footer>
</body></html>"""

import re
for src,out,title in [('MASTERCLASS_CHEATSHEET.md','cheatsheet.html','Шпаргалка ведущего'),
                      ('MASTERCLASS_PROMPTS.md','prompts.html','Промпты всех практик'),
                      ('BRING_YOUR_OWN_DATA.md','bring-your-own-data.html','Что принести с собой')]:
    open(f'{ROOT}/{out}','w',encoding='utf-8').write(md2html(open(f'masterclass/{src}',encoding='utf-8').read(), title))
print('HTML-версии общих документов собраны: cheatsheet, prompts, bring-your-own-data')


# ── README.html по каждой практике (чтобы на телефоне читалось, а не ломалось) ──
for c in CASES:
    md=open(f"{ROOT}/{c['slug']}/README.md",encoding='utf-8').read()
    html_page=md2html(md, f"Практика {c['n']}. {c['title']}", back='../codex-cases.html')
    html_page=html_page.replace('href="../style.css"','href="../../style.css"')
    html_page=html_page.replace('href="../index.html"','href="../../index.html"')
    html_page=html_page.replace('href="../codex-cases.html"','href="../../codex-cases.html"')
    # Визуально разводим две аудитории: участнику — одно, ведущему — другое.
    html_page=html_page.replace('<h1>Для участника</h1>',
        '<div class="aud aud-part"><p class="aud-label">Как пройти практику</p>')
    html_page=html_page.replace('<h1>Что искать в данных</h1>',
        '</div><div class="aud aud-find"><p class="aud-label">Что искать в данных</p>')
    html_page=html_page.replace('<nav class="lesson-nav">','</div><nav class="lesson-nav">',1)
    open(f"{ROOT}/{c['slug']}/README.html",'w',encoding='utf-8').write(html_page)
print(f'README.html по практикам: {len(CASES)}')
