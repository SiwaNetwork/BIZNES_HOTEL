"""
Калькулятор бизнес-модели проекта QUANTUM
Основные функции для расчета финансовых показателей
"""

from parameters import *
import pandas as pd
from datetime import datetime, timedelta

class BusinessCalculator:
    """Класс для расчета бизнес-модели проекта"""
    
    def __init__(self, scenario='baseline', variant='B', equipment_type='mini', assembly_option='shiwa_assembled', assembly_variant='80_20'):
        """
        Инициализация калькулятора
        
        Args:
            scenario: сценарий развития ('baseline', 'optimistic', 'pessimistic')
            variant: модель монетизации ('A' или 'B')
            equipment_type: тип оборудования ('mini' или '1u_2u')
            assembly_option: вариант сборки ('shiwa_assembled', 'etecsa_assembly', 'mixed_approach')
            assembly_variant: вариант распределения доходов ('80_20' или '50_50')
        """
        self.scenario_params = get_scenario_params(scenario)
        self.variant_params = get_variant_params(variant)
        self.equipment_type = equipment_type
        self.assembly_option = assembly_option
        self.assembly_variant = assembly_variant
        self.equipment_prices = calculate_equipment_prices(equipment_type, assembly_option)
        self.total_costs = calculate_total_costs()
        self.local_assembly_params = get_local_assembly_variant(assembly_variant)
        
    def calculate_shiwa_revenue(self):
        """Рассчитать доходы SHIWA NETWORK"""
        hotels_count = self.scenario_params['hotels_count']
        success_rate = self.scenario_params['success_rate'] / 100
        effective_hotels = hotels_count * success_rate
        
        # Доход от продажи оборудования ETECSA
        equipment_revenue = effective_hotels * self.equipment_prices['selling_price_usd']
        
        # Доход от абонентской платы
        if self.variant_params['name'] == 'Продажа оборудования + подписка':
            # Вариант А: продажа + подписка (реалистичная модель)
            monthly_subscription = self.variant_params['monthly_subscription_shiwa']
            annual_subscription = effective_hotels * monthly_subscription * 12
            total_annual_revenue = equipment_revenue + annual_subscription
            
        else:
            # Вариант Б: аренда с настраиваемым разделением
            # Всегда используем выбранный вариант распределения
            shiwa_share = self.local_assembly_params['shiwa_share']
            
            monthly_fee = self.scenario_params['monthly_fee']
            annual_subscription = effective_hotels * monthly_fee * shiwa_share * 12
            total_annual_revenue = annual_subscription  # При аренде нет дохода от продажи оборудования
        
        return {
            'equipment_revenue': equipment_revenue,
            'subscription_revenue': annual_subscription,
            'total_revenue': total_annual_revenue,
            'effective_hotels': effective_hotels
        }
    
    def calculate_etecsa_revenue(self):
        """Рассчитать доходы ETECSA"""
        hotels_count = self.scenario_params['hotels_count']
        success_rate = self.scenario_params['success_rate'] / 100
        effective_hotels = hotels_count * success_rate
        
        if self.variant_params['name'] == 'Продажа оборудования + подписка':
            # Вариант А: доход от продажи оборудования отелям + абонентская плата
            # ETECSA продает оборудование с наценкой 50%
            markup = self.variant_params['etecsa_markup_percent'] / 100
            hotel_price = self.equipment_prices['selling_price_usd'] * (1 + markup)
            equipment_profit = effective_hotels * (hotel_price - self.equipment_prices['selling_price_usd'])
            
            # Доход от абонентской платы ETECSA
            monthly_etecsa_fee = self.variant_params['monthly_subscription_etecsa']
            subscription_revenue = effective_hotels * monthly_etecsa_fee * 12
            
            # Комиссия за сборку оборудования (если применимо)
            assembly_fee_revenue = effective_hotels * self.equipment_prices['assembly_fee_usd']
            
        else:
            # Вариант Б: доля от абонентской платы
            # Всегда используем выбранный вариант распределения
            etecsas_share = self.local_assembly_params['etecsa_share']
            
            monthly_fee = self.scenario_params['monthly_fee']
            subscription_revenue = effective_hotels * monthly_fee * etecsas_share * 12
            equipment_profit = 0
            assembly_fee_revenue = 0
        
        # Операционные затраты
        operational_costs = ETECSA_OPERATIONAL_COSTS_USD
        
        # Дополнительные затраты при локальной сборке
        if self.assembly_option == 'etecsa_assembly':
            operational_costs += LOCAL_ASSEMBLY_COSTS['monthly_support_cost_usd']
        
        # Применяем дополнительные затраты для пессимистичного сценария
        if self.scenario_params['name'] == 'Пессимистичный':
            operational_costs *= self.scenario_params.get('additional_costs', 1)
        
        # Общий доход ETECSA
        total_revenue = equipment_profit + subscription_revenue + assembly_fee_revenue
        
        # Чистая прибыль
        net_profit = total_revenue - operational_costs
        
        return {
            'equipment_profit': equipment_profit,
            'subscription_revenue': subscription_revenue,
            'assembly_fee_revenue': assembly_fee_revenue,
            'total_revenue': total_revenue,
            'operational_costs': operational_costs,
            'net_profit': net_profit,
            'effective_hotels': effective_hotels
        }
    
    def calculate_hotel_benefits(self):
        """Рассчитать выгоды для отелей"""
        hotels_count = self.scenario_params['hotels_count']
        success_rate = self.scenario_params['success_rate'] / 100
        effective_hotels = hotels_count * success_rate
        
        monthly_fee = self.scenario_params['monthly_fee']
        annual_cost = monthly_fee * 12
        
        # Более консервативная оценка выгод для отелей
        # Основные выгоды от синхронизации времени:
        # 1. Снижение ошибок в биллинге
        # 2. Повышение эффективности персонала
        # 3. Сокращение простоя IT-систем
        
        # Консервативная оценка экономии (в USD в год на отель)
        billing_savings = 1000  # Экономия от снижения ошибок в биллинге
        efficiency_savings = 5000  # Экономия от повышения эффективности персонала
        downtime_savings = 1200  # Экономия от сокращения простоя систем
        
        total_benefit = billing_savings + efficiency_savings + downtime_savings
        
        # ROI только если выгода превышает затраты
        if total_benefit > annual_cost:
            roi = (total_benefit - annual_cost) / annual_cost * 100
        else:
            roi = 0
        
        return {
            'annual_cost': annual_cost,
            'billing_savings': billing_savings,
            'efficiency_savings': efficiency_savings,
            'downtime_savings': downtime_savings,
            'total_benefit': total_benefit,
            'roi_percent': roi,
            'effective_hotels': effective_hotels
        }
    
    def calculate_shiwa_profitability(self):
        """Рассчитать прибыльность SHIWA NETWORK"""
        revenue = self.calculate_shiwa_revenue()
        
        # Базовые операционные затраты
        operational_costs = self.total_costs['total_costs_usd']
        
        # Для модели продажи добавляем затраты на оборудование
        equipment_costs = 0
        if self.variant_params['name'] == 'Продажа оборудования + подписка':
            equipment_costs = self.equipment_prices['adjusted_cost_usd'] * self.scenario_params['hotels_count']
        
        # Общие затраты
        costs = operational_costs + equipment_costs
        
        # Применяем дополнительные затраты для пессимистичного сценария
        if self.scenario_params['name'] == 'Пессимистичный':
            costs *= self.scenario_params.get('additional_costs', 1)
        
        net_profit = revenue['total_revenue'] - costs
        profit_margin = (net_profit / revenue['total_revenue']) * 100 if revenue['total_revenue'] > 0 else 0
        
        return {
            'total_revenue': revenue['total_revenue'],
            'total_costs': costs,
            'net_profit': net_profit,
            'profit_margin_percent': profit_margin,
            'roi_percent': (net_profit / costs) * 100 if costs > 0 else 0
        }
    
    def generate_financial_summary(self):
        """Сгенерировать финансовую сводку"""
        shiwa_revenue = self.calculate_shiwa_revenue()
        etecsas_revenue = self.calculate_etecsa_revenue()
        hotel_benefits = self.calculate_hotel_benefits()
        shiwa_profitability = self.calculate_shiwa_profitability()
        
        return {
            'scenario': self.scenario_params['name'],
            'variant': self.variant_params['name'],
            'equipment_type': self.equipment_type,
            'equipment_name': self.equipment_prices['equipment_name'],
            'assembly_option': self.assembly_option,
            'assembly_name': self.equipment_prices['assembly_name'],
            'assembly_variant': self.assembly_variant,
            'hotels_count': self.scenario_params['hotels_count'],
            'effective_hotels': shiwa_revenue['effective_hotels'],
            'shiwa': {
                'equipment_revenue': shiwa_revenue['equipment_revenue'],
                'subscription_revenue': shiwa_revenue['subscription_revenue'],
                'total_revenue': shiwa_revenue['total_revenue'],
                'total_costs': shiwa_profitability['total_costs'],
                'net_profit': shiwa_profitability['net_profit'],
                'profit_margin': shiwa_profitability['profit_margin_percent'],
                'roi': shiwa_profitability['roi_percent']
            },
            'etecsa': {
                'equipment_profit': etecsas_revenue['equipment_profit'],
                'subscription_revenue': etecsas_revenue['subscription_revenue'],
                'operational_costs': etecsas_revenue['operational_costs'],
                'net_profit': etecsas_revenue['net_profit']
            },
            'hotels': {
                'annual_cost': hotel_benefits['annual_cost'],
                'billing_savings': hotel_benefits['billing_savings'],
                'efficiency_savings': hotel_benefits['efficiency_savings'],
                'downtime_savings': hotel_benefits['downtime_savings'],
                'total_benefit': hotel_benefits['total_benefit'],
                'roi': hotel_benefits['roi_percent']
            }
        }
    
    def calculate_payback_period(self):
        """Рассчитать период окупаемости"""
        shiwa_profitability = self.calculate_shiwa_profitability()
        monthly_profit = shiwa_profitability['net_profit'] / 12
        
        if monthly_profit <= 0:
            return None
        
        # Время окупаемости в месяцах (на основе чистой прибыли)
        payback_months = shiwa_profitability['total_costs'] / monthly_profit
        
        return {
            'payback_months': payback_months,
            'payback_years': payback_months / 12,
            'monthly_profit': monthly_profit
        }

