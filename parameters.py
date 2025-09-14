"""
Параметры бизнес-модели проекта QUANTUM для отелей Кубы
Все основные параметры проекта собраны в одном месте для удобного изменения
"""

# =============================================================================
# ОСНОВНЫЕ ПАРАМЕТРЫ ПРОЕКТА
# =============================================================================

# Количество отелей в проекте
HOTELS_COUNT = 50

# Абонентская плата в месяц (USD) - общая для отеля
MONTHLY_FEE_USD = 500

# Подписка SHIWA за ПО и поддержку (USD/месяц на отель)
SHIWA_SUBSCRIPTION_USD = 20

# Абонентская плата ETECSA за услуги связи и ТО (USD/месяц на отель)  
ETECSA_SUBSCRIPTION_USD = 480

# Курс рубль к доллару
RUB_TO_USD_RATE = 78

# =============================================================================
# ПАРАМЕТРЫ ОБОРУДОВАНИЯ
# =============================================================================

# Добавленная стоимость (интеллектуальный софт + лицензия) (рубли)
# Для реалистичной модели: SHIWA продает комплектующие + лицензию
INTELLECTUAL_VALUE_RUB = 50000

# Типы оборудования и их характеристики
EQUIPMENT_TYPES = {
    'mini': {
        'name': 'Quantum GrandMaster Mini',
        'description': 'Термостатированный кварц',
        'cost_rub': 90000,  # Себестоимость производства
        'complexity_factor': 1.0,  # Коэффициент сложности для сборки
        'local_assembly_reduction': 0.15  # Снижение затрат при локальной сборке (15%)
    },
    '1u_2u': {
        'name': 'Quantum GrandMaster 1U/2U',
        'description': 'Рубидиевый/цезиевый генератор',
        'cost_rub': 350000,  # Себестоимость производства (более дорогой)
        'complexity_factor': 1.5,  # Коэффициент сложности для сборки
        'local_assembly_reduction': 0.20  # Снижение затрат при локальной сборке (20%)
    }
}

# Тип оборудования по умолчанию
DEFAULT_EQUIPMENT_TYPE = 'mini'

# Варианты сборки оборудования
ASSEMBLY_OPTIONS = {
    'shiwa_assembled': {
        'name': 'Готовое оборудование от SHIWA',
        'description': 'SHIWA собирает и поставляет готовое оборудование',
        'cost_multiplier': 1.0,  # Базовая себестоимость
        'shiwa_profit_margin': 0.3,  # Маржа SHIWA 30%
        'delivery_time': '2-3 недели'
    },
    'etecsa_assembly': {
        'name': 'Сборка ETECSA из комплектующих',
        'description': 'SHIWA поставляет комплектующие, ETECSA собирает оборудование',
        'cost_multiplier': 0.85,  # Снижение себестоимости на 15%
        'shiwa_profit_margin': 0.2,  # Меньшая маржа SHIWA 20%
        'etecsa_assembly_fee': 0.1,  # Комиссия ETECSA за сборку 10%
        'delivery_time': '1-2 недели'
    },
    'mixed_approach': {
        'name': 'Смешанный подход',
        'description': 'Часть оборудования готовая, часть собирается на месте',
        'cost_multiplier': 0.9,  # Средняя себестоимость
        'shiwa_profit_margin': 0.25,  # Средняя маржа SHIWA 25%
        'delivery_time': '1-3 недели'
    }
}

# Варианты распределения доходов при локальной сборке
LOCAL_ASSEMBLY_VARIANTS = {
    '80_20': {
        'name': 'Стандартный (80/20)',
        'shiwa_share': 0.8,  # 80% SHIWA
        'etecsa_share': 0.2,  # 20% ETECSA
        'description': 'SHIWA получает 80% от абонентской платы, ETECSA - 20%'
    },
    '50_50': {
        'name': 'Равное распределение (50/50)',
        'shiwa_share': 0.5,  # 50% SHIWA
        'etecsa_share': 0.5,  # 50% ETECSA
        'description': 'Равное распределение доходов между SHIWA и ETECSA'
    }
}

# Варианты по умолчанию
DEFAULT_ASSEMBLY_OPTION = 'shiwa_assembled'
DEFAULT_LOCAL_ASSEMBLY_VARIANT = '80_20'

# Наценка ETECSA при продаже отелям (%)
ETECSA_MARKUP_PERCENT = 39

# Дополнительные затраты на локальную сборку
LOCAL_ASSEMBLY_COSTS = {
    'training_cost_usd': 50000,  # Затраты на обучение персонала
    'setup_cost_usd': 30000,     # Затраты на подготовку производства
    'monthly_support_cost_usd': 5000  # Ежемесячная поддержка производства
}

# =============================================================================
# МОДЕЛИ МОНЕТИЗАЦИИ
# =============================================================================

