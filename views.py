from django.shortcuts import redirect, render
from django.urls import reverse

from . import motorcycle_flow
from . import elevator_flow
from . import fire_flow
from . import supplemental_flow
from . import medical_liability_flow
from . import life_flow
from . import travel_flow
from .vehicle_catalog import VEHICLE_CATALOG


QUOTE_TYPES = {
    'third_party': 'بیمه شخص ثالث',
    'body': 'بیمه بدنه',
}


def home(request):
    return render(request, 'pages/home.html')


def _quote(request, kind):
    return request.session.get(f'{kind}_quote', {})


def _save_quote(request, kind, quote):
    request.session[f'{kind}_quote'] = quote


def _context(kind, quote, step, **extra):
    return {
        'quote': quote,
        'step': step,
        'insurance_title': QUOTE_TYPES[kind],
        'lookup_url_name': f'{kind}_lookup',
        'vehicle_url_name': f'{kind}_vehicle',
        'history_url_name': f'{kind}_history',
        'plate_letters': ('الف', 'ب', 'ج', 'د', 'س', 'ص', 'ط', 'ق', 'ل', 'م', 'ن', 'و', 'ه', 'ی'),
        'vehicle_catalog': VEHICLE_CATALOG,
        **extra,
    }


def quote_lookup(request, kind):
    quote = _quote(request, kind)
    if request.method == 'POST':
        plate_parts = [request.POST.get(key, '').strip() for key in ('plate_left', 'plate_letter', 'plate_middle', 'plate_city')]
        quote.update({
            'license_plate': '-'.join(plate_parts),
            'national_code': request.POST.get('national_code', '').strip(),
            'entry_method': 'lookup',
        })
        _save_quote(request, kind, quote)
        return redirect(f'{kind}_history')
    plate_parts = quote.get('license_plate', '').split('-')
    if len(plate_parts) != 4:
        plate_parts = ('', 'الف', '', '')
    return render(request, 'pages/quote_lookup.html', _context(kind, quote, 1, plate_parts=plate_parts))


def quote_vehicle(request, kind):
    quote = _quote(request, kind)
    if request.method == 'POST':
        vehicle_type = request.POST.get('vehicle_type', '').strip()
        valid_types = ('سواری', 'وانت', 'کامیون', 'کامیونت', 'ون')
        if vehicle_type not in valid_types:
            return render(request, 'pages/quote_vehicle.html', _context(kind, quote, 1, error='نوع وسیله نقلیه را انتخاب کنید.'), status=400)
        quote['vehicle_type'] = vehicle_type
        quote.pop('brand', None)
        quote.pop('model', None)
        quote.pop('year', None)
        quote['entry_method'] = 'manual'
        quote.pop('license_plate', None)
        _save_quote(request, kind, quote)
        return redirect(f'{kind}_vehicle_details')
    return render(request, 'pages/quote_vehicle.html', _context(kind, quote, 1))


VEHICLE_DETAILS = {
    'سواری': {'title': 'مشخصات خودروی سواری', 'fields': {'vehicle_usage': ['شخصی', 'تاکسی', 'آموزش رانندگی'], 'cylinder_count': ['کمتر از ۴ سیلندر', '۴ سیلندر', 'بیش از ۴ سیلندر'], 'vehicle_year': ['۱۴۰۴ به بعد', '۱۳۹۵ تا ۱۴۰۳', 'قبل از ۱۳۹۵']}},
    'وانت': {'title': 'مشخصات وانت', 'fields': {'vehicle_usage': ['شخصی', 'عمومی'], 'cargo_type': ['بار عادی', 'مواد خطرناک', 'حمل سوخت'], 'vehicle_year': ['۱۴۰۴ به بعد', '۱۳۹۵ تا ۱۴۰۳', 'قبل از ۱۳۹۵']}},
    'کامیون': {'title': 'مشخصات کامیون', 'fields': {'vehicle_usage': ['شخصی', 'عمومی'], 'cargo_type': ['بار عادی', 'مواد خطرناک', 'حمل سوخت'], 'vehicle_year': ['۱۴۰۴ به بعد', '۱۳۹۵ تا ۱۴۰۳', 'قبل از ۱۳۹۵']}},
    'کامیونت': {'title': 'مشخصات کامیونت', 'fields': {'vehicle_usage': ['شخصی', 'عمومی'], 'cargo_type': ['بار عادی', 'مواد خطرناک', 'حمل سوخت'], 'vehicle_year': ['۱۴۰۴ به بعد', '۱۳۹۵ تا ۱۴۰۳', 'قبل از ۱۳۹۵']}},
    'ون': {'title': 'مشخصات ون', 'fields': {'vehicle_usage': ['شخصی', 'عمومی', 'تاکسی'], 'passenger_capacity': ['تا ۹ نفر', '۱۰ تا ۱۵ نفر', 'بیش از ۱۵ نفر'], 'vehicle_year': ['۱۴۰۴ به بعد', '۱۳۹۵ تا ۱۴۰۳', 'قبل از ۱۳۹۵']}},
}


