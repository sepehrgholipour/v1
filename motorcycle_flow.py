"""Step-by-step question flow for بیمه شخص ثالث موتورسیکلت.

The motorcycle journey mirrors the reference site: it starts from the bike
itself instead of the plate, so there is no پلاک or کد ملی step and no
brand/model catalog. The user answers one question per screen - مدل موتورسیکلت,
سال تولید, سابقه بیمه, تخفیف عدم خسارت and تعهد مالی - and only the steps that
apply to the given answers are shown.
"""

SESSION_KEY = 'motorcycle_quote'

TITLE = 'بیمه شخص ثالث موتورسیکلت'

HAD_PREVIOUS_POLICY = 'دارم'
NO_PREVIOUS_POLICY = 'ندارم'
ZERO_KILOMETER = 'صفر کیلومتر'
PLATE_CHANGED = 'بله'
PLATE_UNCHANGED = 'خیر'
DAMAGE_TAKEN = 'بله'
NO_DAMAGE = 'خیر'

MOTORCYCLE_MODELS = [
    {'value': 'برقی', 'icon': '🛵', 'title': 'برقی', 'note': 'موتورسیکلت برقی'},
    {'value': 'تک سیلندر', 'icon': '🏍️', 'title': 'تک سیلندر', 'note': 'پرفروش‌ترین گروه بازار'},
    {'value': 'دو سیلندر و بیش از دو سیلندر', 'icon': '🏍️', 'title': 'دو سیلندر و بیش از دو سیلندر', 'note': 'موتورهای پرقدرت'},
    {'value': 'سه چرخ', 'icon': '🛺', 'title': 'سه چرخ', 'note': 'سه چرخ یا سایدکار'},
]

PRODUCTION_YEARS = [
    {'value': str(year), 'label': f'{year + 621} - {year}'}
    for year in range(1405, 1363, -1)
]

POLICY_STATUS_OPTIONS = [
    {'value': HAD_PREVIOUS_POLICY, 'icon': '📄', 'title': 'بله بیمه داشته است.', 'note': 'تمدید یا انتقال بیمه‌نامه'},
    {'value': NO_PREVIOUS_POLICY, 'icon': '✨', 'title': 'خیر بیمه نداشته است.', 'note': 'اولین بیمه‌نامه موتورسیکلت'},
    {'value': ZERO_KILOMETER, 'icon': '🛵', 'title': 'موتورسیکلت صفر کیلومتر است.', 'note': 'بیمه‌نامه قبلی ندارد'},
]

PREVIOUS_COMPANIES = [
    'ایران', 'آسیا', 'البرز', 'پارسیان', 'دانا', 'سرمد', 'آرمان', 'آسماری', 'امید',
    'تجارت نو', 'تعاون', 'حافظ', 'حکمت صبا', 'خاورمیانه', 'دی', 'رازی', 'سامان',
    'سینا', 'ما', 'معلم', 'ملت', 'میهن', 'نوین', 'هوشمند فردا', 'پاسارگاد', 'پردیس',
    'کارآفرین', 'کوثر',
]

POLICY_START_DATES = [
    'کمتر از ۳۰ روز گذشته',
    'بین ۱ ماه تا ۱ سال گذشته',
    'بیش از ۱ سال گذشته',
]

POLICY_END_DATES = ['منقضی شده', 'تا ۳۰ روز آینده', 'بیش از ۳۰ روز']

PLATE_CHANGE_OPTIONS = [
    {'value': PLATE_CHANGED, 'icon': '🔄', 'title': 'بله تعویض پلاک داشته است.', 'note': 'تخفیف روی پلاک دیگری است'},
    {'value': PLATE_UNCHANGED, 'icon': '🏍️', 'title': 'خیر تعویض پلاک نداشته است.', 'note': 'همان پلاک بیمه‌نامه قبلی'},
]

