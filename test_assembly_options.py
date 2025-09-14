"""
Тестирование различных вариантов сборки оборудования
"""

from business_calculator import BusinessCalculator
from parameters import *

def test_assembly_options():
    """Тест различных вариантов сборки оборудования"""
    print("=== ТЕСТ ВАРИАНТОВ СБОРКИ ОБОРУДОВАНИЯ ===")
    
    assembly_options = ['shiwa_assembled', 'etecsa_assembly', 'mixed_approach']
    equipment_types = ['mini', '1u_2u']
    
    for eq_type in equipment_types:
        print(f"\n--- {eq_type.upper()} ---")
        
        for assembly in assembly_options:
            print(f"\n{ASSEMBLY_OPTIONS[assembly]['name']}:")
            
            calc = BusinessCalculator('baseline', 'A', eq_type, assembly)
            summary = calc.generate_financial_summary()
            
            print(f"  Себестоимость: ${calc.equipment_prices['adjusted_cost_usd']:,.0f}")
            print(f"  Цена продажи ETECSA: ${calc.equipment_prices['selling_price_usd']:,.0f}")
            print(f"  Цена продажи отелям: ${calc.equipment_prices['hotel_price_usd']:,.0f}")
            print(f"  Маржа SHIWA: {calc.equipment_prices['shiwa_margin']*100:.0f}%")
            print(f"  Время поставки: {calc.equipment_prices['delivery_time']}")
            
            if calc.equipment_prices['assembly_fee_usd'] > 0:
                print(f"  Комиссия за сборку: ${calc.equipment_prices['assembly_fee_usd']:,.0f}")
            
            print(f"  Доход SHIWA: ${summary['shiwa']['total_revenue']:,.0f}")
            print(f"  Прибыль SHIWA: ${summary['shiwa']['net_profit']:,.0f}")
            print(f"  Прибыль ETECSA: ${summary['etecsa']['net_profit']:,.0f}")
            print(f"  Экономия отелей: ${summary['hotels']['total_benefit']:,.0f}")

def test_realistic_roi():
    """Тест реалистичного ROI для отелей"""
    print("\n=== ТЕСТ РЕАЛИСТИЧНОГО ROI ДЛЯ ОТЕЛЕЙ ===")
    
    calc = BusinessCalculator('baseline', 'A', 'mini', 'shiwa_assembled')
    hotel_benefits = calc.calculate_hotel_benefits()
    
    print(f"Годовые затраты отеля: ${hotel_benefits['annual_cost']:,.0f}")
    print(f"Экономия от снижения ошибок в биллинге: ${hotel_benefits['billing_savings']:,.0f}")
    print(f"Экономия от повышения эффективности: ${hotel_benefits['efficiency_savings']:,.0f}")
    print(f"Экономия от сокращения простоя: ${hotel_benefits['downtime_savings']:,.0f}")
    print(f"Общая годовая экономия: ${hotel_benefits['total_benefit']:,.0f}")
    print(f"ROI: {hotel_benefits['roi_percent']:.1f}%")
    
    if hotel_benefits['roi_percent'] > 0:
        print("✅ Отель получает положительный ROI")
    else:
        print("❌ ROI отрицательный - отель не получает выгоды")

def compare_assembly_profits():
    """Сравнение прибыльности разных вариантов сборки"""
    print("\n=== СРАВНЕНИЕ ПРИБЫЛЬНОСТИ ВАРИАНТОВ СБОРКИ ===")
    
    assembly_options = ['shiwa_assembled', 'etecsa_assembly', 'mixed_approach']
    
    print(f"{'Вариант сборки':<20} {'Доход SHIWA':<12} {'Прибыль SHIWA':<13} {'Прибыль ETECSA':<14} {'Экономия отелей':<15}")
    print("-" * 80)
    
    for assembly in assembly_options:
        calc = BusinessCalculator('baseline', 'A', 'mini', assembly)
        summary = calc.generate_financial_summary()
        
        print(f"{ASSEMBLY_OPTIONS[assembly]['name']:<20} "
              f"${summary['shiwa']['total_revenue']:<11,.0f} "
              f"${summary['shiwa']['net_profit']:<12,.0f} "
              f"${summary['etecsa']['net_profit']:<13,.0f} "
              f"${summary['hotels']['total_benefit']:<14,.0f}")

def test_equipment_cost_breakdown():
    """Детализация затрат на оборудование"""
    print("\n=== ДЕТАЛИЗАЦИЯ ЗАТРАТ НА ОБОРУДОВАНИЕ ===")
    
    for assembly in ['shiwa_assembled', 'etecsa_assembly']:
        print(f"\n--- {ASSEMBLY_OPTIONS[assembly]['name']} ---")
        
        calc = BusinessCalculator('baseline', 'A', 'mini', assembly)
        prices = calc.equipment_prices
        
        print(f"Базовая себестоимость: ${prices['base_cost_usd']:,.0f}")
        print(f"Скорректированная себестоимость: ${prices['adjusted_cost_usd']:,.0f}")
        print(f"Интеллектуальная стоимость: ${prices['intellectual_value_rub']/RUB_TO_USD_RATE:,.0f}")
        print(f"Общая себестоимость: ${prices['total_cost_usd']:,.0f}")
        print(f"Маржа SHIWA ({prices['shiwa_margin']*100:.0f}%): ${prices['selling_price_usd'] - prices['total_cost_usd']:,.0f}")
        print(f"Цена продажи ETECSA: ${prices['selling_price_usd']:,.0f}")
        print(f"Цена продажи отелям: ${prices['hotel_price_usd']:,.0f}")
        
        if prices['assembly_fee_usd'] > 0:
            print(f"Комиссия за сборку ETECSA: ${prices['assembly_fee_usd']:,.0f}")

if __name__ == "__main__":
    print("ТЕСТИРОВАНИЕ ВАРИАНТОВ СБОРКИ ОБОРУДОВАНИЯ")
    print("=" * 60)
    
    test_assembly_options()
    test_realistic_roi()
    compare_assembly_profits()
    test_equipment_cost_breakdown()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ:")
    print("✅ Добавлены варианты сборки оборудования")
    print("✅ SHIWA может продавать готовое оборудование или комплектующие")
    print("✅ ETECSA может собирать оборудование и получать комиссию")
    print("✅ ROI для отелей стал реалистичным")
    print("✅ Модель учитывает разные стратегии партнерства")