def compare_scenarios():
    """Сравнить все сценарии"""
    scenarios = ['baseline', 'optimistic', 'pessimistic']
    variants = ['A', 'B']
    
    results = []
    
    for scenario in scenarios:
        for variant in variants:
            calculator = BusinessCalculator(scenario, variant)
            summary = calculator.generate_financial_summary()
            results.append(summary)
    
    return results

def create_summary_table(results):
    """Создать сводную таблицу результатов"""
    data = []
    
    for result in results:
        data.append({
            'Сценарий': result['scenario'],
            'Вариант': result['variant'],
            'Отели (эффект.)': f"{result['effective_hotels']:.0f}",
            'Доход SHIWA (USD)': f"{result['shiwa']['total_revenue']:,.0f}",
            'Прибыль SHIWA (USD)': f"{result['shiwa']['net_profit']:,.0f}",
            'ROI SHIWA (%)': f"{result['shiwa']['roi']:.1f}",
            'Прибыль ETECSA (USD)': f"{result['etecsa']['net_profit']:,.0f}",
            'ROI отелей (%)': f"{result['hotels']['roi']:.0f}"
        })
    
    return pd.DataFrame(data)

# Функция для быстрого анализа
def quick_analysis(scenario='baseline', variant='B'):
    """Быстрый анализ для заданного сценария и варианта"""
    calculator = BusinessCalculator(scenario, variant)
    summary = calculator.generate_financial_summary()
    payback = calculator.calculate_payback_period()
    
    print(f"=== АНАЛИЗ ПРОЕКТА ===")
    print(f"Сценарий: {summary['scenario']}")
    print(f"Вариант: {summary['variant']}")
    print(f"Количество отелей: {summary['effective_hotels']:.0f}")
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

if __name__ == "__main__":
    # Пример использования
    quick_analysis('baseline', 'B')
