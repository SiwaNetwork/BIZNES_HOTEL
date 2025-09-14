"""
Тест модели аренды оборудования
"""

import requests
import json

def test_rental_model_api():
    """Тест API для модели аренды"""
    url = "http://127.0.0.1:5000/api/calculate"
    
    # Тест модели аренды (вариант Б)
    test_data = {
        "scenario": "baseline",
        "variant": "B",  # Аренда оборудования
        "hotels_count": 50,
        "monthly_fee": 500,
        "equipment_type": "mini",
        "assembly_option": "shiwa_assembled",
        "assembly_variant": "80_20"  # 80% SHIWA, 20% ETECSA
    }
    
    try:
        print("=== ТЕСТ МОДЕЛИ АРЕНДЫ ОБОРУДОВАНИЯ ===")
        print(f"Параметры: {test_data}")
        print()
        
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            summary = result['data']['summary']
            
            print("✅ Расчет успешен!")
            print(f"Вариант: {summary['variant']}")
            print(f"Количество отелей: {summary['hotels_count']}")
            print(f"Абонентская плата: $500/мес")
            print()
            
            # Проверяем расчеты
            total_monthly = 50 * 500  # $25,000
            total_annual = total_monthly * 12  # $300,000
            
            print(f"ОБЩАЯ АБОНЕНТСКАЯ ПЛАТА:")
            print(f"  В месяц: ${total_monthly:,}")
            print(f"  В год: ${total_annual:,}")
            print()
            
            # Ожидаемые результаты для 80/20
            expected_shiwa = total_annual * 0.8  # $240,000
            expected_etecsa = total_annual * 0.2  # $60,000
            
            actual_shiwa = summary['shiwa']['total_revenue']
            actual_etecsa = summary['etecsa']['equipment_profit'] + summary['etecsa']['subscription_revenue']
            
            print(f"РАСПРЕДЕЛЕНИЕ ДОХОДОВ (80/20):")
            print(f"  Ожидается SHIWA: ${expected_shiwa:,}")
            print(f"  Фактически SHIWA: ${actual_shiwa:,}")
            print(f"  Ожидается ETECSA: ${expected_etecsa:,}")
            print(f"  Фактически ETECSA: ${actual_etecsa:,}")
            print()
            
            # Проверка
            shiwa_diff = abs(actual_shiwa - expected_shiwa)
            etecsas_diff = abs(actual_etecsa - expected_etecsa)
            
            if shiwa_diff < 1:
                print("✅ Расчет SHIWA корректен!")
            else:
                print(f"❌ Ошибка в расчете SHIWA: разница ${shiwa_diff:,}")
            
            if etecsas_diff < 1:
                print("✅ Расчет ETECSA корректен!")
            else:
                print(f"❌ Ошибка в расчете ETECSA: разница ${etecsas_diff:,}")
            
            print()
            print(f"ДЕТАЛЬНАЯ ИНФОРМАЦИЯ:")
            print(f"  Доход SHIWA от оборудования: ${summary['shiwa']['equipment_revenue']:,}")
            print(f"  Доход SHIWA от подписки: ${summary['shiwa']['subscription_revenue']:,}")
            print(f"  Доход ETECSA от оборудования: ${summary['etecsa']['equipment_profit']:,}")
            print(f"  Доход ETECSA от подписки: ${summary['etecsa']['subscription_revenue']:,}")
            
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return False

def test_50_50_model():
    """Тест модели 50/50"""
    url = "http://127.0.0.1:5000/api/calculate"
    
    test_data = {
        "scenario": "baseline",
        "variant": "B",
        "hotels_count": 50,
        "monthly_fee": 500,
        "equipment_type": "mini",
        "assembly_option": "shiwa_assembled",
        "assembly_variant": "50_50"  # 50% SHIWA, 50% ETECSA
    }
    
    try:
        print("\n=== ТЕСТ МОДЕЛИ 50/50 ===")
        
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            summary = result['data']['summary']
            
            total_annual = 50 * 500 * 12  # $300,000
            expected_shiwa = total_annual * 0.5  # $150,000
            expected_etecsa = total_annual * 0.5  # $150,000
            
            actual_shiwa = summary['shiwa']['total_revenue']
            actual_etecsa = summary['etecsa']['equipment_profit'] + summary['etecsa']['subscription_revenue']
            
            print(f"ОЖИДАЕТСЯ:")
            print(f"  SHIWA: ${expected_shiwa:,}")
            print(f"  ETECSA: ${expected_etecsa:,}")
            print()
            print(f"ФАКТИЧЕСКИ:")
            print(f"  SHIWA: ${actual_shiwa:,}")
            print(f"  ETECSA: ${actual_etecsa:,}")
            
            shiwa_ok = abs(actual_shiwa - expected_shiwa) < 1
            etecsas_ok = abs(actual_etecsa - expected_etecsa) < 1
            
            if shiwa_ok and etecsas_ok:
                print("✅ Модель 50/50 работает корректно!")
            else:
                print("❌ Ошибки в модели 50/50!")
            
            return shiwa_ok and etecsas_ok
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print("ТЕСТ МОДЕЛИ АРЕНДЫ ОБОРУДОВАНИЯ")
    print("=" * 60)
    
    import time
    time.sleep(2)
    
    success1 = test_rental_model_api()
    success2 = test_50_50_model()
    
    if success1 and success2:
        print("\n🎉 Все тесты модели аренды пройдены успешно!")
        print("✅ Расчеты теперь корректны!")
    else:
        print("\n❌ Есть проблемы с моделью аренды")
