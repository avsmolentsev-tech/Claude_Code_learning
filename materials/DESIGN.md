# Дизайн-гайд курса "AI для предпринимателей"

## Философия

Минимализм. Чистота. Воздух. Как у OpenAI — ничего лишнего, каждый элемент на своём месте.
Участники — предприниматели, не дизайнеры. Материалы должны выглядеть дорого и профессионально без визуального шума.

## Цветовая палитра

### Основные цвета
- **Фон:** `#FFFFFF` (чистый белый)
- **Текст:** `#171717` (почти чёрный, мягче чем pure black)
- **Текст вторичный:** `#6B7280` (серый)
- **Акцент:** `#10A37F` (зелёный, как у OpenAI/Claude)
- **Акцент hover:** `#0D8C6D`
- **Разделители:** `#E5E7EB` (светло-серый)
- **Фон карточек:** `#F9FAFB` (чуть серый, отделяет от белого фона)
- **Фон кода:** `#F3F4F6`

### Статусы (для дашборда)
- **Успех/Оплачен:** `#10A37F` (зелёный)
- **В процессе/Доставка:** `#F59E0B` (янтарный)
- **Новый:** `#3B82F6` (синий)
- **Отменён:** `#EF4444` (красный)

## Типографика

- **Заголовки:** Inter или system-ui, `font-weight: 600`
- **Текст:** Inter или system-ui, `font-weight: 400`
- **Код:** JetBrains Mono или monospace
- **Размеры:**
  - H1: `2rem` (32px)
  - H2: `1.5rem` (24px)
  - H3: `1.25rem` (20px)
  - Body: `1rem` (16px)
  - Small: `0.875rem` (14px)
- **Межстрочный интервал:** `1.6` (body), `1.2` (заголовки)

## Отступы и сетка

- **Контейнер:** `max-width: 1200px`, `margin: 0 auto`
- **Базовый отступ:** `16px` (кратно 4px сетке)
- **Между секциями:** `48px`
- **Между карточками:** `24px`
- **Внутри карточек:** `24px`
- **border-radius:** `12px` (карточки), `8px` (кнопки, инпуты)

## Карточки

```css
.card {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 24px;
    /* Без теней или минимальная */
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
```

## Графики (Chart.js)

```javascript
const chartColors = {
    primary: '#10A37F',
    primaryLight: 'rgba(16, 163, 127, 0.1)',
    secondary: '#3B82F6',
    grid: '#E5E7EB',
    text: '#6B7280'
};

const chartDefaults = {
    responsive: true,
    plugins: {
        legend: {
            labels: {
                font: { family: 'Inter, system-ui', size: 13 },
                color: '#6B7280',
                usePointStyle: true,
                padding: 20
            }
        }
    },
    scales: {
        x: {
            grid: { display: false },
            ticks: { color: '#6B7280', font: { size: 12 } }
        },
        y: {
            grid: { color: '#E5E7EB' },
            ticks: { color: '#6B7280', font: { size: 12 } }
        }
    }
};
```

- Столбчатые графики: `border-radius: 6px` на барах
- Линейные графики: `tension: 0.3` (мягкие кривые), `borderWidth: 2`
- Круговые: `borderWidth: 0`, пастельные оттенки основных цветов
- Без 3D, без градиентов на графиках — плоский чистый стиль

## Таблицы

```css
table {
    width: 100%;
    border-collapse: collapse;
}
th {
    text-align: left;
    padding: 12px 16px;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #6B7280;
    border-bottom: 2px solid #E5E7EB;
}
td {
    padding: 12px 16px;
    border-bottom: 1px solid #E5E7EB;
    color: #171717;
}
tr:hover {
    background: #F9FAFB;
}
```

## Кнопки

```css
.btn-primary {
    background: #10A37F;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background 0.15s;
}
.btn-primary:hover {
    background: #0D8C6D;
}
.btn-secondary {
    background: white;
    color: #171717;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 500;
    font-size: 0.875rem;
    cursor: pointer;
    transition: border-color 0.15s;
}
.btn-secondary:hover {
    border-color: #171717;
}
```

## Применение к материалам курса

### HTML-отчёт (секция 3)
- Белый фон, карточки с метриками сверху
- Графики в карточках, без рамок
- Таблица — строгая, без цветных строк (только hover)

### Дашборд (секция 5)
- Шапка: название + дата обновления, минимально
- Метрики-карточки в ряд (4 штуки)
- Графики — по 2 в ряд на десктопе, по 1 на мобильном
- Таблица — внизу, полная ширина

### Telegram-бот (секция 4)
- Текстовые ответы: чистое форматирование, эмодзи-иконки (📊 📈 🏆) как визуальные маркеры
- Графики-картинки из бота: белый фон, зелёный акцент (`#10A37F`)

### Памятка (раздатка)
- При конвертации в PDF: те же шрифты и цвета
- Код в серых блоках (`#F3F4F6`)

## Чего НЕ делать

- Градиенты на фонах
- Тени с большим blur (max `box-shadow: 0 1px 3px`)
- Rounded углы больше 12px
- Анимации ради анимаций
- Яркие фоны секций (синий, зелёный)
- Иконки ради иконок
- Больше 2 акцентных цветов на одной странице