# Вариант А: Продажа оборудования + подписка (РЕАЛИСТИЧНАЯ МОДЕЛЬ)
VARIANT_A = {
    'name': 'Продажа оборудования + подписка',
    'equipment_purchase': True,
    'monthly_subscription_shiwa': SHIWA_SUBSCRIPTION_USD,  # $20 в месяц на отель
    'monthly_subscription_etecsa': ETECSA_SUBSCRIPTION_USD,  # $480 в месяц на отель
    'equipment_payment_type': 'one_time',
    'etecsa_markup_percent': 30  # Наценка ETECSA при продаже отелям
}

# Вариант Б: Аренда оборудования с разделением абонентской платы
VARIANT_B = {
    'name': 'Аренда оборудования (80/20)',
    'equipment_purchase': False,
    'shiwa_share_percent': 80,  # Доля SHIWA от абонентской платы
    'etecsa_share_percent': 20,  # Доля ETECSA от абонентской платы
    'equipment_payment_type': 'rental'
}

# =============================================================================
# РАСХОДЫ SHIWA NETWORK
# =============================================================================

# Оптимизированные затраты SHIWA NETWORK (на основе реальных расчетов)
# ФОТ (только ключевые сотрудники для поддержки и контроля качества)
PROJECT_FOT_RUB = 3000000  # ~$38,462

# Офисные и операционные расходы (минимум)
OFFICE_EXPENSES_RUB = 500000  # ~$6,410

# Командировки (1-2 поездки)
BUSINESS_TRIPS_RUB = 500000  # ~$6,410

# Доставка комплектующих (рубли в год)
DELIVERY_EXPENSES_RUB = 150000  # ~$1,923

# =============================================================================
# РАСХОДЫ ETECSA
# =============================================================================

# Операционные затраты ETECSA (USD в год) - на основе реальных расчетов
ETECSA_OPERATIONAL_COSTS_USD = 40000  # Установка + поддержка + админ расходы

# =============================================================================
# ВЫГОДЫ ДЛЯ ОТЕЛЕЙ
# =============================================================================

# Улучшения в выручке (%)
REVENUE_IMPROVEMENTS = {
    'service_level': 36.5,  # Повышение уровня сервиса
    'checkout_optimization': 152.0,  # Оптимизация времени выезда
}

# Улучшения в прибыли (%)
PROFIT_IMPROVEMENTS = {
    'financial_operations': 30.0,  # Улучшение финансовых операций
    'operational_efficiency': 35.0,  # Повышение операционной эффективности
    'security': 15.0,  # Повышение безопасности
}

# =============================================================================
# СЦЕНАРИИ РАЗВИТИЯ
# =============================================================================

# Базовый сценарий
BASELINE_SCENARIO = {
    'name': 'Базовый',
    'hotels_count': HOTELS_COUNT,
    'monthly_fee': MONTHLY_FEE_USD,
    'success_rate': 100,  # % успешного внедрения
}

# Оптимистичный сценарий
OPTIMISTIC_SCENARIO = {
    'name': 'Оптимистичный',
    'hotels_count': 75,
    'monthly_fee': MONTHLY_FEE_USD,
    'success_rate': 95,
    'additional_benefits': 1.2,  # 20% дополнительных выгод
}

# Пессимистичный сценарий
PESSIMISTIC_SCENARIO = {
    'name': 'Пессимистичный',
    'hotels_count': 30,
    'monthly_fee': MONTHLY_FEE_USD * 0.8,  # 20% снижение цены
    'success_rate': 80,
    'additional_costs': 1.3,  # 30% дополнительных затрат
}

# =============================================================================
# ПАРАМЕТРЫ ЛОКАЛЬНОЙ СБОРКИ
# =============================================================================

# Снижение себестоимости при локальной сборке (%)
LOCAL_ASSEMBLY_COST_REDUCTION = 15

# Дополнительные затраты на обучение персонала (USD)
TRAINING_COSTS_USD = 50000

# Затраты на подготовку производственных площадей (USD)
PRODUCTION_SETUP_COSTS_USD = 30000

# =============================================================================
# ВРЕМЕННЫЕ ПАРАМЕТРЫ
# =============================================================================

# Период расчета (месяцы)
CALCULATION_PERIOD_MONTHS = 12

# Период окупаемости (месяцы)
PAYBACK_PERIOD_MONTHS = 6

# =============================================================================
# ФУНКЦИИ ДЛЯ РАСЧЕТА
# =============================================================================

def get_scenario_params(scenario_name):
    """Получить параметры сценария по имени"""
    scenarios = {
        'baseline': BASELINE_SCENARIO,
        'optimistic': OPTIMISTIC_SCENARIO,
        'pessimistic': PESSIMISTIC_SCENARIO
    }
    return scenarios.get(scenario_name, BASELINE_SCENARIO)

