"""
Тестовый скрипт для проверки бизнес-модели
"""

from business_calculator import BusinessCalculator, quick_analysis
from parameters import *

def test_basic_calculations():
    """Тест базовых расчетов"""
    print("=== ТЕСТ БАЗОВЫХ РАСЧЕТОВ ===")
    
    # Тест 1: Базовый сценарий, вариант B
    print("\n1. Базовый сценарий, вариант B (аренда 80/20):")
    quick_analysis('baseline', 'B')
    
    # Тест 2: Базовый сценарий, вариант A
    print("\n2. Базовый сценарий, вариант A (продажа + подписка):")
    quick_analysis('baseline', 'A')
    
    # Тест 3: Оптимистичный сценарий
    print("\n3. Оптимистичный сценарий, вариант B:")
    quick_analysis('optimistic', 'B')
    
    # Тест 4: Пессимистичный сценарий
    print("\n4. Пессимистичный сценарий, вариант B:")
    quick_analysis('pessimistic', 'B')

def test_parameter_changes():
    """Тест изменения параметров"""
    print("\n=== ТЕСТ ИЗМЕНЕНИЯ ПАРАМЕТРОВ ===")
    
    # Создаем калькулятор
    calc = BusinessCalculator('baseline', 'B')
    
    # Изменяем количество отелей
    calc.scenario_params['hotels_count'] = 75
    print(f"\nКоличество отелей изменено на: {calc.scenario_params['hotels_count']}")
    
    # Пересчитываем
    summary = calc.generate_financial_summary()
    print(f"Новый доход SHIWA: ${summary['shiwa']['total_revenue']:,.0f}")
    print(f"Новая прибыль SHIWA: ${summary['shiwa']['net_profit']:,.0f}")
    
    # Изменяем абонентскую плату
    calc.scenario_params['monthly_fee'] = 400
    print(f"\nАбонентская плата изменена на: ${calc.scenario_params['monthly_fee']}")
    
    # Пересчитываем
    summary = calc.generate_financial_summary()
    print(f"Новый доход SHIWA: ${summary['shiwa']['total_revenue']:,.0f}")
    print(f"Новая прибыль SHIWA: ${summary['shiwa']['net_profit']:,.0f}")

def test_equipment_prices():
    """Тест расчета цен оборудования"""
    print("\n=== ТЕСТ РАСЧЕТА ЦЕН ОБОРУДОВАНИЯ ===")
    
    prices = calculate_equipment_prices()
    
    print(f"Себестоимость производства: ${prices['cost_price_usd']:,.0f}")
    print(f"Интеллектуальная стоимость: ${prices['intellectual_value_rub'] / RUB_TO_USD_RATE:,.0f}")
    print(f"Цена продажи ETECSA: ${prices['selling_price_usd']:,.0f}")
    print(f"Цена продажи отелям: ${prices['hotel_price_usd']:,.0f}")

def test_costs():
    """Тест расчета затрат"""
    print("\n=== ТЕСТ РАСЧЕТА ЗАТРАТ ===")
    
    costs = calculate_total_costs()
    
    print(f"ФОТ проекта (30%): ${costs['project_fot_usd']:,.0f}")
    print(f"Офисные расходы: ${costs['office_expenses_usd']:,.0f}")
    print(f"Командировки: ${costs['business_trips_usd']:,.0f}")
    print(f"Доставка: ${costs['delivery_expenses_usd']:,.0f}")
    print(f"Общие затраты: ${costs['total_costs_usd']:,.0f}")

def test_scenario_comparison():
    """Тест сравнения сценариев"""
    print("\n=== ТЕСТ СРАВНЕНИЯ СЦЕНАРИЕВ ===")
    
    scenarios = ['baseline', 'optimistic', 'pessimistic']
    variants = ['A', 'B']
    
    results = []
    
    for scenario in scenarios:
        for variant in variants:
            calc = BusinessCalculator(scenario, variant)
            summary = calc.generate_financial_summary()
            
            results.append({
                'Сценарий': summary['scenario'],
                'Вариант': summary['variant'],
                'Отели': summary['effective_hotels'],
                'Доход SHIWA': f"${summary['shiwa']['total_revenue']:,.0f}",
                'Прибыль SHIWA': f"${summary['shiwa']['net_profit']:,.0f}",
                'ROI SHIWA': f"{summary['shiwa']['roi']:.1f}%"
            })
    
    # Выводим результаты
    for result in results:
        print(f"{result['Сценарий']} + {result['Вариант']}: "
              f"Отели={result['Отели']:.0f}, "
              f"Доход={result['Доход SHIWA']}, "
              f"Прибыль={result['Прибыль SHIWA']}, "
              f"ROI={result['ROI SHIWA']}")

def test_payback_analysis():
    """Тест анализа окупаемости"""
    print("\n=== ТЕСТ АНАЛИЗА ОКУПАЕМОСТИ ===")
    
    calc = BusinessCalculator('baseline', 'B')
    payback = calc.calculate_payback_period()
    
    if payback:
        print(f"Период окупаемости: {payback['payback_months']:.1f} месяцев")
        print(f"Период окупаемости: {payback['payback_years']:.2f} лет")
        print(f"Ежемесячная прибыль: ${payback['monthly_profit']:,.0f}")
    else:
        print("Окупаемость не достигнута")

if __name__ == "__main__":
    print("ТЕСТИРОВАНИЕ БИЗНЕС-МОДЕЛИ QUANTUM")
    print("=" * 50)
    
    test_basic_calculations()
    test_parameter_changes()
    test_equipment_prices()
    test_costs()
    test_scenario_comparison()
    test_payback_analysis()
    
    print("\n" + "=" * 50)
    print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
    print("\nСистема готова к использованию!")
    print("\nДля интерактивного анализа запустите:")
    print("python interactive_analyzer.py")
