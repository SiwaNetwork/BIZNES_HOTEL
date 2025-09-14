"""
Тест веб-API для проверки исправлений
"""

import requests
import json

def test_calculation_api():
    """Тест API расчета"""
    url = "http://127.0.0.1:5000/api/calculate"
    
    # Тестовые данные
    test_data = {
        "scenario": "baseline",
        "variant": "A", 
        "hotels_count": 50,
        "monthly_fee": 500,
        "equipment_type": "mini",
        "assembly_option": "shiwa_assembled",
        "assembly_variant": "80_20",
        "exchange_rate": 78
    }
    
    try:
        print("Отправляем запрос на расчет...")
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Расчет успешен!")
            summary = result.get('data', {}).get('summary', {})
            print(f"Доход SHIWA: ${summary.get('shiwa', {}).get('total_revenue', 0):,.0f}")
            print(f"Прибыль SHIWA: ${summary.get('shiwa', {}).get('net_profit', 0):,.0f}")
            print(f"Прибыль ETECSA: ${summary.get('etecsa', {}).get('net_profit', 0):,.0f}")
            print(f"Экономия отелей: ${summary.get('hotels', {}).get('total_benefit', 0):,.0f}")
            print(f"Вариант сборки: {summary.get('assembly_name', 'N/A')}")
            print(f"Оборудование: {summary.get('equipment_name', 'N/A')}")
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return False

def test_different_assembly_options():
    """Тест разных вариантов сборки"""
    url = "http://127.0.0.1:5000/api/calculate"
    
    assembly_options = ["shiwa_assembled", "etecsa_assembly", "mixed_approach"]
    
    print("\n=== ТЕСТ РАЗНЫХ ВАРИАНТОВ СБОРКИ ===")
    
    for assembly in assembly_options:
        test_data = {
            "scenario": "baseline",
            "variant": "A",
            "hotels_count": 50,
            "monthly_fee": 500,
            "equipment_type": "mini",
            "assembly_option": assembly,
            "assembly_variant": "80_20"
        }
        
        try:
            response = requests.post(url, json=test_data)
            if response.status_code == 200:
                result = response.json()
                summary = result.get('data', {}).get('summary', {})
                print(f"\n{assembly}:")
                print(f"  Доход SHIWA: ${summary.get('shiwa', {}).get('total_revenue', 0):,.0f}")
                print(f"  Прибыль SHIWA: ${summary.get('shiwa', {}).get('net_profit', 0):,.0f}")
                print(f"  Прибыль ETECSA: ${summary.get('etecsa', {}).get('net_profit', 0):,.0f}")
            else:
                print(f"❌ Ошибка для {assembly}: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка для {assembly}: {e}")

if __name__ == "__main__":
    print("ТЕСТ ВЕБ-API")
    print("=" * 50)
    
    # Ждем немного, чтобы сервер запустился
    import time
    time.sleep(2)
    
    success = test_calculation_api()
    
    if success:
        test_different_assembly_options()
        print("\n✅ Все тесты пройдены успешно!")
    else:
        print("\n❌ Основной тест не прошел")
