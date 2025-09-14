"""
Тестирование различных вариантов оборудования и локальной сборки
"""

from business_calculator import BusinessCalculator
from parameters import *

def test_equipment_types():
    """Тест различных типов оборудования"""
    print("=== ТЕСТ ТИПОВ ОБОРУДОВАНИЯ ===")
    
    equipment_types = ['mini', '1u_2u']
    
    for eq_type in equipment_types:
        print(f"\n--- {eq_type.upper()} ---")
        
        # Тест без локальной сборки
        calc = BusinessCalculator('baseline', 'B', eq_type, False)
        summary = calc.generate_financial_summary()
        
        print(f"Оборудование: {summary['equipment_name']}")
        print(f"Локальная сборка: {summary['local_assembly']}")
        print(f"Себестоимость: ${calc.equipment_prices['cost_price_usd']:,.0f}")
        print(f"Цена продажи ETECSA: ${calc.equipment_prices['selling_price_usd']:,.0f}")
        print(f"Доход SHIWA: ${summary['shiwa']['total_revenue']:,.0f}")
        print(f"Прибыль SHIWA: ${summary['shiwa']['net_profit']:,.0f}")
        print(f"ROI SHIWA: {summary['shiwa']['roi']:.1f}%")

def test_local_assembly_variants():
    """Тест вариантов локальной сборки"""
    print("\n=== ТЕСТ ЛОКАЛЬНОЙ СБОРКИ ===")
    
    assembly_variants = ['80_20', '50_50']
    equipment_types = ['mini', '1u_2u']
    
    for eq_type in equipment_types:
        print(f"\n--- {eq_type.upper()} ---")
        
        for variant in assembly_variants:
            print(f"\nВариант {variant}:")
            
            calc = BusinessCalculator('baseline', 'B', eq_type, True, variant)
            summary = calc.generate_financial_summary()
            
            print(f"  Оборудование: {summary['equipment_name']}")
            print(f"  Локальная сборка: {summary['local_assembly']}")
            print(f"  Распределение: {variant}")
            print(f"  Себестоимость: ${calc.equipment_prices['cost_price_usd']:,.0f}")
            print(f"  Доход SHIWA: ${summary['shiwa']['total_revenue']:,.0f}")
            print(f"  Прибыль SHIWA: ${summary['shiwa']['net_profit']:,.0f}")
            print(f"  Прибыль ETECSA: ${summary['etecsa']['net_profit']:,.0f}")
            print(f"  ROI SHIWA: {summary['shiwa']['roi']:.1f}%")

def test_equipment_comparison():
    """Сравнение типов оборудования"""
    print("\n=== СРАВНЕНИЕ ТИПОВ ОБОРУДОВАНИЯ ===")
    
    scenarios = [
        ('mini', False, '80_20'),
        ('mini', True, '80_20'),
        ('mini', True, '50_50'),
        ('1u_2u', False, '80_20'),
        ('1u_2u', True, '80_20'),
        ('1u_2u', True, '50_50')
    ]
    
    results = []
    
    for eq_type, local_assembly, assembly_variant in scenarios:
        calc = BusinessCalculator('baseline', 'B', eq_type, local_assembly, assembly_variant)
        summary = calc.generate_financial_summary()
        
        results.append({
            'equipment': eq_type,
            'local_assembly': local_assembly,
            'variant': assembly_variant,
            'equipment_name': summary['equipment_name'],
            'shiwa_revenue': summary['shiwa']['total_revenue'],
            'shiwa_profit': summary['shiwa']['net_profit'],
            'etecsa_profit': summary['etecsa']['net_profit'],
            'shiwa_roi': summary['shiwa']['roi']
        })
    
    print(f"{'Тип':<8} {'Лок.сборка':<10} {'Вариант':<8} {'Доход SHIWA':<12} {'Прибыль SHIWA':<13} {'Прибыль ETECSA':<14} {'ROI SHIWA':<10}")
    print("-" * 90)
    
    for result in results:
        print(f"{result['equipment']:<8} {'Да' if result['local_assembly'] else 'Нет':<10} "
              f"{result['variant']:<8} ${result['shiwa_revenue']:<11,.0f} "
              f"${result['shiwa_profit']:<12,.0f} ${result['etecsa_profit']:<13,.0f} "
              f"{result['shiwa_roi']:<9.1f}%")

def test_cost_benefit_analysis():
    """Анализ затрат и выгод"""
    print("\n=== АНАЛИЗ ЗАТРАТ И ВЫГОД ===")
    
    # Сравниваем затраты на локальную сборку
    print("\nЗатраты на локальную сборку:")
    print(f"Обучение персонала: ${LOCAL_ASSEMBLY_COSTS['training_cost_usd']:,}")
    print(f"Подготовка производства: ${LOCAL_ASSEMBLY_COSTS['setup_cost_usd']:,}")
    print(f"Ежемесячная поддержка: ${LOCAL_ASSEMBLY_COSTS['monthly_support_cost_usd']:,}")
    
    # Анализируем выгоды от снижения себестоимости
    print("\nВыгоды от снижения себестоимости:")
    
    for eq_type in ['mini', '1u_2u']:
        eq_info = EQUIPMENT_TYPES[eq_type]
        reduction = eq_info['local_assembly_reduction']
        original_cost = eq_info['cost_rub'] / RUB_TO_USD_RATE
        reduced_cost = original_cost * (1 - reduction)
        savings = original_cost - reduced_cost
        
        print(f"{eq_type.upper()}: ${savings:,.0f} экономии на единицу ({reduction*100:.0f}%)")

def test_scenario_with_equipment():
    """Тест сценариев с разным оборудованием"""
    print("\n=== ТЕСТ СЦЕНАРИЕВ С ОБОРУДОВАНИЕМ ===")
    
    scenarios = ['baseline', 'optimistic', 'pessimistic']
    equipment_types = ['mini', '1u_2u']
    
    for scenario in scenarios:
        print(f"\n--- {scenario.upper()} СЦЕНАРИЙ ---")
        
        for eq_type in equipment_types:
            calc = BusinessCalculator(scenario, 'B', eq_type, True, '80_20')
            summary = calc.generate_financial_summary()
            
            print(f"  {eq_type.upper()}: Доход=${summary['shiwa']['total_revenue']:,.0f}, "
                  f"Прибыль=${summary['shiwa']['net_profit']:,.0f}, ROI={summary['shiwa']['roi']:.1f}%")

if __name__ == "__main__":
    print("ТЕСТИРОВАНИЕ ВАРИАНТОВ ОБОРУДОВАНИЯ И ЛОКАЛЬНОЙ СБОРКИ")
    print("=" * 60)
    
    test_equipment_types()
    test_local_assembly_variants()
    test_equipment_comparison()
    test_cost_benefit_analysis()
    test_scenario_with_equipment()
    
    print("\n" + "=" * 60)
    print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
    print("\nНовые возможности:")
    print("✅ Выбор типа оборудования (Mini vs 1U/2U)")
    print("✅ Локальная сборка на Кубе")
    print("✅ Варианты распределения доходов (80/20 и 50/50)")
    print("✅ Автоматический расчет себестоимости")
    print("✅ Учет затрат на локальную сборку")