DISCOUNT_SOURCES = [
    {'value': 'بدون انتقال تخفیف دیگر', 'icon': '🚫', 'title': 'تخفیف ثالث دیگری ندارم', 'note': 'سابقه تخفیف دیگری ندارم'},
    {'value': 'با همین پلاک', 'icon': '🛵', 'title': 'با همین پلاک تخفیف دارم', 'note': 'تخفیف روی همین پلاک ثبت است'},
    {'value': 'با پلاک دیگر', 'icon': '🔄', 'title': 'تخفیف با پلاک دیگری دارم', 'note': 'با پلاک دیگری انتقال می‌یابد'},
]

PERSIAN_DIGITS = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')

DISCOUNT_FACTORS = ['بدون تخفیف'] + [f'{percent}٪'.translate(PERSIAN_DIGITS) for percent in range(5, 71, 5)]

DAMAGE_COUNTS = ['بدون خسارت', 'یک', 'دو', 'سه یا بیشتر']

DAMAGE_ANSWER_OPTIONS = [
    {'value': NO_DAMAGE, 'icon': '🛡️', 'title': 'خیر دریافت نکرده‌ام.', 'note': 'تخفیف عدم خسارت شما حفظ می‌شود'},
    {'value': DAMAGE_TAKEN, 'icon': '🧾', 'title': 'بله دریافت کرده‌ام.', 'note': 'تعداد خسارت‌ها را وارد می‌کنم'},
]

FINANCIAL_COVERAGES = [
    '۷۰ میلیون تومان', '۲۴۰ میلیون تومان', '۷۲۰ میلیون تومان',
    '۱٫۲ میلیارد تومان', '۲٫۵ میلیارد تومان', '۳ میلیارد تومان',
    '۱۴ میلیارد تومان',
]

POLICY_TERMS = ['یک‌ساله', '۹ ماهه', '۶ ماهه', '۴ ماهه', '۳ ماهه', '۲ ماهه']

# Each step declares the answers it collects. ``values`` restricts a field to a
# known option list; ``None`` means free text. ``required_when`` makes a field
# mandatory only when another answer matches.
STEPS = {
    'model': {
        'label': 'مدل موتورسیکلت',
        'title': 'مدل موتورسیکلت را انتخاب کنید',
        'description': 'نوع موتورسیکلت نرخ پایه بیمه را مشخص می‌کند.',
        'fields': {'model': [option['value'] for option in MOTORCYCLE_MODELS]},
    },
    'year': {
        'label': 'سال تولید',
        'title': 'سال تولید موتورسیکلت',
        'description': 'سال ساخت موتورسیکلت را انتخاب کنید.',
        'fields': {'year': [year['value'] for year in PRODUCTION_YEARS]},
    },
    'policy_status': {
        'label': 'سابقه بیمه',
        'title': 'آیا این موتورسیکلت تاکنون بیمه شخص ثالث داشته است؟',
        'description': 'سابقه بیمه برای محاسبه تخفیف عدم خسارت لازم است.',
        'fields': {'policy_status': [HAD_PREVIOUS_POLICY, NO_PREVIOUS_POLICY]},
    },
    'previous_policy': {
        'label': 'بیمه‌نامه قبلی',
        'title': 'اطلاعات بیمه‌نامه قبلی',
        'description': 'شرکت بیمه‌گر و تاریخ بیمه‌نامه قبلی را وارد کنید.',
        'fields': {
            'previous_company': PREVIOUS_COMPANIES,
            'policy_start_date': None,
            'policy_end_date': None,
        },
    },
    'plate_change': {
        'label': 'تعویض پلاک',
        'title': 'آیا این موتورسیکلت در مدت بیمه‌نامه قبلی تعویض پلاک داشته است؟',
        'description': 'وضعیت پلاک مشخص می‌کند تخفیف از کدام پلاک منتقل می‌شود.',
        'fields': {'plate_changed': [PLATE_CHANGED, PLATE_UNCHANGED]},
    },
    'discount_source': {
        'label': 'تخفیف روی پلاک',
        'title': 'وضعیت تخفیف روی پلاک',
        'description': 'تخفیف عدم خسارت روی کدام پلاک ثبت شده است؟',
        'fields': {'discount_source': [option['value'] for option in DISCOUNT_SOURCES]},
    },
    'discount': {
        'label': 'تخفیف خسارت',
        'title': 'تخفیف عدم خسارت و خسارت بیمه‌نامه قبلی',
        'description': 'درصد تخفیف را دقیقاً مطابق بیمه‌نامه قبلی وارد کنید.',
        'fields': {
            'third_party_discount': DISCOUNT_FACTORS,
            'driver_discount': DISCOUNT_FACTORS,
            'has_damage': [NO_DAMAGE, DAMAGE_TAKEN],
            'property_damage_count': DAMAGE_COUNTS,
            'life_damage_count': DAMAGE_COUNTS,
            'driver_damage_count': DAMAGE_COUNTS,
        },
        'required_when': {
            'property_damage_count': ('has_damage', DAMAGE_TAKEN),
            'life_damage_count': ('has_damage', DAMAGE_TAKEN),
            'driver_damage_count': ('has_damage', DAMAGE_TAKEN),
        },
    },
    'coverage': {
        'label': 'تعهد مالی',
        'title': 'تعهد مالی و مدت بیمه‌نامه',
        'description': 'سقف تعهد مالی و مدت اعتبار بیمه‌نامه را انتخاب کنید.',
        'fields': {
            'financial_coverage': FINANCIAL_COVERAGES,
            'policy_term': POLICY_TERMS,
        },
    },
    'contact': {
        'label': 'اطلاعات تماس',
        'title': 'اطلاعات تماس',
        'description': 'نرخ بیمه‌های شرکت‌های مختلف برایتان پیامک می‌شود.',
        'fields': {
            'full_name': None,
            'national_code': None,
            'mobile': None,
        },
        'optional': ['national_code'],
    },
}

