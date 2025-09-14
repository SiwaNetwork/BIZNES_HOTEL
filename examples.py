"""
Примеры использования бизнес-модели QUANTUM
Демонстрация различных способов анализа и изменения параметров
"""

from business_calculator import BusinessCalculator, quick_analysis
from scenario_analyzer import ScenarioAnalyzer, quick_scenario_analysis
from interactive_analyzer import InteractiveAnalyzer

def example_1_basic_analysis():
    """Пример 1: Базовый анализ проекта"""
    print("=" * 60)
    print("ПРИМЕР 1: БАЗОВЫЙ АНАЛИЗ ПРОЕКТА")
    print("=" * 60)
    
    # Создаем калькулятор для базового сценария, вариант Б
    calc = BusinessCalculator('baseline', 'B')
    
    # Получаем финансовую сводку
    summary = calc.generate_financial_summary()
    
    print(f"Сценарий: {summary['scenario']}")
    print(f"Вариант: {summary['variant']}")
    print(f"Количество отелей: {summary['effective_hotels']:.0f}")
    print()
    
    print("Результаты для SHIWA NETWORK:")
    print(f"  Доход от оборудования: ${summary['shiwa']['equipment_revenue']:,.0f}")
    print(f"  Доход от подписки: ${summary['shiwa']['subscription_revenue']:,.0f}")
    print(f"  Общий доход: ${summary['shiwa']['total_revenue']:,.0f}")
    print(f"  Общие затраты: ${summary['shiwa']['total_costs']:,.0f}")
    print(f"  Чистая прибыль: ${summary['shiwa']['net_profit']:,.0f}")
    print(f"  ROI: {summary['shiwa']['roi']:.1f}%")
    print()
    
    print("Результаты для ETECSA:")
    print(f"  Чистая прибыль: ${summary['etecsa']['net_profit']:,.0f}")
    print()
    
    print("Результаты для отелей:")
    print(f"  Годовые затраты: ${summary['hotels']['annual_cost']:,.0f}")
    print(f"  Годовая выгода: ${summary['hotels']['total_benefit']:,.0f}")
    print(f"  ROI: {summary['hotels']['roi']:.0f}%")
    print()

def example_2_scenario_comparison():
    """Пример 2: Сравнение сценариев"""
    print("=" * 60)
    print("ПРИМЕР 2: СРАВНЕНИЕ СЦЕНАРИЕВ")
    print("=" * 60)
    
    # Создаем анализатор сценариев
    analyzer = ScenarioAnalyzer()
    
    # Показываем сравнительную таблицу
    analyzer.print_comparison_table()
    
    # Находим лучший сценарий по ROI
    analyzer.find_best_scenario('roi_shiwa')

def example_3_sensitivity_analysis():
    """Пример 3: Анализ чувствительности"""
    print("=" * 60)
    print("ПРИМЕР 3: АНАЛИЗ ЧУВСТВИТЕЛЬНОСТИ")
    print("=" * 60)
    
    analyzer = ScenarioAnalyzer()
    
    # Анализ чувствительности к изменению абонентской платы
    fee_values = [300, 400, 500, 600, 700]
    print("Анализ чувствительности к абонентской плате:")
    fee_sensitivity = analyzer.analyze_sensitivity('monthly_fee', fee_values)
    
    print("\n" + "="*40)
    
    # Анализ чувствительности к количеству отелей
    hotels_values = [25, 35, 50, 65, 75]
    print("Анализ чувствительности к количеству отелей:")
    hotels_sensitivity = analyzer.analyze_sensitivity('hotels_count', hotels_values)

def example_4_what_if_scenarios():
    """Пример 4: Сценарии 'что если'"""
    print("=" * 60)
    print("ПРИМЕР 4: СЦЕНАРИИ 'ЧТО ЕСЛИ'")
    print("=" * 60)
    
    analyzer = ScenarioAnalyzer()
    analyzer.print_what_if_analysis()