def quote_vehicle_details(request, kind):
    quote = _quote(request, kind)
    details = VEHICLE_DETAILS.get(quote.get('vehicle_type'))
    if not details:
        return redirect(f'{kind}_vehicle')
    if request.method == 'POST':
        submitted = {name: request.POST.get(name, '').strip() for name in details['fields']}
        if any(value not in details['fields'][name] for name, value in submitted.items()):
            return render(request, 'pages/quote_vehicle_details.html', _context(kind, {**quote, **submitted}, 1, details=details, error='لطفاً همه مشخصات را انتخاب کنید.'), status=400)
        quote.update(submitted)
        _save_quote(request, kind, quote)
        return redirect(f'{kind}_history')
    return render(request, 'pages/quote_vehicle_details.html', _context(kind, quote, 1, details=details))


def quote_history(request, kind):
    quote = _quote(request, kind)
    if not quote.get('vehicle_type') and not quote.get('license_plate'):
        return redirect(f'{kind}_lookup')
    if quote.get('entry_method') == 'manual' and not quote.get('vehicle_usage'):
        return redirect(f'{kind}_vehicle_details')
    if request.method == 'POST':
        quote['policy_status'] = request.POST.get('policy_status', '').strip()
        _save_quote(request, kind, quote)
        if quote['policy_status'] == 'دارم':
            return redirect(f'{kind}_history_dates')
        return redirect(f'{kind}_owner')
    entry_method = quote.get('entry_method') or ('lookup' if quote.get('license_plate') else 'manual')
    previous_url = reverse(f'{kind}_lookup' if entry_method == 'lookup' else f'{kind}_vehicle')
    return render(request, 'pages/quote_history.html', _context(kind, quote, 2, previous_url=previous_url))


def quote_history_dates(request, kind):
    quote = _quote(request, kind)
    if quote.get('policy_status') != 'دارم':
        return redirect(f'{kind}_history')
    if request.method == 'POST':
        start = request.POST.get('previous_start_date', '').strip()
        expiry = request.POST.get('expiry_date', '').strip()
        if not start or not expiry:
            return render(request, 'pages/quote_history_dates.html', _context(kind, quote, 2, error='هر دو تاریخ بیمه‌نامه را وارد کنید.'), status=400)
        quote.update({'previous_start_date': start, 'expiry_date': expiry})
        _save_quote(request, kind, quote)
        return redirect(f'{kind}_owner')
    return render(request, 'pages/quote_history_dates.html', _context(kind, quote, 2))


def quote_owner(request, kind):
    quote = _quote(request, kind)
    if not quote.get('policy_status'):
        return redirect(f'{kind}_history')
    if request.method == 'POST':
        quote.update({key: request.POST.get(key, '').strip() for key in ('full_name', 'national_code', 'mobile')})
        _save_quote(request, kind, quote)
        return redirect(f'{kind}_result')
    return render(request, 'pages/quote_owner.html', _context(kind, quote, 3))


def quote_result(request, kind):
    quote = _quote(request, kind)
    if not quote.get('full_name'):
        return redirect(f'{kind}_owner')
    return render(request, 'pages/quote_result.html', _context(kind, quote, 3))


def third_party_lookup(request): return quote_lookup(request, 'third_party')
def third_party_vehicle(request): return quote_vehicle(request, 'third_party')
def third_party_vehicle_details(request): return quote_vehicle_details(request, 'third_party')
def third_party_history(request): return quote_history(request, 'third_party')
def third_party_history_dates(request): return quote_history_dates(request, 'third_party')
def third_party_owner(request): return quote_owner(request, 'third_party')
def third_party_result(request): return quote_result(request, 'third_party')

