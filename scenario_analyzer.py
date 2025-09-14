"""
Анализатор сценариев развития проекта QUANTUM
Инструменты для анализа различных вариантов развития проекта
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from business_calculator import BusinessCalculator, compare_scenarios, create_summary_table
import json

class ScenarioAnalyzer:
    """Класс для анализа различных сценариев проекта"""
    
    def __init__(self):
        self.results = compare_scenarios()
        self.summary_table = create_summary_table(self.results)
    
    def print_comparison_table(self):
        """Вывести сравнительную таблицу всех сценариев"""
        print("=== СРАВНИТЕЛЬНАЯ ТАБЛИЦА СЦЕНАРИЕВ ===")
        print(self.summary_table.to_string(index=False))
        print()
    
    def find_best_scenario(self, metric='roi_shiwa'):
        """Найти лучший сценарий по заданному показателю"""
        if metric == 'roi_shiwa':
            best_idx = self.summary_table['ROI SHIWA (%)'].astype(float).idxmax()
        elif metric == 'profit_shiwa':
            # Убираем запятые и конвертируем в float
            profits = self.summary_table['Прибыль SHIWA (USD)'].str.replace(',', '').astype(float)
            best_idx = profits.idxmax()
        elif metric == 'profit_etecsa':
            profits = self.summary_table['Прибыль ETECSA (USD)'].str.replace(',', '').astype(float)
            best_idx = profits.idxmax()
        else:
            best_idx = 0
        
        best_scenario = self.summary_table.iloc[best_idx]
        print(f"=== ЛУЧШИЙ СЦЕНАРИЙ ПО {metric.upper()} ===")
        print(f"Сценарий: {best_scenario['Сценарий']}")
        print(f"Вариант: {best_scenario['Вариант']}")
        print(f"ROI SHIWA: {best_scenario['ROI SHIWA (%)']}%")
        print(f"Прибыль SHIWA: {best_scenario['Прибыль SHIWA (USD)']}")
        print(f"Прибыль ETECSA: {best_scenario['Прибыль ETECSA (USD)']}")
        print()
        
        return best_scenario
    
    def analyze_sensitivity(self, parameter, values, scenario='baseline', variant='B'):
        """Анализ чувствительности к изменению параметра"""
        print(f"=== АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ: {parameter} ===")
        print(f"Сценарий: {scenario}, Вариант: {variant}")
        print()
        
        sensitivity_results = []
        
        for value in values:
            # Создаем временный калькулятор с измененным параметром
            calc = BusinessCalculator(scenario, variant)
            
            # Изменяем параметр (упрощенная версия)
            if parameter == 'monthly_fee':
                calc.scenario_params['monthly_fee'] = value
            elif parameter == 'hotels_count':
                calc.scenario_params['hotels_count'] = value
            elif parameter == 'equipment_cost':
                calc.equipment_prices['cost_price_usd'] = value
                calc.equipment_prices['selling_price_usd'] = value + calc.equipment_prices['intellectual_value_rub'] / calc.total_costs['project_fot_usd'] * calc.equipment_prices['cost_price_usd']
            
            summary = calc.generate_financial_summary()
            sensitivity_results.append({
                'value': value,
                'shiwa_profit': summary['shiwa']['net_profit'],
                'shiwa_roi': summary['shiwa']['roi'],
                'etecsa_profit': summary['etecsa']['net_profit']
            })
        
        # Создаем DataFrame для анализа
        df = pd.DataFrame(sensitivity_results)
        
        print("Результаты анализа чувствительности:")
        print(df.to_string(index=False))
        print()
        
        return df
    
    def create_what_if_scenarios(self):
        """Создать сценарии 'что если'"""
        what_if_scenarios = []
        
        # Сценарий 1: Увеличение количества отелей на 25%
        calc1 = BusinessCalculator('baseline', 'B')
        calc1.scenario_params['hotels_count'] = 62  # 50 * 1.25
        summary1 = calc1.generate_financial_summary()
        what_if_scenarios.append({
            'name': 'Увеличение отелей на 25%',
            'shiwa_profit': summary1['shiwa']['net_profit'],
            'shiwa_roi': summary1['shiwa']['roi'],
            'etecsa_profit': summary1['etecsa']['net_profit']
        })
        
        # Сценарий 2: Снижение абонентской платы на 20%
        calc2 = BusinessCalculator('baseline', 'B')
        calc2.scenario_params['monthly_fee'] = 400  # 500 * 0.8
        summary2 = calc2.generate_financial_summary()
        what_if_scenarios.append({
            'name': 'Снижение платы на 20%',
            'shiwa_profit': summary2['shiwa']['net_profit'],
            'shiwa_roi': summary2['shiwa']['roi'],
            'etecsa_profit': summary2['etecsa']['net_profit']
        })
        
        # Сценарий 3: Увеличение затрат на 30%
        calc3 = BusinessCalculator('baseline', 'B')
        calc3.total_costs['total_costs_usd'] *= 1.3
        summary3 = calc3.generate_financial_summary()
        what_if_scenarios.append({
            'name': 'Увеличение затрат на 30%',
            'shiwa_profit': summary3['shiwa']['net_profit'],
            'shiwa_roi': summary3['shiwa']['roi'],
            'etecsa_profit': summary3['etecsa']['net_profit']
        })
        
        # Сценарий 4: Комбинация: больше отелей, но меньше плата
        calc4 = BusinessCalculator('baseline', 'B')
        calc4.scenario_params['hotels_count'] = 75
        calc4.scenario_params['monthly_fee'] = 400
        summary4 = calc4.generate_financial_summary()
        what_if_scenarios.append({
            'name': '75 отелей по $400',
            'shiwa_profit': summary4['shiwa']['net_profit'],
            'shiwa_roi': summary4['shiwa']['roi'],
            'etecsa_profit': summary4['etecsa']['net_profit']
        })
        
        return what_if_scenarios
    
    def print_what_if_analysis(self):
        """Вывести анализ сценариев 'что если'"""
        scenarios = self.create_what_if_scenarios()
        
        print("=== АНАЛИЗ СЦЕНАРИЕВ 'ЧТО ЕСЛИ' ===")
        print()
        
        for scenario in scenarios:
            print(f"Сценарий: {scenario['name']}")
            print(f"  Прибыль SHIWA: ${scenario['shiwa_profit']:,.0f}")
            print(f"  ROI SHIWA: {scenario['shiwa_roi']:.1f}%")
            print(f"  Прибыль ETECSA: ${scenario['etecsa_profit']:,.0f}")
            print()
    
    def calculate_break_even_analysis(self):
        """Анализ точки безубыточности"""
        print("=== АНАЛИЗ ТОЧКИ БЕЗУБЫТОЧНОСТИ ===")
        print()
        
        # Для SHIWA NETWORK
        calc = BusinessCalculator('baseline', 'B')
        monthly_costs = calc.total_costs['total_costs_usd'] / 12
        monthly_revenue_per_hotel = 500 * 0.8  # 80% от абонентской платы
        
        breakeven_hotels = monthly_costs / monthly_revenue_per_hotel
        
        print(f"SHIWA NETWORK:")
        print(f"  Ежемесячные затраты: ${monthly_costs:,.0f}")
        print(f"  Доход с отеля в месяц: ${monthly_revenue_per_hotel}")
        print(f"  Точка безубыточности: {breakeven_hotels:.1f} отелей")
        print()
        
        # Для ETECSA
        etecsas_monthly_costs = ETECSA_OPERATIONAL_COSTS_USD / 12
        etecsas_monthly_revenue_per_hotel = 500 * 0.2  # 20% от абонентской платы
        
        etecsas_breakeven_hotels = etecsas_monthly_costs / etecsas_monthly_revenue_per_hotel
        
        print(f"ETECSA:")
        print(f"  Ежемесячные затраты: ${etecsas_monthly_costs:,.0f}")
        print(f"  Доход с отеля в месяц: ${etecsas_monthly_revenue_per_hotel}")
        print(f"  Точка безубыточности: {etecsas_breakeven_hotels:.1f} отелей")
        print()
        
        return {
            'shiwa_breakeven': breakeven_hotels,
            'etecsa_breakeven': etecsas_breakeven_hotels
        }
    
    def export_results_to_json(self, filename='scenario_analysis_results.json'):
        """Экспорт результатов в JSON файл"""
        export_data = {
            'summary_table': self.summary_table.to_dict('records'),
            'what_if_scenarios': self.create_what_if_scenarios(),
            'breakeven_analysis': self.calculate_break_even_analysis(),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"Результаты экспортированы в файл: {filename}")
    
    def run_full_analysis(self):
        """Запустить полный анализ всех сценариев"""
        print("=" * 60)
        print("ПОЛНЫЙ АНАЛИЗ БИЗНЕС-МОДЕЛИ ПРОЕКТА QUANTUM")
        print("=" * 60)
        print()
        
        # 1. Сравнительная таблица
        self.print_comparison_table()
        
        # 2. Лучшие сценарии
        print("=" * 40)
        self.find_best_scenario('roi_shiwa')
        self.find_best_scenario('profit_shiwa')
        
        # 3. Анализ "что если"
        print("=" * 40)
        self.print_what_if_analysis()
        
        # 4. Анализ точки безубыточности
        print("=" * 40)
        self.calculate_break_even_analysis()
        
        # 5. Экспорт результатов
        print("=" * 40)
        self.export_results_to_json()

# Функция для быстрого запуска анализа
def quick_scenario_analysis():
    """Быстрый анализ сценариев"""
    analyzer = ScenarioAnalyzer()
    analyzer.run_full_analysis()

if __name__ == "__main__":
    quick_scenario_analysis()
