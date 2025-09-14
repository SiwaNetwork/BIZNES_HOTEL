"""
Веб-интерфейс для бизнес-модели QUANTUM
Flask приложение с API для расчетов
"""

from flask import Flask, render_template, request, jsonify
from business_calculator import BusinessCalculator
from parameters import *
from parameters import RUB_TO_USD_RATE
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/scenarios')
def get_scenarios():
    """Получить список доступных сценариев"""
    scenarios = {
        'baseline': {
            'name': 'Базовый',
            'hotels_count': BASELINE_SCENARIO['hotels_count'],
            'monthly_fee': BASELINE_SCENARIO['monthly_fee'],
            'success_rate': BASELINE_SCENARIO['success_rate']
        },
        'optimistic': {
            'name': 'Оптимистичный',
            'hotels_count': OPTIMISTIC_SCENARIO['hotels_count'],
            'monthly_fee': OPTIMISTIC_SCENARIO['monthly_fee'],
            'success_rate': OPTIMISTIC_SCENARIO['success_rate']
        },
        'pessimistic': {
            'name': 'Пессимистичный',
            'hotels_count': PESSIMISTIC_SCENARIO['hotels_count'],
            'monthly_fee': PESSIMISTIC_SCENARIO['monthly_fee'],
            'success_rate': PESSIMISTIC_SCENARIO['success_rate']
        }
    }
    
    variants = {
        'A': {
            'name': 'Продажа оборудования + подписка',
            'description': 'Единоразовая продажа оборудования + ежемесячная подписка $20'
        },
        'B': {
            'name': 'Аренда оборудования (80/20)',
            'description': 'Разделение абонентской платы: SHIWA 80%, ETECSA 20%'
        }
    }
    
    return jsonify({
        'scenarios': scenarios,
        'variants': variants
    })

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Рассчитать бизнес-модель с заданными параметрами"""
    try:
        data = request.get_json()
        
        # Получаем параметры из запроса
        scenario = data.get('scenario', 'baseline')
        variant = data.get('variant', 'B')
        
        # Получаем параметры оборудования
        equipment_type = data.get('equipment_type', 'mini')
        assembly_option = data.get('assembly_option', 'shiwa_assembled')
        assembly_variant = data.get('assembly_variant', '80_20')
        
        # Создаем калькулятор
        calc = BusinessCalculator(scenario, variant, equipment_type, assembly_option, assembly_variant)
        
        # Применяем пользовательские параметры если есть
        if 'hotels_count' in data:
            calc.scenario_params['hotels_count'] = int(data['hotels_count'])
        if 'monthly_fee' in data:
            calc.scenario_params['monthly_fee'] = float(data['monthly_fee'])
        if 'equipment_cost' in data:
            # Обновляем базовую стоимость оборудования
            new_cost_usd = float(data['equipment_cost'])
            calc.equipment_prices['base_cost_usd'] = new_cost_usd
            calc.equipment_prices['base_cost_rub'] = new_cost_usd * RUB_TO_USD_RATE
        if 'exchange_rate' in data:
            rate = float(data['exchange_rate'])
            # Пересчитываем цены с новым курсом
            if 'base_cost_rub' in calc.equipment_prices:
                calc.equipment_prices['base_cost_usd'] = calc.equipment_prices['base_cost_rub'] / rate
            if 'adjusted_cost_rub' in calc.equipment_prices:
                calc.equipment_prices['adjusted_cost_usd'] = calc.equipment_prices['adjusted_cost_rub'] / rate
            if 'selling_price_rub' in calc.equipment_prices:
                calc.equipment_prices['selling_price_usd'] = calc.equipment_prices['selling_price_rub'] / rate
            if 'hotel_price_rub' in calc.equipment_prices:
                calc.equipment_prices['hotel_price_usd'] = calc.equipment_prices['hotel_price_rub'] / rate
        if 'equipment_type' in data:
            calc.equipment_type = data['equipment_type']
            calc.equipment_prices = calculate_equipment_prices(data['equipment_type'], calc.assembly_option)
        if 'assembly_option' in data:
            calc.assembly_option = data['assembly_option']
            calc.equipment_prices = calculate_equipment_prices(calc.equipment_type, data['assembly_option'])
        if 'assembly_variant' in data:
            calc.assembly_variant = data['assembly_variant']
            calc.local_assembly_params = get_local_assembly_variant(data['assembly_variant'])
        
        # Рассчитываем результаты
        summary = calc.generate_financial_summary()
        payback = calc.calculate_payback_period()
        
        # Формируем ответ
        result = {
            'success': True,
            'data': {
                'summary': summary,
                'payback': payback,
                'equipment_prices': calc.equipment_prices,
                'costs': calc.total_costs,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/compare', methods=['POST'])
def compare_scenarios():
    """Сравнить несколько сценариев"""
    try:
        data = request.get_json()
        scenarios_to_compare = data.get('scenarios', [])
        
        results = []
        
        for scenario_data in scenarios_to_compare:
            calc = BusinessCalculator(
                scenario_data.get('scenario', 'baseline'),
                scenario_data.get('variant', 'B')
            )
            
            summary = calc.generate_financial_summary()
            payback = calc.calculate_payback_period()
            
            results.append({
                'scenario': summary['scenario'],
                'variant': summary['variant'],
                'summary': summary,
                'payback': payback
            })
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/sensitivity', methods=['POST'])
def sensitivity_analysis():
    """Анализ чувствительности"""
    try:
        data = request.get_json()
        
        parameter = data.get('parameter')  # 'hotels_count', 'monthly_fee', etc.
        values = data.get('values', [])
        base_scenario = data.get('scenario', 'baseline')
        base_variant = data.get('variant', 'B')
        
        results = []
        
        for value in values:
            calc = BusinessCalculator(base_scenario, base_variant)
            
            # Применяем изменение параметра
            if parameter == 'hotels_count':
                calc.scenario_params['hotels_count'] = int(value)
            elif parameter == 'monthly_fee':
                calc.scenario_params['monthly_fee'] = float(value)
            elif parameter == 'equipment_cost':
                calc.equipment_prices['cost_price_usd'] = float(value)
            
            summary = calc.generate_financial_summary()
            
            results.append({
                'value': value,
                'shiwa_profit': summary['shiwa']['net_profit'],
                'shiwa_roi': summary['shiwa']['roi'],
                'etecsa_profit': summary['etecsa']['net_profit'],
                'total_revenue': summary['shiwa']['total_revenue']
            })
        
        return jsonify({
            'success': True,
            'data': {
                'parameter': parameter,
                'results': results
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/breakeven')
def breakeven_analysis():
    """Анализ точки безубыточности"""
    try:
        # Для SHIWA NETWORK
        calc = BusinessCalculator('baseline', 'B')
        monthly_costs = calc.total_costs['total_costs_usd'] / 12
        monthly_revenue_per_hotel = 500 * 0.8  # 80% от абонентской платы
        shiwa_breakeven = monthly_costs / monthly_revenue_per_hotel
        
        # Для ETECSA
        etecsas_monthly_costs = ETECSA_OPERATIONAL_COSTS_USD / 12
        etecsas_monthly_revenue_per_hotel = 500 * 0.2  # 20% от абонентской платы
        etecsas_breakeven = etecsas_monthly_costs / etecsas_monthly_revenue_per_hotel
        
        return jsonify({
            'success': True,
            'data': {
                'shiwa': {
                    'monthly_costs': monthly_costs,
                    'monthly_revenue_per_hotel': monthly_revenue_per_hotel,
                    'breakeven_hotels': shiwa_breakeven
                },
                'etecsa': {
                    'monthly_costs': etecsas_monthly_costs,
                    'monthly_revenue_per_hotel': etecsas_monthly_revenue_per_hotel,
                    'breakeven_hotels': etecsas_breakeven
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/analytics', methods=['POST'])
def get_analytics():
    """API для получения данных аналитики"""
    try:
        data = request.get_json()
        scenario = data.get('scenario', 'baseline')
        variant = data.get('variant', 'A')
        equipment_type = data.get('equipment_type', 'mini')
        assembly_option = data.get('assembly_option', 'shiwa_assembled')
        assembly_variant = data.get('assembly_variant', '80_20')
        
        calc = BusinessCalculator(scenario, variant, equipment_type, assembly_option, assembly_variant)
        summary = calc.generate_financial_summary()
        
        # Подготавливаем данные для аналитики
        analytics_data = {
            'summary': summary,
            'charts': {
                'revenue_comparison': {
                    'labels': ['SHIWA NETWORK', 'ETECSA'],
                    'data': [
                        summary['shiwa']['total_revenue'],
                        summary['etecsa']['equipment_profit'] + summary['etecsa']['subscription_revenue']
                    ]
                },
                'profit_comparison': {
                    'labels': ['SHIWA NETWORK', 'ETECSA'],
                    'data': [
                        summary['shiwa']['net_profit'],
                        summary['etecsa']['net_profit']
                    ]
                },
                'shiwa_revenue_breakdown': {
                    'labels': ['Доход от оборудования', 'Доход от подписки'],
                    'data': [
                        summary['shiwa']['equipment_revenue'],
                        summary['shiwa']['subscription_revenue']
                    ]
                },
                'etecsa_revenue_breakdown': {
                    'labels': ['Доход от оборудования', 'Доход от подписки'],
                    'data': [
                        summary['etecsa']['equipment_profit'],
                        summary['etecsa']['subscription_revenue']
                    ]
                },
                'hotel_benefits_breakdown': {
                    'labels': ['Экономия от биллинга', 'Экономия от эффективности', 'Экономия от простоя'],
                    'data': [
                        summary['hotels']['billing_savings'],
                        summary['hotels']['efficiency_savings'],
                        summary['hotels']['downtime_savings']
                    ]
                }
            },
            'metrics': {
                'total_project_value': summary['shiwa']['total_revenue'] + summary['etecsa']['equipment_profit'] + summary['etecsa']['subscription_revenue'],
                'shiwa_roi': summary['shiwa']['roi'],
                'etecsa_roi': (summary['etecsa']['net_profit'] / summary['etecsa']['operational_costs']) * 100 if summary['etecsa']['operational_costs'] > 0 else 0,
                'hotel_roi': summary['hotels']['roi'],
                'payback_period': calc.calculate_payback_period()
            }
        }
        
        return jsonify({
            'success': True,
            'data': analytics_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