def body_lookup(request): return quote_lookup(request, 'body')
def body_vehicle(request): return quote_vehicle(request, 'body')
def body_vehicle_details(request): return quote_vehicle_details(request, 'body')
def body_history(request): return quote_history(request, 'body')
def body_history_dates(request): return quote_history_dates(request, 'body')
def body_owner(request): return quote_owner(request, 'body')
def body_result(request): return quote_result(request, 'body')


def _motorcycle_answers(request):
    return request.session.get(motorcycle_flow.SESSION_KEY, {})


def _motorcycle_progress(steps, position, finished=False):
    progress = []
    for index, name in enumerate(steps):
        if finished or index < position:
            state = 'done'
        elif index == position:
            state = 'current'
        else:
            state = 'pending'
        progress.append({'label': motorcycle_flow.STEPS[name]['label'], 'state': state})
    return progress


def _motorcycle_context(answers, step, error=None):
    steps = motorcycle_flow.active_steps(answers)
    finished = step == motorcycle_flow.RESULT_STEP
    position = steps.index(step) if step in steps else len(steps)
    flow = motorcycle_flow
    return {
        'answers': answers,
        'step': step,
        'step_spec': flow.STEPS.get(step, {'label': 'استعلام قیمت و مقایسه', 'title': 'استعلام قیمت و مقایسه بیمه موتورسیکلت'}),
        'progress': _motorcycle_progress(steps, position, finished),
        'step_number': len(steps) if finished else position + 1,
        'step_total': len(steps),
        'back_url_name': 'home' if position <= 0 else flow.url_name(steps[position - 1]),
        'next_label': 'بعد',
        'error': error,
        'models': flow.MOTORCYCLE_MODELS,
        'years': flow.PRODUCTION_YEARS,
        'policy_status_options': flow.POLICY_STATUS_OPTIONS,
        'companies': flow.PREVIOUS_COMPANIES,
        'policy_start_dates': flow.POLICY_START_DATES,
        'policy_end_dates': flow.POLICY_END_DATES,
        'plate_change_options': flow.PLATE_CHANGE_OPTIONS,
        'discount_sources': flow.DISCOUNT_SOURCES,
        'discount_factors': flow.DISCOUNT_FACTORS,
        'damage_answers': flow.DAMAGE_ANSWER_OPTIONS,
        'damage_counts': flow.DAMAGE_COUNTS,
        'financial_coverages': flow.FINANCIAL_COVERAGES,
        'policy_terms': flow.POLICY_TERMS,
    }


def motorcycle_step(step):
    """One question of the motorcycle journey, guarded like the car flows."""
    def view(request):
        answers = _motorcycle_answers(request)
        steps = motorcycle_flow.active_steps(answers)
        pending = motorcycle_flow.first_unanswered(answers)
        if pending and (step not in steps or steps.index(step) > steps.index(pending)):
            return redirect(motorcycle_flow.url_name(pending))
        if request.method == 'POST':
            collected, invalid = motorcycle_flow.collect(request, step, answers)
            if invalid:
                return render(
                    request,
                    f'pages/motorcycle_{step}.html',
                    _motorcycle_context({**answers, **collected}, step, error='گزینه‌های انتخاب‌شده معتبر نیست. لطفاً دوباره بررسی کنید.'),
                    status=400,
                )
            answers.update(collected)
            request.session[motorcycle_flow.SESSION_KEY] = answers
            return redirect(motorcycle_flow.url_name(motorcycle_flow.next_step(answers, step)))
        return render(request, f'pages/motorcycle_{step}.html', _motorcycle_context(answers, step))
    return view


def motorcycle_result(request):
    answers = _motorcycle_answers(request)
    pending = motorcycle_flow.first_unanswered(answers)
    if pending:
        return redirect(motorcycle_flow.url_name(pending))
    return render(request, 'pages/motorcycle_result.html', _motorcycle_context(answers, motorcycle_flow.RESULT_STEP))


