"""Supplemental health quote wizard, matching the fields used by BimeBazar."""
SESSION_KEY = 'supplemental_quote'
TITLE = 'بیمه درمان تکمیلی'
TYPE_OPTIONS = ['انفرادی', 'خانوادگی', 'سازمانی']
AGE_OPTIONS = ['از ۰ تا ۱۵ سال', 'از ۱۶ تا ۴۵ سال', 'از ۴۶ تا ۵۰ سال', 'از ۵۱ تا ۶۰ سال', 'از ۶۱ تا ۷۰ سال']
BASE_OPTIONS = ['سازمان تامین اجتماعی', 'سازمان بیمه خدمات درمانی', 'سازمان بیمه خدمات درمانی نیروهای مسلح', 'بیمه سلامت ایرانیان', 'فاقد بیمه‌گر پایه']
ILLNESS_OPTIONS = ['بیماری قلبی', 'انواع سرطان', 'انواع سکته قلبی یا مغزی', 'دیابت وابسته به انسولین', 'صرع', 'ندارم']

def initial():
    return {'type': {'label': 'بیمه موردنظر خود را انتخاب کنید.', 'title': 'بیمه موردنظر خود را انتخاب کنید.', 'field': 'insurance_type', 'options': TYPE_OPTIONS},
            'count': {'label': 'تعداد افراد را مشخص کنید:', 'title': 'تعداد افراد را مشخص کنید:', 'field': 'number_of_person'},
            'age': {'label': 'بازه سنی', 'title': 'بازه سنی', 'field': 'age_range', 'options': AGE_OPTIONS},
            'base': {'label': 'شرکت بیمه‌گر پایه', 'title': 'شرکت بیمه‌گر پایه', 'field': 'base_insurance', 'options': BASE_OPTIONS},
            'illness': {'label': 'بیماری زمینه‌ای', 'title': 'بیماری زمینه‌ای', 'field': 'chronic_illness', 'options': ILLNESS_OPTIONS},
            'mobile': {'label': 'موبایل', 'title': 'شماره موبایل خود را وارد کنید', 'field': 'cell_num', 'input_type': 'tel', 'placeholder': '۰۹۱۲۱۲۳۴۵۶۷'},
            'name': {'label': 'نام و نام خانوادگی', 'title': 'نام و نام خانوادگی', 'field': 'full_name', 'input_type': 'text', 'placeholder': 'نام و نام خانوادگی'},
            'company_name': {'label': 'نام شرکت', 'title': 'مشخصات شرکت را وارد کنید', 'field': 'company_name', 'input_type': 'text', 'placeholder': 'نام شرکت'},
            'company_id': {'label': 'شناسه ملی شرکت', 'title': 'مشخصات شرکت را وارد کنید', 'field': 'company_national_id', 'input_type': 'text', 'placeholder': 'شناسه ملی شرکت'},
            'agent_mobile': {'label': 'شماره تلفن همراه نماینده شرکت', 'title': 'لطفاً شماره تلفن همراه نماینده شرکت را وارد کنید', 'field': 'cell_num', 'input_type': 'tel', 'placeholder': '۰۹۱۲۱۲۳۴۵۶۷'}}

def steps(answers):
    result = ['type', 'count']
    if answers.get('insurance_type') == TYPE_OPTIONS[2]:
        return result + ['company_name', 'company_id', 'agent_mobile']
    try:
        person_count = int(answers.get('number_of_person', 0))
    except (TypeError, ValueError):
        person_count = 0
    return result + [f'person_{number}' for number in range(1, person_count + 1)] + ['mobile', 'name']

def spec(step, answers=None):
    answers = answers or {}
    if step == 'count':
        data = initial()['count'].copy()
        insurance_type = answers.get('insurance_type')
        if insurance_type == TYPE_OPTIONS[2]:
            data.update(input_type='number', min=10, max=10000, unit='نفر', label='تعداد افراد را (با احتساب اعضای خانواده) مشخص کنید:', title='تعداد افراد را (با احتساب اعضای خانواده) مشخص کنید:', placeholder='تعداد افراد')
        else:
            minimum, maximum = (2, 15) if insurance_type == TYPE_OPTIONS[1] else (1, 20)
            options = list(range(minimum, maximum + 1))
            data.update(options=options, option_labels={number: f'{number} نفر' for number in options}, display='person_count_picker')
        return data
    if step.startswith('person_'):
        person = step.rsplit('_', 1)[1]
        is_family = answers.get('insurance_type') == 'خانوادگی'
        person_title = 'اطلاعات سرپرست' if is_family and person == '1' else f'اطلاعات نفر {person}'
        return {'label': person_title, 'title': person_title, 'field': f'person_{person}', 'fields': [
            dict(initial()['age'], field=f'age_range_{person}', label='بازه سنی'),
            dict(initial()['base'], field=f'base_insurance_{person}', label='شرکت بیمه‌گر پایه'),
            dict(initial()['illness'], field=f'chronic_illness_{person}', label='بیماری زمینه‌ای'),
        ]}
    return initial()[step]

def collect(request, step):
    if step.startswith('person_'):
        data = {f'person_{step.rsplit("_", 1)[1]}': 'ثبت شد'}
        for field in spec(step, request.session.get(SESSION_KEY, {}))['fields']:
            value = request.POST.get(field['field'], '').strip()
            if value not in field['options']:
                return None
            data[field['field']] = value
        return data
    item = spec(step, request.session.get(SESSION_KEY, {})); value = request.POST.get(item['field'], '').strip()
    if item.get('input_type') == 'number': return value if value.isdigit() and item['min'] <= int(value) <= item['max'] else None
    if item['field'] == 'number_of_person':
        return value if value.isdigit() and int(value) in item.get('options', []) else None
    if item.get('input_type') == 'tel': return value if __import__('re').fullmatch(r'09\d{9}', value.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹','0123456789'))) else None
    if item['field'] in ('full_name', 'company_name'): return value if 3 <= len(value) <= 256 else None
    if item['field'] == 'company_national_id': return value if 3 <= len(value) <= 256 else None
    return value if value in item.get('options', []) else None
