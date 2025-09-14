"""
Проверка расчетов абонентской платы
"""

from business_calculator import BusinessCalculator

def check_subscription_calculations():
    """Проверка расчетов абонентской платы"""
    print("=== ПРОВЕРКА РАСЧЕТОВ АБОНЕНТСКОЙ ПЛАТЫ ===")
    
    calc = BusinessCalculator('baseline', 'A', 'mini', 'shiwa_assembled')
    summary = calc.generate_financial_summary()
    
    print(f"Количество отелей: {summary['hotels_count']}")
    print(f"Эффективных отелей: {summary['effective_hotels']}")
    print(f"Абонентская плата с отеля: ${calc.scenario_params['monthly_fee']}")
    print()
    
    # Общая абонентская плата
    total_monthly = summary['hotels_count'] * calc.scenario_params['monthly_fee']
    total_annual = total_monthly * 12
    
    print(f"ОБЩАЯ АБОНЕНТСКАЯ ПЛАТА:")
    print(f"  В месяц: ${total_monthly:,}")
    print(f"  В год: ${total_annual:,}")
    print()
    
    # Распределение между SHIWA и ETECSA
    shiwa_annual = summary['shiwa']['subscription_revenue']
    etecsas_annual = summary['etecsa']['subscription_revenue']
    
    print(f"РАСПРЕДЕЛЕНИЕ ДОХОДОВ:")
    print(f"  SHIWA получает: ${shiwa_annual:,} в год")
    print(f"  ETECSA получает: ${etecsas_annual:,} в год")
    print(f"  Итого: ${shiwa_annual + etecsas_annual:,} в год")
    print()
    
    # Проверка математики
    print(f"ПРОВЕРКА МАТЕМАТИКИ:")
    print(f"  SHIWA + ETECSA = ${shiwa_annual + etecsas_annual:,}")
    print(f"  Общая абонентская плата = ${total_annual:,}")
    print(f"  Разница: ${abs((shiwa_annual + etecsas_annual) - total_annual):,}")
    
    if abs((shiwa_annual + etecsas_annual) - total_annual) < 1:
        print("  ✅ Расчеты корректны!")
    else:
        print("  ❌ Ошибка в расчетах!")
    
    # Проверяем параметры подписки
    print()
    print("ПАРАМЕТРЫ ПОДПИСКИ:")
    print(f"  SHIWA подписка: ${calc.variant_params['monthly_subscription_shiwa']}/мес")
    print(f"  ETECSA подписка: ${calc.variant_params['monthly_subscription_etecsa']}/мес")
    print(f"  Итого: ${calc.variant_params['monthly_subscription_shiwa'] + calc.variant_params['monthly_subscription_etecsa']}/мес")

def check_different_scenarios():
    """Проверка разных сценариев"""
    print("\n=== ПРОВЕРКА РАЗНЫХ СЦЕНАРИЕВ ===")
    
    scenarios = ['baseline', 'optimistic', 'pessimistic']
    
    for scenario in scenarios:
        print(f"\n--- {scenario.upper()} ---")
        calc = BusinessCalculator(scenario, 'A', 'mini', 'shiwa_assembled')
        summary = calc.generate_financial_summary()
        
        total_monthly = summary['hotels_count'] * calc.scenario_params['monthly_fee']
        shiwa_annual = summary['shiwa']['subscription_revenue']
        etecsas_annual = summary['etecsa']['subscription_revenue']
        
        print(f"  Отелей: {summary['hotels_count']}")
        print(f"  Абонентская плата: ${calc.scenario_params['monthly_fee']}/мес")
        print(f"  Общая в месяц: ${total_monthly:,}")
        print(f"  SHIWA в год: ${shiwa_annual:,}")
        print(f"  ETECSA в год: ${etecsas_annual:,}")
        print(f"  Итого в год: ${shiwa_annual + etecsas_annual:,}")

if __name__ == "__main__":
    check_subscription_calculations()
    check_different_scenarios()