STEP_ORDER = [
    'model', 'year', 'policy_status', 'previous_policy', 'plate_change',
    'discount_source', 'discount', 'coverage', 'contact',
]

RESULT_STEP = 'result'


def url_name(step):
    return 'motorcycle_result' if step == RESULT_STEP else f'motorcycle_{step}'


def next_step(answers, step):
    """The step that follows ``step``, or ``result`` when the flow is done."""
    if step == 'policy_status':
        return 'previous_policy' if answers.get('policy_status') == HAD_PREVIOUS_POLICY else 'coverage'
    if step == 'plate_change':
        return 'discount_source' if answers.get('plate_changed') == PLATE_CHANGED else 'discount'
    if step == 'contact':
        return RESULT_STEP
    following = STEP_ORDER[STEP_ORDER.index(step) + 1]
    return following


def active_steps(answers):
    """The steps the given answers lead through, skipping the ones that do not apply."""
    has_previous_policy = answers.get('policy_status') == HAD_PREVIOUS_POLICY
    steps = []
    for step in STEP_ORDER:
        if step in ('previous_policy', 'plate_change', 'discount_source', 'discount') and not has_previous_policy:
            continue
        if step == 'discount_source' and answers.get('plate_changed') != PLATE_CHANGED:
            continue
        steps.append(step)
    return steps


def required_names(step, answers):
    """Field names that must be answered before leaving ``step``."""
    optional = set(STEPS[step].get('optional', []))
    conditional = STEPS[step].get('required_when', {})
    names = [name for name in STEPS[step]['fields'] if name not in optional | set(conditional)]
    for name, (parent, value) in conditional.items():
        if answers.get(parent) == value:
            names.append(name)
    return names


def is_complete(answers, step):
    return all(answers.get(name) for name in required_names(step, answers))


def first_unanswered(answers):
    for step in active_steps(answers):
        if not is_complete(answers, step):
            return step
    return None


def collect(request, step, answers):
    """Split the submitted step into ``(answers, invalid_fields)``.

    Conditional fields are judged against the answer just submitted, so picking
    «بله دریافت کرده‌ام» makes the damage counts mandatory on the same post.
    """
    accepted, seen = {}, dict(answers)
    for name, values in STEPS[step]['fields'].items():
        value = request.POST.get(name, '').strip()
        if value and (values is None or value in values):
            accepted[name] = value
            seen[name] = value
    required = set(required_names(step, seen))
    invalid = [name for name in STEPS[step]['fields'] if name not in accepted and name in required]
    return accepted, invalid