def example_5_breakeven_analysis():
    """Пример 5: Анализ точки безубыточности"""
    print("=" * 60)
    print("ПРИМЕР 5: АНАЛИЗ ТОЧКИ БЕЗУБЫТОЧНОСТИ")
    print("=" * 60)
    
    analyzer = ScenarioAnalyzer()
    breakeven_results = analyzer.calculate_break_even_analysis()
    
    print(f"SHIWA NETWORK достигнет безубыточности при {breakeven_results['shiwa_breakeven']:.1f} отелях")
    print(f"ETECSA достигнет безубыточности при {breakeven_results['etecsa_breakeven']:.1f} отелях")

def example_6_custom_parameters():
    """Пример 6: Работа с пользовательскими параметрами"""
    print("=" * 60)
    print("ПРИМЕР 6: ПОЛЬЗОВАТЕЛЬСКИЕ ПАРАМЕТРЫ")
    print("=" * 60)
    
    # Создаем интерактивный анализатор
    analyzer = InteractiveAnalyzer()
    
    # Изменяем параметры
    analyzer.change_hotels_count(75)  # Увеличиваем количество отелей
    analyzer.change_monthly_fee(450)  # Снижаем абонентскую плату
    analyzer.change_variant('A')      # Меняем на вариант А
    
    print("Измененные параметры:")
    analyzer.show_current_parameters()
    
    print("\nАнализ с новыми параметрами:")
    analyzer.run_analysis_with_custom_params()

def example_7_payback_analysis():
    """Пример 7: Анализ окупаемости"""
    print("=" * 60)
    print("ПРИМЕР 7: АНАЛИЗ ОКУПАЕМОСТИ")
    print("=" * 60)
    
    scenarios = ['baseline', 'optimistic', 'pessimistic']
    variants = ['A', 'B']
    
    for scenario in scenarios:
        for variant in variants:
            calc = BusinessCalculator(scenario, variant)
            payback = calc.calculate_payback_period()
            
            if payback:
                print(f"{scenario} + {variant}: Окупаемость {payback['payback_months']:.1f} месяцев")
            else:
                print(f"{scenario} + {variant}: Окупаемость не достигнута")

def example_8_export_analysis():
    """Пример 8: Экспорт результатов анализа"""
    print("=" * 60)
    print("ПРИМЕР 8: ЭКСПОРТ РЕЗУЛЬТАТОВ")
    print("=" * 60)
    
    analyzer = ScenarioAnalyzer()
    
    # Экспортируем результаты в JSON
    analyzer.export_results_to_json('project_analysis_results.json')
    
    print("Результаты анализа экспортированы в файл 'project_analysis_results.json'")

def example_9_quick_analysis():
    """Пример 9: Быстрый анализ"""
    print("=" * 60)
    print("ПРИМЕР 9: БЫСТРЫЙ АНАЛИЗ")
    print("=" * 60)
    
    # Быстрый анализ базового сценария
    print("Базовый сценарий, вариант B:")
    quick_analysis('baseline', 'B')
    
    print("\n" + "="*40)
    
    # Быстрый анализ оптимистичного сценария
    print("Оптимистичный сценарий, вариант B:")
    quick_analysis('optimistic', 'B')

def run_all_examples():
    """Запустить все примеры"""
    examples = [
        example_1_basic_analysis,
        example_2_scenario_comparison,
        example_3_sensitivity_analysis,
        example_4_what_if_scenarios,
        example_5_breakeven_analysis,
        example_6_custom_parameters,
        example_7_payback_analysis,
        example_8_export_analysis,
        example_9_quick_analysis
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
            print("\n" + "="*80 + "\n")
        except Exception as e:
            print(f"Ошибка в примере {i}: {e}")
            print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ БИЗНЕС-МОДЕЛИ QUANTUM")
    print("=" * 80)
    print()
    
    # Запускаем все примеры
    run_all_examples()
    
    print("Все примеры выполнены!")
    print()
    print("Для интерактивного анализа используйте:")
    print("python interactive_analyzer.py")
    print()
    print("Для полного анализа сценариев используйте:")
    print("python scenario_analyzer.py")
