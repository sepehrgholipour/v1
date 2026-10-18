"""Step-by-step building information needed for a fire-insurance quote."""

SESSION_KEY = 'fire_quote'
TITLE = 'بیمه آتش‌سوزی'

STEPS = {
    'usage': {'label': 'کاربری ملک', 'title': 'کاربری ملک چیست؟', 'description': 'نوع استفاده از محل مورد بیمه را انتخاب کنید.', 'field': 'usage', 'options': ['مسکونی', 'اداری', 'تجاری', 'انبار', 'کارگاه و صنعتی']},
    'property_type': {'label': 'نوع ملک', 'title': 'نوع ملک را انتخاب کنید', 'description': 'مشخصات ملک در محاسبه پیشنهادها اثر دارد.', 'field': 'property_type', 'options': ['آپارتمان', 'خانه ویلایی', 'مجتمع مسکونی', 'مغازه یا دفتر', 'سوله و کارگاه']},
    'units': {'label': 'تعداد واحد', 'title': 'ملک چند واحد دارد؟', 'description': 'تعداد کل واحدهای ساختمان را انتخاب کنید.', 'field': 'units', 'options': ['یک واحد', '۲ تا ۴ واحد', '۵ تا ۱۰ واحد', 'بیش از ۱۰ واحد']},
    'structure': {'label': 'نوع سازه', 'title': 'نوع سازه ساختمان چیست؟', 'description': 'نوع اسکلت یا مصالح اصلی بنا را انتخاب کنید.', 'field': 'structure', 'options': ['بتنی', 'فلزی', 'آجری', 'سایر']},
    'age': {'label': 'عمر بنا', 'title': 'عمر بنا چقدر است؟', 'description': 'سن تقریبی ساختمان را از زمان ساخت انتخاب کنید.', 'field': 'age', 'options': ['کمتر از ۵ سال', '۵ تا ۱۵ سال', 'بیش از ۱۵ سال']},
    'area': {'label': 'متراژ', 'title': 'متراژ مورد بیمه را وارد کنید', 'description': 'متراژ کل فضای مورد بیمه را برحسب مترمربع وارد کنید.', 'field': 'area', 'input_type': 'number', 'placeholder': 'مثلاً ۱۲۰'},
    'insured_item': {'label': 'مورد بیمه', 'title': 'چه چیزی را بیمه می‌کنید؟', 'description': 'پوشش موردنظر خود را انتخاب کنید.', 'field': 'insured_item', 'options': ['بنا و لوازم', 'فقط بنا', 'فقط لوازم و اثاثیه']},
    'building_value': {'label': 'ارزش بنا', 'title': 'هزینه ساخت هر مترمربع را انتخاب کنید', 'description': 'این مبلغ برای محاسبه ارزش بازسازی بنا استفاده می‌شود؛ قیمت زمین ملاک نیست.', 'field': 'building_value', 'options': ['تا ۱۵ میلیون تومان', '۱۵ تا ۲۵ میلیون تومان', '۲۵ تا ۴۰ میلیون تومان', 'بیش از ۴۰ میلیون تومان']},
    'contents_value': {'label': 'ارزش لوازم', 'title': 'ارزش لوازم و اثاثیه چقدر است؟', 'description': 'طلا، جواهرات و پول نقد را در این مبلغ لحاظ نکنید.', 'field': 'contents_value', 'options': ['تا ۵۰۰ میلیون تومان', '۵۰۰ میلیون تا ۱ میلیارد تومان', '۱ تا ۳ میلیارد تومان', 'بیش از ۳ میلیارد تومان']},
    'coverage': {'label': 'پوشش تکمیلی', 'title': 'پوشش‌های تکمیلی را انتخاب کنید', 'description': 'برای دریافت پیشنهاد، سطح پوشش موردنظر را مشخص کنید.', 'field': 'coverage', 'options': ['فقط آتش‌سوزی، صاعقه و انفجار', 'آتش‌سوزی به‌همراه زلزله', 'پوشش کامل (زلزله، سیل و سرقت)']},
}
ORDER = list(STEPS)

def url_name(step): return 'fire_result' if step == 'result' else f'fire_{step}'
def next_step(step): return 'result' if ORDER.index(step) == len(ORDER) - 1 else ORDER[ORDER.index(step) + 1]
def first_unanswered(answers): return next((step for step in ORDER if not answers.get(STEPS[step]['field'])), None)
def collect(request, step):
    spec, value = STEPS[step], request.POST.get(STEPS[step]['field'], '').strip()
    if spec.get('input_type') == 'number':
        return value if value.isdigit() and 1 <= int(value) <= 100000 else None
    return value if value in spec['options'] else None
