"""
Сравнение моделей монетизации
"""

from business_calculator import BusinessCalculator

def compare_monetization_models():
    """Сравнение моделей монетизации"""
    print("=== СРАВНЕНИЕ МОДЕЛЕЙ МОНЕТИЗАЦИИ ===")
    
    models = [
        ('A', 'Продажа оборудования + подписка'),
        ('B', 'Аренда оборудования (80/20)')
    ]
    
    for variant, name in models:
        print(f"\n--- {name} ---")
        calc = BusinessCalculator('baseline', variant, 'mini', 'shiwa_assembled')
        summary = calc.generate_financial_summary()
        payback = calc.calculate_payback_period()
        
        print(f"Доход SHIWA: ${summary['shiwa']['total_revenue']:,.0f}")
        print(f"Прибыль SHIWA: ${summary['shiwa']['net_profit']:,.0f}")
        print(f"Затраты SHIWA: ${summary['shiwa']['total_costs']:,.0f}")
        print(f"ROI SHIWA: {summary['shiwa']['roi']:.1f}%")
        print(f"Окупаемость: {payback['payback_months']:.1f} месяцев ({payback['payback_years']:.1f} лет)")
        
        # Детализация доходов
        print(f"  Доход от оборудования: ${summary['shiwa']['equipment_revenue']:,.0f}")
        print(f"  Доход от подписки: ${summary['shiwa']['subscription_revenue']:,.0f}")

def check_equipment_costs_in_models():
    """Проверка затрат на оборудование в разных моделях"""
    print("\n=== ЗАТРАТЫ НА ОБОРУДОВАНИЕ В РАЗНЫХ МОДЕЛЯХ ===")
    
    calc = BusinessCalculator('baseline', 'A', 'mini', 'shiwa_assembled')
    prices = calc.equipment_prices
    
    print(f"Себестоимость оборудования:")
    print(f"  Один сервер: ${prices['adjusted_cost_usd']:,.0f}")
    print(f"  50 серверов: ${prices['adjusted_cost_usd'] * 50:,.0f}")
    print()
    
    # Модель А: продажа + подписка
    calc_a = BusinessCalculator('baseline', 'A', 'mini', 'shiwa_assembled')
    summary_a = calc_a.generate_financial_summary()
    payback_a = calc_a.calculate_payback_period()
    
    print(f"МОДЕЛЬ А (Продажа + подписка):")
    print(f"  Доход: ${summary_a['shiwa']['total_revenue']:,.0f}")
    print(f"  Прибыль: ${summary_a['shiwa']['net_profit']:,.0f}")
    print(f"  Окупаемость: {payback_a['payback_months']:.1f} месяцев")
    print(f"  Включает затраты на оборудование: ДА")
    print()
    
    # Модель Б: аренда
    calc_b = BusinessCalculator('baseline', 'B', 'mini', 'shiwa_assembled', '80_20')
    summary_b = calc_b.generate_financial_summary()
    payback_b = calc_b.calculate_payback_period()
    
    print(f"МОДЕЛЬ Б (Аренда 80/20):")
    print(f"  Доход: ${summary_b['shiwa']['total_revenue']:,.0f}")
    print(f"  Прибыль: ${summary_b['shiwa']['net_profit']:,.0f}")
    print(f"  Окупаемость: {payback_b['payback_months']:.1f} месяцев")
    print(f"  Включает затраты на оборудование: НЕТ (только операционные)")

def explain_payback_difference():
    """Объяснение разницы в окупаемости"""
    print("\n=== ОБЪЯСНЕНИЕ РАЗНИЦЫ В ОКУПАЕМОСТИ ===")
    
    print("ПОЧЕМУ РАЗНАЯ ОКУПАЕМОСТЬ:")
    print()
    print("МОДЕЛЬ А (Продажа + подписка):")
    print("  - SHIWA покупает оборудование за $57,700 (50 × $1,154)")
    print("  - SHIWA продает ETECSA за $116,667")
    print("  - SHIWA получает подписку $12,000/год")
    print("  - Общий доход: $128,667/год")
    print("  - Затраты: $53,205 (операционные)")
    print("  - Прибыль: $75,462/год")
    print("  - Окупаемость: ~8.5 месяцев")
    print()
    print("МОДЕЛЬ Б (Аренда 80/20):")
    print("  - SHIWA НЕ покупает оборудование")
    print("  - SHIWA получает 80% от абонентской платы: $240,000/год")
    print("  - Затраты: $53,205 (только операционные)")
    print("  - Прибыль: $186,795/год")
    print("  - Окупаемость: ~2.7 месяцев")
    print()
    print("ВЫВОД: Модель аренды выгоднее для SHIWA!")

if __name__ == "__main__":
    compare_monetization_models()
    check_equipment_costs_in_models()
    explain_payback_difference()
