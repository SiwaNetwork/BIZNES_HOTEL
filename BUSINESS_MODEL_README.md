# Бизнес-модель проекта QUANTUM для отелей Кубы

## Описание

Гибкая и удобная система для расчета и анализа бизнес-модели проекта синхронизации времени QUANTUM для отелей Кубы. Система позволяет легко изменять параметры и сразу видеть результаты расчетов.

## Структура проекта

```
BIZNES_HOTEL/
├── parameters.py              # Основные параметры проекта
├── business_calculator.py     # Калькулятор бизнес-модели
├── scenario_analyzer.py       # Анализатор сценариев
├── interactive_analyzer.py    # Интерактивный анализатор
├── examples.py               # Примеры использования
├── BUSINESS_MODEL_README.md  # Документация
└── requirements.txt          # Зависимости
```

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install pandas matplotlib numpy
```

### 2. Базовый анализ

```python
from business_calculator import quick_analysis

# Быстрый анализ базового сценария
quick_analysis('baseline', 'B')
```

### 3. Сравнение всех сценариев

```python
from scenario_analyzer import quick_scenario_analysis

# Полный анализ всех сценариев
quick_scenario_analysis()
```

### 4. Интерактивный режим

```bash
python interactive_analyzer.py
```

## Основные компоненты

### 1. parameters.py

Содержит все основные параметры проекта:

- **Основные параметры**: количество отелей, абонентская плата, курс валют
- **Параметры оборудования**: себестоимость, цены продажи
- **Модели монетизации**: варианты А и Б
- **Расходы**: ФОТ, офисные расходы, командировки
- **Сценарии развития**: базовый, оптимистичный, пессимистичный

### 2. business_calculator.py

Основной калькулятор для расчета финансовых показателей:

```python
from business_calculator import BusinessCalculator

# Создание калькулятора
calc = BusinessCalculator('baseline', 'B')

# Расчет доходов SHIWA NETWORK
shiwa_revenue = calc.calculate_shiwa_revenue()

# Расчет доходов ETECSA
etecsa_revenue = calc.calculate_etecsa_revenue()

# Расчет выгод для отелей
hotel_benefits = calc.calculate_hotel_benefits()

# Полная финансовая сводка
summary = calc.generate_financial_summary()
```

### 3. scenario_analyzer.py

Анализатор для сравнения различных сценариев:

```python
from scenario_analyzer import ScenarioAnalyzer

analyzer = ScenarioAnalyzer()

# Сравнительная таблица всех сценариев
analyzer.print_comparison_table()

# Лучший сценарий по ROI
analyzer.find_best_scenario('roi_shiwa')

# Анализ чувствительности
analyzer.analyze_sensitivity('monthly_fee', [300, 400, 500, 600, 700])

# Сценарии "что если"
analyzer.print_what_if_analysis()

# Анализ точки безубыточности
analyzer.calculate_break_even_analysis()
```

### 4. interactive_analyzer.py

Интерактивный анализатор для изменения параметров:

```python
from interactive_analyzer import InteractiveAnalyzer

analyzer = InteractiveAnalyzer()

# Изменение параметров
analyzer.change_hotels_count(75)
analyzer.change_monthly_fee(450)
analyzer.change_variant('A')

# Анализ с новыми параметрами
analyzer.run_analysis_with_custom_params()

# Сохранение пользовательского сценария
analyzer.save_custom_scenario('Мой сценарий')
```

## Доступные сценарии

### 1. Базовый сценарий (baseline)
- 50 отелей
- Абонентская плата: $500/месяц
- Успешность внедрения: 100%

### 2. Оптимистичный сценарий (optimistic)
- 75 отелей
- Абонентская плата: $500/месяц
- Успешность внедрения: 95%
- Дополнительные выгоды: +20%

### 3. Пессимистичный сценарий (pessimistic)
- 30 отелей
- Абонентская плата: $400/месяц
- Успешность внедрения: 80%
- Дополнительные затраты: +30%

## Модели монетизации

### Вариант А: Продажа оборудования + подписка
- Продажа оборудования ETECSA
- Подписка SHIWA: $20/отель/месяц
- Единоразовая оплата отелями

### Вариант Б: Аренда оборудования (80/20)
- Продажа оборудования ETECSA
- Разделение абонентской платы:
  - SHIWA: 80% ($400/месяц)
  - ETECSA: 20% ($100/месяц)

## Основные показатели

### Для SHIWA NETWORK
- Общий доход
- Чистая прибыль
- ROI (возврат на инвестиции)
- Период окупаемости
- Рентабельность

### Для ETECSA
- Доход от оборудования
- Доход от абонентской платы
- Операционные затраты
- Чистая прибыль

### Для отелей
- Годовые затраты
- Экономические выгоды
- ROI от внедрения

## Примеры использования

### 1. Базовый анализ проекта
```python
from examples import example_1_basic_analysis
example_1_basic_analysis()
```

### 2. Сравнение сценариев
```python
from examples import example_2_scenario_comparison
example_2_scenario_comparison()
```

### 3. Анализ чувствительности
```python
from examples import example_3_sensitivity_analysis
example_3_sensitivity_analysis()
```

### 4. Сценарии "что если"
```python
from examples import example_4_what_if_scenarios
example_4_what_if_scenarios()
```

### 5. Анализ точки безубыточности
```python
from examples import example_5_breakeven_analysis
example_5_breakeven_analysis()
```

## Интерактивные команды

При использовании `interactive_analyzer.py` доступны следующие команды:

- `show` - показать текущие параметры
- `scenario <название>` - изменить сценарий
- `variant <A|B>` - изменить вариант монетизации
- `hotels <число>` - изменить количество отелей
- `fee <сумма>` - изменить абонентскую плату
- `cost <сумма>` - изменить себестоимость оборудования
- `rate <курс>` - изменить курс рубль/доллар
- `analyze` - запустить анализ
- `save <имя>` - сохранить сценарий
- `load <файл>` - загрузить сценарий
- `menu` - показать меню
- `quit` - выход

## Экспорт результатов

Система поддерживает экспорт результатов в JSON формате:

```python
from scenario_analyzer import ScenarioAnalyzer

analyzer = ScenarioAnalyzer()
analyzer.export_results_to_json('results.json')
```

## Настройка параметров

Все основные параметры можно изменить в файле `parameters.py`:

```python
# Количество отелей
HOTELS_COUNT = 50

# Абонентская плата
MONTHLY_FEE_USD = 500

# Курс валют
RUB_TO_USD_RATE = 78

# Себестоимость оборудования
EQUIPMENT_COST_RUB = 90000
```

## Запуск всех примеров

```bash
python examples.py
```

## Требования

- Python 3.7+
- pandas
- matplotlib
- numpy

## Поддержка

Для вопросов и предложений по улучшению модели обращайтесь к разработчикам проекта.

## Лицензия

Внутренний проект SHIWA NETWORK.