def elevator_step(step):
    def view(request):
        answers = request.session.get(elevator_flow.SESSION_KEY, {})
        pending = elevator_flow.first_unanswered(answers)
        if pending and elevator_flow.ORDER.index(step) > elevator_flow.ORDER.index(pending):
            return redirect(elevator_flow.url_name(pending))
        spec = elevator_flow.STEPS[step]
        if request.method == 'POST':
            value = elevator_flow.collect(request, step)
            if not value:
                return render(request, 'pages/elevator_step.html', _elevator_context(answers, step, 'لطفاً یکی از گزینه‌های نمایش‌داده‌شده را انتخاب کنید.'), status=400)
            answers[spec['field']] = value
            request.session[elevator_flow.SESSION_KEY] = answers
            return redirect(elevator_flow.url_name(elevator_flow.next_step(step)))
        return render(request, 'pages/elevator_step.html', _elevator_context(answers, step))
    return view


def _elevator_context(answers, step, error=None):
    position = elevator_flow.ORDER.index(step)
    return {
        'answers': answers, 'step_spec': elevator_flow.STEPS[step], 'error': error, 'product_title': elevator_flow.TITLE,
        'selected_value': answers.get(elevator_flow.STEPS[step]['field'], ''),
        'product_description': 'مشخصات آسانسور را وارد کنید تا پیشنهاد شرکت‌های بیمه را مقایسه کنید.',
        'step_number': position + 1, 'step_total': len(elevator_flow.ORDER),
        'progress': [
            {'label': elevator_flow.STEPS[name]['label'], 'state': 'done' if index < position else ('current' if index == position else 'pending')}
            for index, name in enumerate(elevator_flow.ORDER)
        ],
        'back_url_name': 'home' if position == 0 else elevator_flow.url_name(elevator_flow.ORDER[position - 1]),
    }


def elevator_result(request):
    answers = request.session.get(elevator_flow.SESSION_KEY, {})
    pending = elevator_flow.first_unanswered(answers)
    if pending:
        return redirect(elevator_flow.url_name(pending))
    return render(request, 'pages/elevator_result.html', {
        'answers': answers, 'product_title': elevator_flow.TITLE,
        'product_description': 'مشخصات آسانسور ثبت شده و آمادهٔ مقایسهٔ پیشنهادهای بیمه است.',
        'page_title': 'استعلام بیمه آسانسور آماده است', 'step_spec': {'label': 'نتیجه', 'title': 'استعلام بیمه آسانسور آماده است'},
        'step_number': len(elevator_flow.ORDER), 'step_total': len(elevator_flow.ORDER),
        'progress': [{'label': elevator_flow.STEPS[name]['label'], 'state': 'done'} for name in elevator_flow.ORDER],
    })


def fire_step(step):
    def view(request):
        answers = request.session.get(fire_flow.SESSION_KEY, {})
        pending = fire_flow.first_unanswered(answers)
        if pending and fire_flow.ORDER.index(step) > fire_flow.ORDER.index(pending):
            return redirect(fire_flow.url_name(pending))
        if request.method == 'POST':
            value = fire_flow.collect(request, step)
            if not value:
                return render(request, 'pages/fire_step.html', _fire_context(answers, step, 'اطلاعات واردشده معتبر نیست. لطفاً دوباره بررسی کنید.'), status=400)
            answers[fire_flow.STEPS[step]['field']] = value
            request.session[fire_flow.SESSION_KEY] = answers
            return redirect(fire_flow.url_name(fire_flow.next_step(step)))
        return render(request, 'pages/fire_step.html', _fire_context(answers, step))
    return view


def _fire_context(answers, step, error=None):
    position = fire_flow.ORDER.index(step)
    return {'answers': answers, 'step_spec': fire_flow.STEPS[step], 'error': error, 'product_title': fire_flow.TITLE,
        'selected_value': answers.get(fire_flow.STEPS[step]['field'], ''),
        'product_description': 'مشخصات ساختمان را وارد کنید تا پوشش‌ها و پیشنهادهای مناسب بیمه آتش‌سوزی را مقایسه کنید.',
        'step_number': position + 1, 'step_total': len(fire_flow.ORDER),
        'progress': [{'label': fire_flow.STEPS[name]['label'], 'state': 'done' if index < position else ('current' if index == position else 'pending')} for index, name in enumerate(fire_flow.ORDER)],
        'back_url_name': 'home' if position == 0 else fire_flow.url_name(fire_flow.ORDER[position - 1])}


