"""
Отладка модели "Продажа + подписка"
"""

from business_calculator import BusinessCalculator

def debug_sale_model():
    """Отладка модели продажи + подписка"""
    print("=== ОТЛАДКА МОДЕЛИ 'ПРОДАЖА + ПОДПИСКА' ===")
    
    calc = BusinessCalculator('baseline', 'A', 'mini', 'shiwa_assembled')
    summary = calc.generate_financial_summary()
    payback = calc.calculate_payback_period()
    
    print(f"Сценарий: {summary['scenario']}")
    print(f"Вариант: {summary['variant']}")
    print(f"Количество отелей: {summary['hotels_count']}")
    print()
    
    # Детализация доходов
    print("ДОХОДЫ SHIWA:")
    print(f"  От продажи оборудования: ${summary['shiwa']['equipment_revenue']:,.0f}")
    print(f"  От подписки: ${summary['shiwa']['subscription_revenue']:,.0f}")
    print(f"  Общий доход: ${summary['shiwa']['total_revenue']:,.0f}")
    print()
    
    # Детализация затрат
    print("ЗАТРАТЫ SHIWA:")
    print(f"  Общие затраты: ${summary['shiwa']['total_costs']:,.0f}")
    print()
    
    # Расчет прибыли
    net_profit = summary['shiwa']['net_profit']
    print(f"ПРИБЫЛЬ:")
    print(f"  Чистая прибыль: ${net_profit:,.0f}")
    print(f"  ROI: {summary['shiwa']['roi']:.1f}%")
    print()
    
    # Проверка окупаемости
    print("ОКУПАЕМОСТЬ:")
    print(f"  Из системы: {payback['payback_months']:.1f} месяцев")
    print(f"  Ежемесячная прибыль: ${payback['monthly_profit']:,.0f}")
    
    # Ручной расчет
    monthly_profit_manual = net_profit / 12
    payback_manual = summary['shiwa']['total_costs'] / monthly_profit_manual
    
    print(f"  Ручной расчет прибыли: ${monthly_profit_manual:,.0f}/мес")
    print(f"  Ручной расчет окупаемости: {payback_manual:.1f} месяцев")
    print()
    
    # Проверка логики
    if abs(payback['payback_months'] - payback_manual) < 1:
        print("✅ Расчет окупаемости корректен!")
    else:
        print("❌ Ошибка в расчете окупаемости!")
        print(f"Разница: {abs(payback['payback_months'] - payback_manual):.1f} месяцев")

def check_equipment_costs_in_sale():
    """Проверка затрат на оборудование в модели продажи"""
    print("\n=== ЗАТРАТЫ НА ОБОРУДОВАНИЕ В МОДЕЛИ ПРОДАЖИ ===")
    
    calc = BusinessCalculator('baseline', 'A', 'mini', 'shiwa_assembled')
    prices = calc.equipment_prices
    
    print(f"ЗАТРАТЫ НА ОБОРУДОВАНИЕ:")
    print(f"  Себестоимость одного сервера: ${prices['adjusted_cost_usd']:,.0f}")
    print(f"  Количество отелей: 50")
    print(f"  Общие затраты на оборудование: ${prices['adjusted_cost_usd'] * 50:,.0f}")
    print()
    
    # Проверяем, включаются ли затраты на оборудование
    summary = calc.generate_financial_summary()
    profitability = calc.calculate_shiwa_profitability()
    
    print(f"ВКЛЮЧЕНЫ ЛИ ЗАТРАТЫ НА ОБОРУДОВАНИЕ В РАСЧЕТ:")
    print(f"  Общие затраты SHIWA: ${profitability['total_costs_usd']:,.0f}")
    print(f"  Затраты на оборудование: ${prices['adjusted_cost_usd'] * 50:,.0f}")
    print(f"  Операционные затраты: ${profitability['total_costs_usd'] - (prices['adjusted_cost_usd'] * 50):,.0f}")
    
    # Это ключевой вопрос!
    if profitability['total_costs_usd'] > prices['adjusted_cost_usd'] * 50:
        print("✅ Затраты на оборудование ВКЛЮЧЕНЫ в расчет окупаемости")
    else:
        print("❌ Затраты на оборудование НЕ включены в расчет окупаемости")

def calculate_realistic_payback():
    """Расчет реалистичной окупаемости"""
    print("\n=== РЕАЛИСТИЧНАЯ ОКУПАЕМОСТЬ ===")
    
    calc = BusinessCalculator('baseline', 'A', 'mini', 'shiwa_assembled')
    summary = calc.generate_financial_summary()
    prices = calc.equipment_prices
    profitability = calc.calculate_shiwa_profitability()
    
    # Реалистичный расчет: включаем затраты на оборудование
    equipment_costs = prices['adjusted_cost_usd'] * 50
    operational_costs = profitability['total_costs_usd']
    total_costs = equipment_costs + operational_costs
    
    annual_revenue = summary['shiwa']['total_revenue']
    annual_profit = annual_revenue - total_costs
    monthly_profit = annual_profit / 12
    
    realistic_payback = total_costs / monthly_profit if monthly_profit > 0 else float('inf')
    
    print(f"РЕАЛИСТИЧНЫЙ РАСЧЕТ (с затратами на оборудование):")
    print(f"  Затраты на оборудование: ${equipment_costs:,.0f}")
    print(f"  Операционные затраты: ${operational_costs:,.0f}")
    print(f"  Общие затраты: ${total_costs:,.0f}")
    print(f"  Годовой доход: ${annual_revenue:,.0f}")
    print(f"  Годовая прибыль: ${annual_profit:,.0f}")
    print(f"  Ежемесячная прибыль: ${monthly_profit:,.0f}")
    print(f"  Реалистичная окупаемость: {realistic_payback:.1f} месяцев ({realistic_payback/12:.1f} лет)")
    
    # Сравнение
    payback = calc.calculate_payback_period()
    print()
    print(f"СРАВНЕНИЕ:")
    print(f"  Система показывает: {payback['payback_months']:.1f} месяцев")
    print(f"  Реалистичный расчет: {realistic_payback:.1f} месяцев")
    print(f"  Разница: {abs(payback['payback_months'] - realistic_payback):.1f} месяцев")

if __name__ == "__main__":
    debug_sale_model()
    check_equipment_costs_in_sale()
    calculate_realistic_payback()
