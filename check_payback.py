"""
Проверка расчета окупаемости
"""

from business_calculator import BusinessCalculator

def check_payback_calculation():
    """Проверка расчета окупаемости"""
    print("=== ПРОВЕРКА РАСЧЕТА ОКУПАЕМОСТИ ===")
    
    # Модель аренды 80/20
    calc = BusinessCalculator('baseline', 'B', 'mini', 'shiwa_assembled', '80_20')
    summary = calc.generate_financial_summary()
    payback = calc.calculate_payback_period()
    
    print(f"Сценарий: {summary['scenario']}")
    print(f"Вариант: {summary['variant']}")
    print(f"Количество отелей: {summary['hotels_count']}")
    print()
    
    # Затраты SHIWA
    shiwa_costs = summary['shiwa']['total_costs']
    print(f"ЗАТРАТЫ SHIWA:")
    print(f"  Общие затраты: ${shiwa_costs:,.0f}")
    print()
    
    # Доходы SHIWA
    shiwa_revenue = summary['shiwa']['total_revenue']
    print(f"ДОХОДЫ SHIWA:")
    print(f"  Общий доход: ${shiwa_revenue:,.0f}")
    print()
    
    # Расчет окупаемости вручную
    monthly_profit = payback['monthly_profit']
    payback_months = shiwa_costs / monthly_profit if monthly_profit > 0 else float('inf')
    
    print(f"РАСЧЕТ ОКУПАЕМОСТИ:")
    print(f"  Ежемесячная прибыль: ${monthly_profit:,.0f}")
    print(f"  Затраты: ${shiwa_costs:,.0f}")
    print(f"  Окупаемость (затраты/прибыль): {payback_months:.1f} месяцев")
    print(f"  Окупаемость (из системы): {payback['payback_months']:.1f} месяцев")
    print()
    
    # Проверка логики
    if abs(payback_months - payback['payback_months']) < 1:
        print("✅ Расчет окупаемости корректен!")
    else:
        print("❌ Ошибка в расчете окупаемости!")
    
    # Детальная проверка затрат
    print()
    print("ДЕТАЛЬНАЯ ПРОВЕРКА ЗАТРАТ:")
    profitability = calc.calculate_shiwa_profitability()
    print(f"  ФОТ: ${profitability['project_fot_usd']:,.0f}")
    print(f"  Офис: ${profitability['office_expenses_usd']:,.0f}")
    print(f"  Командировки: ${profitability['business_trips_usd']:,.0f}")
    print(f"  Доставка: ${profitability['delivery_expenses_usd']:,.0f}")
    print(f"  Итого затрат: ${profitability['total_costs_usd']:,.0f}")

def check_equipment_costs():
    """Проверка затрат на оборудование"""
    print("\n=== ПРОВЕРКА ЗАТРАТ НА ОБОРУДОВАНИЕ ===")
    
    calc = BusinessCalculator('baseline', 'B', 'mini', 'shiwa_assembled', '80_20')
    prices = calc.equipment_prices
    
    print(f"ЗАТРАТЫ НА ОБОРУДОВАНИЕ:")
    print(f"  Себестоимость одного сервера: ${prices['adjusted_cost_usd']:,.0f}")
    print(f"  Количество отелей: 50")
    print(f"  Общие затраты на оборудование: ${prices['adjusted_cost_usd'] * 50:,.0f}")
    print()
    
    # Проверяем, включаются ли затраты на оборудование в расчет окупаемости
    summary = calc.generate_financial_summary()
    profitability = calc.calculate_shiwa_profitability()
    
    print(f"ВКЛЮЧЕНЫ ЛИ ЗАТРАТЫ НА ОБОРУДОВАНИЕ:")
    print(f"  Затраты SHIWA (из системы): ${profitability['total_costs_usd']:,.0f}")
    print(f"  Затраты на оборудование: ${prices['adjusted_cost_usd'] * 50:,.0f}")
    print(f"  Операционные затраты: ${profitability['total_costs_usd'] - (prices['adjusted_cost_usd'] * 50):,.0f}")

def check_realistic_payback():
    """Проверка реалистичной окупаемости"""
    print("\n=== РЕАЛИСТИЧНАЯ ОКУПАЕМОСТЬ ===")
    
    # При модели аренды SHIWA не покупает оборудование
    calc = BusinessCalculator('baseline', 'B', 'mini', 'shiwa_assembled', '80_20')
    summary = calc.generate_financial_summary()
    profitability = calc.calculate_shiwa_profitability()
    
    # Только операционные затраты (без оборудования)
    operational_costs = profitability['total_costs_usd']
    annual_revenue = summary['shiwa']['total_revenue']
    annual_profit = annual_revenue - operational_costs
    monthly_profit = annual_profit / 12
    
    realistic_payback = operational_costs / monthly_profit if monthly_profit > 0 else float('inf')
    
    print(f"РЕАЛИСТИЧНЫЙ РАСЧЕТ:")
    print(f"  Операционные затраты: ${operational_costs:,.0f}")
    print(f"  Годовой доход: ${annual_revenue:,.0f}")
    print(f"  Годовая прибыль: ${annual_profit:,.0f}")
    print(f"  Ежемесячная прибыль: ${monthly_profit:,.0f}")
    print(f"  Окупаемость: {realistic_payback:.1f} месяцев ({realistic_payback/12:.1f} лет)")

if __name__ == "__main__":
    check_payback_calculation()
    check_equipment_costs()
    check_realistic_payback()