def fire_result(request):
    answers = request.session.get(fire_flow.SESSION_KEY, {})
    pending = fire_flow.first_unanswered(answers)
    if pending: return redirect(fire_flow.url_name(pending))
    return render(request, 'pages/fire_result.html', {
        'answers': answers, 'product_title': fire_flow.TITLE,
        'product_description': 'مشخصات ساختمان ثبت شده و آمادهٔ مقایسهٔ پیشنهادهای بیمه است.',
        'page_title': 'استعلام بیمه آتش‌سوزی آماده است', 'step_spec': {'label': 'نتیجه', 'title': 'استعلام بیمه آتش‌سوزی آماده است'},
        'step_number': len(fire_flow.ORDER), 'step_total': len(fire_flow.ORDER),
        'progress': [{'label': fire_flow.STEPS[name]['label'], 'state': 'done'} for name in fire_flow.ORDER],
    })


def supplemental_step(step):
    def view(request):
        answers = request.session.get(supplemental_flow.SESSION_KEY, {})
        order = supplemental_flow.steps(answers)
        if step not in order:
            return redirect('supplemental_count' if step == 'count' else 'supplemental_type')
        position = order.index(step); item = supplemental_flow.spec(step, answers)
        if request.method == 'POST':
            value = supplemental_flow.collect(request, step)
            if value is None:
                return render(request, 'pages/supplemental_step.html', _supplemental_context(answers, order, step, 'اطلاعات واردشده معتبر نیست.'), status=400)
            if isinstance(value, dict): answers.update(value)
            else: answers[item['field']] = value
            request.session[supplemental_flow.SESSION_KEY] = answers
            order = supplemental_flow.steps(answers)
            return redirect('supplemental_result' if position == len(order) - 1 else ('supplemental_count' if order[position + 1] == 'count' else reverse('supplemental_dynamic', kwargs={'step': order[position + 1]})))
        return render(request, 'pages/supplemental_step.html', _supplemental_context(answers, order, step))
    return view


def supplemental_dynamic(request, step):
    return supplemental_step(step)(request)


def _supplemental_context(answers, order, step, error=None):
    position = order.index(step)
    item = supplemental_flow.spec(step, answers)
    for field in item.get('fields', []):
        field['selected'] = answers.get(field['field'], '')
    previous = 'home' if position == 0 else ('supplemental_count' if order[position - 1] == 'count' else 'supplemental_dynamic')
    return {'answers': answers, 'step_spec': item, 'selected_value': answers.get(item.get('field', ''), ''), 'error': error, 'product_title': supplemental_flow.TITLE, 'product_description': 'اطلاعات افراد و بیمه پایه را وارد کنید تا طرح‌های مناسب را مقایسه کنید.', 'step_number': position + 1, 'step_total': len(order) + 1, 'progress': [{'label': supplemental_flow.spec(name, answers)['label'], 'state': 'done' if i < position else ('current' if i == position else 'pending')} for i, name in enumerate(order)], 'back_url_name': previous, 'back_url': '' if previous != 'supplemental_dynamic' else reverse('supplemental_dynamic', kwargs={'step': order[position - 1]})}


def supplemental_result(request):
    answers = request.session.get(supplemental_flow.SESSION_KEY, {})
    order = supplemental_flow.steps(answers)
    if any(
        any(field['field'] not in answers for field in supplemental_flow.spec(step, answers).get('fields', []))
        or supplemental_flow.spec(step, answers).get('field') not in answers
        for step in order
    ):
        return redirect('supplemental_type')
    return render(request, 'pages/supplemental_result.html', {'answers': answers, 'product_title': supplemental_flow.TITLE, 'product_description': 'اطلاعات شما ثبت شده و آمادهٔ مقایسهٔ طرح‌هاست.', 'page_title': 'استعلام بیمه درمان تکمیلی آماده است', 'step_spec': {'label': 'نتیجه', 'title': 'استعلام بیمه درمان تکمیلی آماده است'}, 'step_number': len(order) + 1, 'step_total': len(order) + 1, 'progress': [{'label': supplemental_flow.spec(name, answers)['label'], 'state': 'done'} for name in order]})


