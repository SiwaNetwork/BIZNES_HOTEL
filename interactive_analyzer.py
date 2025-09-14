"""
Интерактивный анализатор бизнес-модели
Позволяет изменять параметры и сразу видеть результаты
"""

from business_calculator import BusinessCalculator, quick_analysis
from scenario_analyzer import ScenarioAnalyzer
import json

class InteractiveAnalyzer:
    """Интерактивный анализатор для изменения параметров"""
    
    def __init__(self):
        self.current_scenario = 'baseline'
        self.current_variant = 'B'
        self.custom_params = {}
    
    def show_current_parameters(self):
        """Показать текущие параметры"""
        calc = BusinessCalculator(self.current_scenario, self.current_variant)
        
        print("=== ТЕКУЩИЕ ПАРАМЕТРЫ ===")
        print(f"Сценарий: {self.current_scenario}")
        print(f"Вариант: {self.current_variant}")
        print(f"Количество отелей: {calc.scenario_params['hotels_count']}")
        print(f"Абонентская плата: ${calc.scenario_params['monthly_fee']}")
        print(f"Курс рубль/доллар: {calc.equipment_prices.get('rub_to_usd_rate', 78)}")
        print(f"Себестоимость оборудования: ${calc.equipment_prices['cost_price_usd']:,.0f}")
        print(f"Цена продажи ETECSA: ${calc.equipment_prices['selling_price_usd']:,.0f}")
        print()
    
    def change_scenario(self, scenario):
        """Изменить сценарий"""
        valid_scenarios = ['baseline', 'optimistic', 'pessimistic']
        if scenario in valid_scenarios:
            self.current_scenario = scenario
            print(f"Сценарий изменен на: {scenario}")
        else:
            print(f"Неверный сценарий. Доступные: {valid_scenarios}")
    
    def change_variant(self, variant):
        """Изменить вариант монетизации"""
        valid_variants = ['A', 'B']
        if variant.upper() in valid_variants:
            self.current_variant = variant.upper()
            print(f"Вариант изменен на: {variant.upper()}")
        else:
            print(f"Неверный вариант. Доступные: {valid_variants}")
    
    def change_hotels_count(self, count):
        """Изменить количество отелей"""
        try:
            count = int(count)
            if count > 0:
                self.custom_params['hotels_count'] = count
                print(f"Количество отелей изменено на: {count}")
            else:
                print("Количество отелей должно быть положительным числом")
        except ValueError:
            print("Неверный формат числа")
    
    def change_monthly_fee(self, fee):
        """Изменить абонентскую плату"""
        try:
            fee = float(fee)
            if fee > 0:
                self.custom_params['monthly_fee'] = fee
                print(f"Абонентская плата изменена на: ${fee}")
            else:
                print("Абонентская плата должна быть положительным числом")
        except ValueError:
            print("Неверный формат числа")
    
    def change_equipment_cost(self, cost):
        """Изменить себестоимость оборудования"""
        try:
            cost = float(cost)
            if cost > 0:
                self.custom_params['equipment_cost'] = cost
                print(f"Себестоимость оборудования изменена на: ${cost:,.0f}")
            else:
                print("Себестоимость должна быть положительным числом")
        except ValueError:
            print("Неверный формат числа")
    
    def change_exchange_rate(self, rate):
        """Изменить курс валют"""
        try:
            rate = float(rate)
            if rate > 0:
                self.custom_params['rub_to_usd_rate'] = rate
                print(f"Курс рубль/доллар изменен на: {rate}")
            else:
                print("Курс должен быть положительным числом")
        except ValueError:
            print("Неверный формат числа")
    
    def create_custom_calculator(self):
        """Создать калькулятор с пользовательскими параметрами"""
        calc = BusinessCalculator(self.current_scenario, self.current_variant)
        
        # Применяем пользовательские параметры
        if 'hotels_count' in self.custom_params:
            calc.scenario_params['hotels_count'] = self.custom_params['hotels_count']
        
        if 'monthly_fee' in self.custom_params:
            calc.scenario_params['monthly_fee'] = self.custom_params['monthly_fee']
        
        if 'equipment_cost' in self.custom_params:
            calc.equipment_prices['cost_price_usd'] = self.custom_params['equipment_cost']
            # Пересчитываем цену продажи
            calc.equipment_prices['selling_price_usd'] = (
                self.custom_params['equipment_cost'] + 
                calc.equipment_prices['intellectual_value_rub'] / 
                (self.custom_params.get('rub_to_usd_rate', 78))
            )
        
        if 'rub_to_usd_rate' in self.custom_params:
            # Пересчитываем все цены в долларах
            rate = self.custom_params['rub_to_usd_rate']
            calc.equipment_prices['cost_price_usd'] = calc.equipment_prices['cost_price_rub'] / rate
            calc.equipment_prices['selling_price_usd'] = calc.equipment_prices['selling_price_rub'] / rate
            calc.equipment_prices['hotel_price_usd'] = calc.equipment_prices['hotel_price_rub'] / rate
        
        return calc
    
    def run_analysis_with_custom_params(self):
        """Запустить анализ с пользовательскими параметрами"""
        calc = self.create_custom_calculator()
        summary = calc.generate_financial_summary()
        payback = calc.calculate_payback_period()
        
        print("=== АНАЛИЗ С ПОЛЬЗОВАТЕЛЬСКИМИ ПАРАМЕТРАМИ ===")
        print(f"Сценарий: {summary['scenario']}")
        print(f"Вариант: {summary['variant']}")
        print(f"Количество отелей: {summary['effective_hotels']:.0f}")
        print(f"Абонентская плата: ${summary.get('monthly_fee', 500)}")
        print()
        
        print(f"=== SHIWA NETWORK ===")
        print(f"Общий доход: ${summary['shiwa']['total_revenue']:,.0f}")
        print(f"Общие затраты: ${summary['shiwa']['total_costs']:,.0f}")
        print(f"Чистая прибыль: ${summary['shiwa']['net_profit']:,.0f}")
        print(f"Рентабельность: {summary['shiwa']['profit_margin']:.1f}%")
        print(f"ROI: {summary['shiwa']['roi']:.1f}%")
        if payback:
            print(f"Окупаемость: {payback['payback_months']:.1f} месяцев")
        print()
        
        print(f"=== ETECSA ===")
        print(f"Чистая прибыль: ${summary['etecsa']['net_profit']:,.0f}")
        print()
        
        print(f"=== ОТЕЛИ ===")
        print(f"Годовые затраты: ${summary['hotels']['annual_cost']:,.0f}")
        print(f"Годовая выгода: ${summary['hotels']['total_benefit']:,.0f}")
        print(f"ROI: {summary['hotels']['roi']:.0f}%")
        print()
        
        return summary
    
    def save_custom_scenario(self, name):
        """Сохранить пользовательский сценарий"""
        calc = self.create_custom_calculator()
        summary = calc.generate_financial_summary()
        
        custom_scenario = {
            'name': name,
            'parameters': self.custom_params.copy(),
            'scenario': self.current_scenario,
            'variant': self.current_variant,
            'results': summary,
            'timestamp': calc.generate_financial_summary()  # Добавляем временную метку
        }
        
        filename = f"custom_scenario_{name.lower().replace(' ', '_')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(custom_scenario, f, ensure_ascii=False, indent=2)
        
        print(f"Пользовательский сценарий '{name}' сохранен в файл: {filename}")
    
    def load_custom_scenario(self, filename):
        """Загрузить пользовательский сценарий"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                scenario_data = json.load(f)
            
            self.custom_params = scenario_data['parameters']
            self.current_scenario = scenario_data['scenario']
            self.current_variant = scenario_data['variant']
            
            print(f"Сценарий '{scenario_data['name']}' загружен")
            self.show_current_parameters()
            
        except FileNotFoundError:
            print(f"Файл {filename} не найден")
        except json.JSONDecodeError:
            print(f"Ошибка при чтении файла {filename}")
    
    def show_menu(self):
        """Показать меню интерактивного анализатора"""
        print("=" * 50)
        print("ИНТЕРАКТИВНЫЙ АНАЛИЗАТОР БИЗНЕС-МОДЕЛИ")
        print("=" * 50)
        print()
        print("Доступные команды:")
        print("1. show - показать текущие параметры")
        print("2. scenario <baseline|optimistic|pessimistic> - изменить сценарий")
        print("3. variant <A|B> - изменить вариант монетизации")
        print("4. hotels <число> - изменить количество отелей")
        print("5. fee <сумма> - изменить абонентскую плату")
        print("6. cost <сумма> - изменить себестоимость оборудования")
        print("7. rate <курс> - изменить курс рубль/доллар")
        print("8. analyze - запустить анализ с текущими параметрами")
        print("9. save <имя> - сохранить текущий сценарий")
        print("10. load <файл> - загрузить сценарий из файла")
        print("11. menu - показать это меню")
        print("12. quit - выход")
        print()
    
    def run_interactive_session(self):
        """Запустить интерактивную сессию"""
        self.show_menu()
        
        while True:
            try:
                command = input("Введите команду: ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    print("До свидания!")
                    break
                elif command == 'menu':
                    self.show_menu()
                elif command == 'show':
                    self.show_current_parameters()
                elif command.startswith('scenario '):
                    scenario = command.split(' ', 1)[1]
                    self.change_scenario(scenario)
                elif command.startswith('variant '):
                    variant = command.split(' ', 1)[1]
                    self.change_variant(variant)
                elif command.startswith('hotels '):
                    count = command.split(' ', 1)[1]
                    self.change_hotels_count(count)
                elif command.startswith('fee '):
                    fee = command.split(' ', 1)[1]
                    self.change_monthly_fee(fee)
                elif command.startswith('cost '):
                    cost = command.split(' ', 1)[1]
                    self.change_equipment_cost(cost)
                elif command.startswith('rate '):
                    rate = command.split(' ', 1)[1]
                    self.change_exchange_rate(rate)
                elif command == 'analyze':
                    self.run_analysis_with_custom_params()
                elif command.startswith('save '):
                    name = command.split(' ', 1)[1]
                    self.save_custom_scenario(name)
                elif command.startswith('load '):
                    filename = command.split(' ', 1)[1]
                    self.load_custom_scenario(filename)
                else:
                    print("Неизвестная команда. Введите 'menu' для просмотра доступных команд.")
                
                print()
                
            except KeyboardInterrupt:
                print("\nДо свидания!")
                break
            except Exception as e:
                print(f"Ошибка: {e}")

def quick_interactive_analysis():
    """Быстрый запуск интерактивного анализа"""
    analyzer = InteractiveAnalyzer()
    analyzer.run_interactive_session()

if __name__ == "__main__":
    quick_interactive_analysis()