def get_variant_params(variant_name):
    """Получить параметры модели монетизации по имени"""
    variants = {
        'A': VARIANT_A,
        'B': VARIANT_B
    }
    return variants.get(variant_name, VARIANT_B)

def calculate_equipment_prices(equipment_type=DEFAULT_EQUIPMENT_TYPE, assembly_option=DEFAULT_ASSEMBLY_OPTION):
    """Рассчитать цены оборудования с учетом типа и варианта сборки"""
    eq_type = EQUIPMENT_TYPES.get(equipment_type, EQUIPMENT_TYPES[DEFAULT_EQUIPMENT_TYPE])
    assembly = ASSEMBLY_OPTIONS.get(assembly_option, ASSEMBLY_OPTIONS[DEFAULT_ASSEMBLY_OPTION])
    
    # Базовая себестоимость
    base_cost_rub = eq_type['cost_rub']
    
    # Применяем множитель себестоимости в зависимости от варианта сборки
    adjusted_cost_rub = base_cost_rub * assembly['cost_multiplier']
    
    # Добавленная стоимость (интеллектуальная собственность)
    intellectual_value_rub = INTELLECTUAL_VALUE_RUB
    
    # Общая себестоимость для SHIWA
    total_cost_rub = adjusted_cost_rub + intellectual_value_rub
    
    # Цена продажи SHIWA → ETECSA (с учетом маржи SHIWA)
    shiwa_margin = assembly['shiwa_profit_margin']
    selling_price_rub = total_cost_rub * (1 + shiwa_margin)
    
    # Цена продажи отелям (с наценкой ETECSA)
    hotel_price_rub = selling_price_rub * (1 + ETECSA_MARKUP_PERCENT / 100)
    
    # Комиссия ETECSA за сборку (если применимо)
    assembly_fee_rub = 0
    if 'etecsa_assembly_fee' in assembly:
        assembly_fee_rub = total_cost_rub * assembly['etecsa_assembly_fee']
    
    return {
        'equipment_type': equipment_type,
        'equipment_name': eq_type['name'],
        'equipment_description': eq_type['description'],
        'assembly_option': assembly_option,
        'assembly_name': assembly['name'],
        'base_cost_rub': base_cost_rub,
        'adjusted_cost_rub': adjusted_cost_rub,
        'intellectual_value_rub': intellectual_value_rub,
        'total_cost_rub': total_cost_rub,
        'selling_price_rub': selling_price_rub,
        'hotel_price_rub': hotel_price_rub,
        'assembly_fee_rub': assembly_fee_rub,
        'base_cost_usd': base_cost_rub / RUB_TO_USD_RATE,
        'adjusted_cost_usd': adjusted_cost_rub / RUB_TO_USD_RATE,
        'total_cost_usd': total_cost_rub / RUB_TO_USD_RATE,
        'selling_price_usd': selling_price_rub / RUB_TO_USD_RATE,
        'hotel_price_usd': hotel_price_rub / RUB_TO_USD_RATE,
        'assembly_fee_usd': assembly_fee_rub / RUB_TO_USD_RATE,
        'shiwa_margin': shiwa_margin,
        'delivery_time': assembly['delivery_time'],
        'complexity_factor': eq_type['complexity_factor']
    }

def get_local_assembly_variant(variant_key=DEFAULT_LOCAL_ASSEMBLY_VARIANT):
    """Получить параметры варианта локальной сборки"""
    return LOCAL_ASSEMBLY_VARIANTS.get(variant_key, LOCAL_ASSEMBLY_VARIANTS[DEFAULT_LOCAL_ASSEMBLY_VARIANT])

def get_equipment_type_info(equipment_type=DEFAULT_EQUIPMENT_TYPE):
    """Получить информацию о типе оборудования"""
    return EQUIPMENT_TYPES.get(equipment_type, EQUIPMENT_TYPES[DEFAULT_EQUIPMENT_TYPE])

def get_assembly_option_info(assembly_option=DEFAULT_ASSEMBLY_OPTION):
    """Получить информацию о варианте сборки"""
    return ASSEMBLY_OPTIONS.get(assembly_option, ASSEMBLY_OPTIONS[DEFAULT_ASSEMBLY_OPTION])

def calculate_total_costs():
    """Рассчитать общие затраты SHIWA NETWORK"""
    return {
        'project_fot_usd': PROJECT_FOT_RUB / RUB_TO_USD_RATE,
        'office_expenses_usd': OFFICE_EXPENSES_RUB / RUB_TO_USD_RATE,
        'business_trips_usd': BUSINESS_TRIPS_RUB / RUB_TO_USD_RATE,
        'delivery_expenses_usd': DELIVERY_EXPENSES_RUB / RUB_TO_USD_RATE,
        'total_costs_usd': (PROJECT_FOT_RUB + OFFICE_EXPENSES_RUB + 
                           BUSINESS_TRIPS_RUB + DELIVERY_EXPENSES_RUB) / RUB_TO_USD_RATE
    }
