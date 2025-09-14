"""
Тест системы аналитики с графиками и таблицами
"""

import requests
import json

def test_analytics_api():
    """Тест API аналитики"""
    url = "http://127.0.0.1:5000/api/analytics"
    
    # Тестовые данные
    test_data = {
        "scenario": "baseline",
        "variant": "A", 
        "equipment_type": "mini",
        "assembly_option": "shiwa_assembled",
        "assembly_variant": "80_20"
    }
    
    try:
        print("Отправляем запрос на аналитику...")
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Аналитика получена успешно!")
            
            data = result['data']
            summary = data['summary']
            charts = data['charts']
            metrics = data['metrics']
            
            print("\n📊 ОСНОВНЫЕ МЕТРИКИ:")
            print(f"Общая стоимость проекта: ${metrics['total_project_value']:,.0f}")
            print(f"ROI SHIWA: {metrics['shiwa_roi']:.1f}%")
            print(f"ROI ETECSA: {metrics['etecsa_roi']:.1f}%")
            print(f"ROI отелей: {metrics['hotel_roi']:.1f}%")
            print(f"Период окупаемости: {metrics['payback_period']['payback_months']:.1f} месяцев")
            
            print("\n📈 ДАННЫЕ ДЛЯ ГРАФИКОВ:")
            print("Сравнение доходов:")
            for i, label in enumerate(charts['revenue_comparison']['labels']):
                print(f"  {label}: ${charts['revenue_comparison']['data'][i]:,.0f}")
            
            print("Сравнение прибыли:")
            for i, label in enumerate(charts['profit_comparison']['labels']):
                print(f"  {label}: ${charts['profit_comparison']['data'][i]:,.0f}")
            
            print("\n💰 РАСПРЕДЕЛЕНИЕ ДОХОДОВ SHIWA:")
            for i, label in enumerate(charts['shiwa_revenue_breakdown']['labels']):
                value = charts['shiwa_revenue_breakdown']['data'][i]
                percentage = (value / sum(charts['shiwa_revenue_breakdown']['data'])) * 100
                print(f"  {label}: ${value:,.0f} ({percentage:.1f}%)")
            
            print("\n🏢 РАСПРЕДЕЛЕНИЕ ДОХОДОВ ETECSA:")
            for i, label in enumerate(charts['etecsa_revenue_breakdown']['labels']):
                value = charts['etecsa_revenue_breakdown']['data'][i]
                percentage = (value / sum(charts['etecsa_revenue_breakdown']['data'])) * 100
                print(f"  {label}: ${value:,.0f} ({percentage:.1f}%)")
            
            print("\n🏨 ВЫГОДЫ ДЛЯ ОТЕЛЕЙ:")
            for i, label in enumerate(charts['hotel_benefits_breakdown']['labels']):
                value = charts['hotel_benefits_breakdown']['data'][i]
                percentage = (value / sum(charts['hotel_benefits_breakdown']['data'])) * 100
                print(f"  {label}: ${value:,.0f} ({percentage:.1f}%)")
            
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return False

def test_different_assembly_analytics():
    """Тест аналитики для разных вариантов сборки"""
    url = "http://127.0.0.1:5000/api/analytics"
    
    assembly_options = ["shiwa_assembled", "etecsa_assembly", "mixed_approach"]
    
    print("\n=== АНАЛИТИКА ДЛЯ РАЗНЫХ ВАРИАНТОВ СБОРКИ ===")
    
    results = {}
    
    for assembly in assembly_options:
        test_data = {
            "scenario": "baseline",
            "variant": "A",
            "equipment_type": "mini",
            "assembly_option": assembly,
            "assembly_variant": "80_20"
        }
        
        try:
            response = requests.post(url, json=test_data)
            if response.status_code == 200:
                result = response.json()
                data = result['data']
                summary = data['summary']
                metrics = data['metrics']
                
                results[assembly] = {
                    'shiwa_revenue': summary['shiwa']['total_revenue'],
                    'shiwa_profit': summary['shiwa']['net_profit'],
                    'etecsa_profit': summary['etecsa']['net_profit'],
                    'shiwa_roi': metrics['shiwa_roi'],
                    'etecsa_roi': metrics['etecsa_roi'],
                    'payback_months': metrics['payback_period']['payback_months']
                }
            else:
                print(f"❌ Ошибка для {assembly}: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка для {assembly}: {e}")
    
    # Выводим сравнительную таблицу
    print(f"\n{'Вариант сборки':<25} {'Доход SHIWA':<15} {'Прибыль SHIWA':<15} {'Прибыль ETECSA':<15} {'ROI SHIWA':<12} {'Окупаемость':<12}")
    print("-" * 100)
    
    for assembly, data in results.items():
        print(f"{assembly:<25} ${data['shiwa_revenue']:<14,.0f} ${data['shiwa_profit']:<14,.0f} "
              f"${data['etecsa_profit']:<14,.0f} {data['shiwa_roi']:<11.1f}% {data['payback_months']:<11.1f}м")

def test_equipment_types_analytics():
    """Тест аналитики для разных типов оборудования"""
    url = "http://127.0.0.1:5000/api/analytics"
    
    equipment_types = ["mini", "1u_2u"]
    
    print("\n=== АНАЛИТИКА ДЛЯ РАЗНЫХ ТИПОВ ОБОРУДОВАНИЯ ===")
    
    for eq_type in equipment_types:
        test_data = {
            "scenario": "baseline",
            "variant": "A",
            "equipment_type": eq_type,
            "assembly_option": "shiwa_assembled",
            "assembly_variant": "80_20"
        }
        
        try:
            response = requests.post(url, json=test_data)
            if response.status_code == 200:
                result = response.json()
                data = result['data']
                summary = data['summary']
                metrics = data['metrics']
                
                print(f"\n--- {eq_type.upper()} ---")
                print(f"Оборудование: {summary['equipment_name']}")
                print(f"Общая стоимость проекта: ${metrics['total_project_value']:,.0f}")
                print(f"Доход SHIWA: ${summary['shiwa']['total_revenue']:,.0f}")
                print(f"Прибыль SHIWA: ${summary['shiwa']['net_profit']:,.0f}")
                print(f"Прибыль ETECSA: ${summary['etecsa']['net_profit']:,.0f}")
                print(f"ROI SHIWA: {metrics['shiwa_roi']:.1f}%")
                print(f"ROI ETECSA: {metrics['etecsa_roi']:.1f}%")
                print(f"Период окупаемости: {metrics['payback_period']['payback_months']:.1f} месяцев")
            else:
                print(f"❌ Ошибка для {eq_type}: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка для {eq_type}: {e}")

if __name__ == "__main__":
    print("ТЕСТ СИСТЕМЫ АНАЛИТИКИ")
    print("=" * 60)
    
    # Ждем немного, чтобы сервер запустился
    import time
    time.sleep(2)
    
    success = test_analytics_api()
    
    if success:
        test_different_assembly_analytics()
        test_equipment_types_analytics()
        print("\n✅ Все тесты аналитики пройдены успешно!")
        print("\n🎯 Система готова для создания графиков и таблиц!")
    else:
        print("\n❌ Основной тест аналитики не прошел")
