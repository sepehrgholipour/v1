"""The short, quote-first journey used for elevator liability insurance."""

SESSION_KEY = 'elevator_quote'
TITLE = 'بیمه آسانسور'

STEPS = {
    'usage': {
        'label': 'نوع کاربری', 'title': 'نوع کاربری آسانسور چیست؟',
        'description': 'کاربری ساختمان را انتخاب کنید تا پیشنهادهای متناسب نمایش داده شوند.',
        'field': 'usage', 'options': ['مسکونی', 'اداری-تجاری', 'باربری'],
    },
    'capacity': {
        'label': 'ظرفیت', 'title': 'ظرفیت آسانسور چقدر است؟',
        'description': 'ظرفیت درج‌شده روی پلاک آسانسور را انتخاب کنید.',
        'field': 'capacity', 'options': [f'{n} نفر' for n in range(2, 13)],
    },
    'stops': {
        'label': 'تعداد طبقات آسانسور', 'title': 'تعداد طبقات آسانسور',
        'description': 'همه طبقات دارای ایستگاه آسانسور را در نظر بگیرید.',
        'field': 'stops', 'options': [f'{n} طبقه' for n in range(2, 21)],
    },
    'age': {
        'label': 'عمر آسانسور', 'title': 'عمر آسانسور چقدر است؟',
        'description': 'سن تقریبی آسانسور را از زمان نصب انتخاب کنید.',
        'field': 'age', 'options': [f'{n} سال' for n in range(1, 26)],
    },
    'door': {
        'label': 'درب داخلی', 'title': 'آسانسور دارای درب داخلی است',
        'description': 'منظور درب کابین آسانسور است، نه درب طبقات.',
        'field': 'interior_door', 'options': ['خیر', 'بله'],
    },
}

ORDER = list(STEPS)


def url_name(step):
    return 'elevator_result' if step == 'result' else f'elevator_{step}'


def next_step(step):
    index = ORDER.index(step)
    return 'result' if index == len(ORDER) - 1 else ORDER[index + 1]


def first_unanswered(answers):
    return next((step for step in ORDER if not answers.get(STEPS[step]['field'])), None)


def collect(request, step):
    spec = STEPS[step]
    value = request.POST.get(spec['field'], '').strip()
    return value if value in spec['options'] else None