def medical_liability_step(step):
    def view(request):
        flow = medical_liability_flow
        answers = request.session.get(flow.SESSION_KEY, {})
        current_order = flow.order(answers)
        if step not in current_order:
            return redirect('medical_liability_type')
        position = current_order.index(step)
        missing = next((name for name in current_order[:position] if not flow.answered(name, answers)), None)
        if missing:
            return redirect('medical_liability_type' if missing == 'applicant_type' else reverse('medical_liability_field', kwargs={'step': missing}))
        if request.method == 'POST':
            value = flow.collect(request, step, answers)
            if value is None:
                return render(request, 'pages/medical_liability_step.html', _medical_liability_context(answers, step, 'اطلاعات واردشده معتبر نیست.'), status=400)
            if isinstance(value, dict):
                answers.update(value)
            elif step == 'applicant_type':
                answers = {flow.spec(step, answers)['field']: value}
            else:
                answers[flow.spec(step, answers)['field']] = value
            request.session[flow.SESSION_KEY] = answers
            new_order = flow.order(answers)
            return redirect('medical_liability_result' if position == len(new_order)-1 else reverse('medical_liability_field', kwargs={'step': new_order[position + 1]}))
        return render(request, 'pages/medical_liability_step.html', _medical_liability_context(answers, step))
    return view

def medical_liability_form(request):
    return medical_liability_step('applicant_type')(request)


def _medical_liability_context(answers, step, error=None):
    flow = medical_liability_flow
    current_order = flow.order(answers)
    position = current_order.index(step)
    spec = flow.spec(step, answers)
    spec['selected'] = answers.get(spec['field'], [])
    for field in spec.get('fields', []):
        field['selected'] = answers.get(field['field'], [])
        field['selected_value'] = answers.get(field['field'], '')
    return {
        'answers': answers, 'step_spec': spec, 'selected_value': answers.get(spec['field'], ''), 'error': error,
        'product_title': flow.TITLE, 'product_description': 'نوع درخواست و اطلاعات تماس خود را وارد کنید تا پیشنهادهای مناسب را دریافت کنید.',
        'step_number': position + 1, 'step_total': len(current_order),
        'progress': [{'label': flow.spec(name, answers)['label'], 'state': 'done' if i < position else ('current' if i == position else 'pending')} for i, name in enumerate(current_order)],
        'back_url_name': 'home',
        'back_url': '' if position == 0 else (reverse('medical_liability_type') if position == 1 else reverse('medical_liability_field', kwargs={'step': current_order[position - 1]})),
    }


def medical_liability_dynamic(request, step):
    return medical_liability_step(step)(request)


def medical_liability_result(request):
    flow = medical_liability_flow
    answers = request.session.get(flow.SESSION_KEY, {})
    current_order = flow.order(answers)
    if any(
        not flow.answered(name, answers)
        for name in current_order
    ):
        return redirect('medical_liability_type')
    return render(request, 'pages/medical_liability_result.html', {
        'answers': answers, 'product_title': flow.TITLE, 'product_description': 'اطلاعات شما ثبت شد و آماده دریافت پیشنهاد است.',
        'page_title': 'درخواست بیمه مسئولیت ثبت شد', 'step_spec': {'label': 'نتیجه', 'title': 'درخواست بیمه مسئولیت ثبت شد'},
        'step_number': len(current_order), 'step_total': len(current_order),
        'progress': [{'label': flow.spec(name, answers)['label'], 'state': 'done'} for name in current_order],
    })


def life_step(step):
    def view(request):
        flow=life_flow; answers=request.session.get(flow.SESSION_KEY,{})
        active=flow.active_steps(answers)
        if step not in active: return redirect('life_birth_year')
        pos=active.index(step)
        # Some route names (premium_six/premium_three) intentionally share the
        # `premium` answer field.  Guard steps by their input field, not URL name.
        pending=next((name for name in active[:pos] if flow.spec(name, answers)['field'] not in answers),None)
        if pending: return redirect('life_birth_year' if pending=='birth_year' else reverse('life_field',kwargs={'step':pending}))
        if request.method=='POST':
            value=flow.collect(request,step,answers)
            if value is None: return render(request,'pages/supplemental_step.html',_life_context(answers,step,'اطلاعات واردشده معتبر نیست.'),status=400)
            answers[flow.spec(step,answers)['field']]=value; request.session[flow.SESSION_KEY]=answers
            active=flow.active_steps(answers)
            return redirect('life_result' if pos==len(active)-1 else reverse('life_field',kwargs={'step':active[pos+1]}))
        return render(request,'pages/supplemental_step.html',_life_context(answers,step))
    return view

