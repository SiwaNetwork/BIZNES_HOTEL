"""
Проверка модели аренды оборудования (вариант Б)
"""

from business_calculator import BusinessCalculator

def check_rental_model():
    """Проверка модели аренды оборудования"""
    print("=== ПРОВЕРКА МОДЕЛИ АРЕНДЫ ОБОРУДОВАНИЯ ===")
    
    # Вариант Б: Аренда оборудования (80/20)
    calc = BusinessCalculator('baseline', 'B', 'mini', 'shiwa_assembled', '80_20')
    summary = calc.generate_financial_summary()
    
    print(f"Сценарий: {summary['scenario']}")
    print(f"Вариант: {summary['variant']}")
    print(f"Количество отелей: {summary['hotels_count']}")
    print(f"Абонентская плата: ${calc.scenario_params['monthly_fee']}/мес")
    print()
    
    # Общая абонентская плата
    total_monthly = summary['hotels_count'] * calc.scenario_params['monthly_fee']
    total_annual = total_monthly * 12
    
    print(f"ОБЩАЯ АБОНЕНТСКАЯ ПЛАТА:")
    print(f"  В месяц: ${total_monthly:,}")
    print(f"  В год: ${total_annual:,}")
    print()
    
    # Распределение по модели 80/20
    shiwa_share = 0.8  # 80% для SHIWA
    etecsas_share = 0.2  # 20% для ETECSA
    
    expected_shiwa_annual = total_annual * shiwa_share
    expected_etecsas_annual = total_annual * etecsas_share
    
    print(f"ОЖИДАЕМОЕ РАСПРЕДЕЛЕНИЕ (80/20):")
    print(f"  SHIWA (80%): ${expected_shiwa_annual:,} в год")
    print(f"  ETECSA (20%): ${expected_etecsas_annual:,} в год")
    print()
    
    # Фактические результаты
    actual_shiwa = summary['shiwa']['total_revenue']
    actual_etecsa = summary['etecsa']['equipment_profit'] + summary['etecsa']['subscription_revenue']
    
    print(f"ФАКТИЧЕСКИЕ РЕЗУЛЬТАТЫ:")
    print(f"  SHIWA: ${actual_shiwa:,}")
    print(f"  ETECSA: ${actual_etecsa:,}")
    print()
    
    # Проверка
    print(f"ПРОВЕРКА:")
    print(f"  Разница SHIWA: ${actual_shiwa - expected_shiwa_annual:,}")
    print(f"  Разница ETECSA: ${actual_etecsa - expected_etecsas_annual:,}")
    
    if abs(actual_shiwa - expected_shiwa_annual) < 1000:
        print("  ✅ Расчеты SHIWA корректны!")
    else:
        print("  ❌ Ошибка в расчетах SHIWA!")
    
    if abs(actual_etecsa - expected_etecsas_annual) < 1000:
        print("  ✅ Расчеты ETECSA корректны!")
    else:
        print("  ❌ Ошибка в расчетах ETECSA!")
    
    # Детальная проверка
    print()
    print("ДЕТАЛЬНАЯ ПРОВЕРКА:")
    shiwa_revenue = calc.calculate_shiwa_revenue()
    etecsas_revenue = calc.calculate_etecsa_revenue()
    
    print(f"  SHIWA equipment_revenue: ${shiwa_revenue['equipment_revenue']:,}")
    print(f"  SHIWA subscription_revenue: ${shiwa_revenue['subscription_revenue']:,}")
    print(f"  ETECSA equipment_profit: ${etecsas_revenue['equipment_profit']:,}")
    print(f"  ETECSA subscription_revenue: ${etecsas_revenue['subscription_revenue']:,}")

def check_assembly_variants():
    """Проверка разных вариантов распределения"""
    print("\n=== ПРОВЕРКА ВАРИАНТОВ РАСПРЕДЕЛЕНИЯ ===")
    
    variants = ['80_20', '50_50']
    
    for variant in variants:
        print(f"\n--- {variant} ---")
        calc = BusinessCalculator('baseline', 'B', 'mini', 'shiwa_assembled', variant)
        summary = calc.generate_financial_summary()
        
        total_annual = 50 * 500 * 12  # 50 отелей × $500 × 12 месяцев
        
        if variant == '80_20':
            expected_shiwa = total_annual * 0.8
            expected_etecsa = total_annual * 0.2
        else:  # 50_50
            expected_shiwa = total_annual * 0.5
            expected_etecsa = total_annual * 0.5
        
        actual_shiwa = summary['shiwa']['total_revenue']
        actual_etecsa = summary['etecsa']['equipment_profit'] + summary['etecsa']['subscription_revenue']
        
        print(f"  Ожидается SHIWA: ${expected_shiwa:,}")
        print(f"  Фактически SHIWA: ${actual_shiwa:,}")
        print(f"  Ожидается ETECSA: ${expected_etecsa:,}")
        print(f"  Фактически ETECSA: ${actual_etecsa:,}")

if __name__ == "__main__":
    check_rental_model()
    check_assembly_variants()