def _life_context(answers,step,error=None):
    active=life_flow.active_steps(answers); pos=active.index(step); spec=life_flow.spec(step,answers)
    if 'labels' in spec: spec['option_labels']=dict(zip(spec['options'],spec['labels']))
    return {'answers':answers,'step_spec':spec,'selected_value':answers.get(spec['field'],''),'error':error,'product_title':life_flow.TITLE,'product_description':'اطلاعات طرح بیمه عمر خود را وارد کنید تا پیشنهادهای مناسب را مقایسه کنید.','step_number':pos+1,'step_total':len(active),'progress':[{'label':life_flow.spec(n,answers)['label'],'state':'done' if i<pos else ('current' if i==pos else 'pending')} for i,n in enumerate(active)],'back_url_name':'home','back_url':'' if pos==0 else (reverse('life_birth_year') if pos==1 else reverse('life_field',kwargs={'step':active[pos-1]}))}

def life_dynamic(request,step): return life_step(step)(request)

def life_result(request):
    answers=request.session.get(life_flow.SESSION_KEY,{}) ; active=life_flow.active_steps(answers)
    if any(life_flow.spec(name, answers)['field'] not in answers for name in active): return redirect('life_birth_year')
    return render(request,'pages/life_result.html',{'answers':answers,'product_title':life_flow.TITLE,'step_spec':{'label':'نتیجه','title':'استعلام بیمه عمر آماده است'},'step_number':len(active),'step_total':len(active),'progress':[{'label':life_flow.spec(n,answers)['label'],'state':'done'} for n in active]})


def travel_step(step):
    def view(request):
        answers = request.session.get(travel_flow.SESSION_KEY, {})
        position = travel_flow.STEPS.index(step); item = travel_flow.spec(step)
        if request.method == 'POST':
            value = travel_flow.collect(request, step)
            if value is None:
                return render(request, 'pages/travel_step.html', _travel_context(answers, step, 'لطفاً اطلاعات معتبر وارد کنید.'), status=400)
            answers.update(value if isinstance(value, dict) else {item['field']: value}); request.session[travel_flow.SESSION_KEY] = answers
            return redirect('travel_result' if position == len(travel_flow.STEPS)-1 else ['travel_country','travel_persons','travel_duration'][position+1])
        return render(request, 'pages/travel_step.html', _travel_context(answers, step))
    return view


def _travel_context(answers, step, error=None):
    item = travel_flow.spec(step)
    for field in item.get('fields', []): field['selected'] = answers.get(field['field'], '0')
    pos = travel_flow.STEPS.index(step)
    return {'answers': answers, 'step_spec': item, 'selected_value': answers.get(item.get('field',''), ''), 'error': error, 'product_title': travel_flow.TITLE, 'product_description': 'کشور مقصد، تعداد مسافران و مدت سفر خود را وارد کنید.', 'step_number': pos+1, 'step_total': len(travel_flow.STEPS), 'progress': [{'label': travel_flow.spec(n)['label'], 'state': 'done' if i<pos else ('current' if i==pos else 'pending')} for i,n in enumerate(travel_flow.STEPS)], 'back_url_name': 'home' if pos == 0 else ['travel_country','travel_persons','travel_duration'][pos-1]}


def travel_result(request):
    answers = request.session.get(travel_flow.SESSION_KEY, {})
    if not all(answers.get(k) for k in ('country','duration')): return redirect('travel_country')
    return render(request, 'pages/travel_result.html', {'answers': answers, 'product_title': travel_flow.TITLE, 'product_description': 'اطلاعات سفر ثبت شده و آمادهٔ مقایسهٔ پیشنهادهاست.', 'step_spec': {'title':'استعلام بیمه مسافرتی آماده است','label':'نتیجه'}, 'step_number':4, 'step_total':4, 'progress':[{'label': travel_flow.spec(n)['label'], 'state':'done'} for n in travel_flow.STEPS]})
