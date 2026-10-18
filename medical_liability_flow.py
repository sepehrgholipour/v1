"""Medical liability form definitions matching BimeBazar forms 11066/11067."""
import json
import urllib.request

SESSION_KEY = 'medical_liability_quote'
TITLE = 'بیمه مسئولیت پزشکان و پیراپزشکان'
API = 'https://others.bimebazar.com/MasterApi/GetInsuranceForm'
DETAILS_STEP = 'coverage_details'
DOCTOR_SPECIALTIES = [
    'پزشک عمومی', 'متخصص داخلی', 'متخصص قلب و عروق', 'متخصص مغز و اعصاب',
    'متخصص جراحی عمومی', 'متخصص ارتوپدی', 'متخصص زنان و زایمان',
    'متخصص کودکان', 'متخصص چشم پزشکی', 'متخصص گوش، حلق و بینی',
    'متخصص پوست و مو', 'متخصص بیهوشی', 'متخصص رادیولوژی',
    'متخصص پاتولوژی', 'متخصص روانپزشکی', 'متخصص اورولوژی',
    'متخصص عفونی', 'متخصص طب فیزیکی و توانبخشی', 'دندانپزشک عمومی',
    'متخصص جراحی فک و صورت', 'داروساز',
]
PARAMEDICAL_SPECIALTIES = [
    'کارشناس پرستاری', 'کاردان پرستاری', 'کمک پرستار', 'بهیار', 'اتاق عمل',
    'هوشبری', 'مامایی', 'علوم آزمایشگاهی', 'رادیولوژی', 'فیزیوتراپی',
    'کاردرمانی', 'گفتاردرمانی', 'بینایی سنجی', 'شنوایی سنجی', 'تغذیه',
    'بهداشت عمومی', 'بهداشت محیط', 'بهداشت حرفه‌ای', 'فوریت‌های پزشکی',
    'تکنسین دارویی', 'تکنسین دندانپزشکی', 'پروتز دندان', 'ارتوپدی فنی',
]
FALLBACK = {45: [('doctorSpecial','تخصص خود را انتخاب کنید.','تخصصی پزشکی',DOCTOR_SPECIALTIES),('TedadDieDarkhasty_doc','تعداد دیه درخواستی','انتخاب کنید',['یک دیه','دو دیه','سه دیه','چهار دیه','پنج دیه']),('AfzayeshMablaghRiyali','پوشش افزایش مبلغ ریالی دیه','انتخاب کنید',['فاقد پوشش','یک سال','دو سال','سه سال']),('extraDr','پوششهای تکمیلی','انتخاب کنید',['مسئولیت رزیدنت','مسئولیت فلوشیپ','پرداخت بدون اعمال تعرفه','افزایش مدت مرور زمان دعاوی','پوشش تکمیلی خدمات زیبایی']),('AdamKhesaratPezeshkan','سابقه عدم خسارت خود را انتخاب کنید.','سابقه عدم خسارت',['با خسارت','صدور اولیه','یکسال عدم خسارت','دوسال عدم خسارت','سه‌سال عدم خسارت','چهارسال عدم خسارت','پنج سال عدم خسارت','شش سال عدم خسارت','هفت سال عدم خسارت و بیشتر']),('EndTime','تاریخ پایان بیمه‌نامه قبلی','تاریخ پایان بیمه نامه',[]),('Modat_BimeName_Oezeshkan','مدت بیمه نامه','انتخاب کنید',['یک سال'])],46: [('PirapezeskanList','تخصص خود را انتخاب کنید.','تخصصی پیراپزشکی',PARAMEDICAL_SPECIALTIES),('TedadDieDarkhasty_doc','تعداد دیه درخواستی','انتخاب کنید',['یک دیه','دو دیه','سه دیه','چهار دیه','پنج دیه']),('AfzayeshMablaghRiyali','پوشش افزایش مبلغ ریالی دیه','انتخاب کنید',['فاقد پوشش','یک سال','دو سال','سه سال']),('extra_pirapezeshk','اطلاعات تکمیلی','انتخاب کنید',['دانشجو هستم','پرستار و یا بهیار شاغل در مطب هستم','پرداخت بدون اعمال تعرفه','افزایش مدت مرور زمان دعاوی']),('AdamKhesaratPezeshkan','سابقه عدم خسارت خود را انتخاب کنید.','سابقه عدم خسارت',['با خسارت','صدور اولیه','یکسال عدم خسارت','دوسال عدم خسارت','سه‌سال عدم خسارت','چهارسال عدم خسارت','پنج سال عدم خسارت','شش سال عدم خسارت','هفت سال عدم خسارت و بیشتر']),('EndTime','تاریخ پایان بیمه‌نامه قبلی','تاریخ پایان بیمه نامه',[]),('Modat_BimeName_Oezeshkan','مدت بیمه نامه','انتخاب کنید',['یک سال'])]}
_forms = {}
def _load(kind):
    if kind in _forms: return _forms[kind]
    try:
        req=urllib.request.Request(API,data=json.dumps({'categoryId':kind}).encode(),headers={'Content-Type':'application/json'},method='POST')
        with urllib.request.urlopen(req,timeout=5) as response: data=json.load(response)
        result=[]
        for page in data.get('pages',[]):
            for form in page.get('forms',[]):
                if form.get('typesName') != 'Info': result.append((form['formName'],form['lbLName'].strip(),form.get('placeHolder','').strip(),[x['dataName'].strip() for x in form.get('formData',[])]))
        _forms[kind]=result or FALLBACK[kind]
    except Exception: _forms[kind]=FALLBACK[kind]
    return _forms[kind]
def kind(answers): return 45 if answers.get('applicant_type') == 'مسئولیت پزشکان' else 46
def fields(answers):
    result=list(_load(kind(answers))); history=answers.get('AdamKhesaratPezeshkan','')
    if history in ('صدور اولیه',''): result=[x for x in result if x[0] != 'EndTime']
    return result
def detail_fields(answers):
    return [x for x in fields(answers) if x[0] not in ('AdamKhesaratPezeshkan', 'EndTime', 'Modat_BimeName_Oezeshkan')]
def later_fields(answers):
    return [x for x in fields(answers) if x[0] in ('AdamKhesaratPezeshkan', 'EndTime', 'Modat_BimeName_Oezeshkan')]
def order(answers): return ['applicant_type', DETAILS_STEP]+[x[0] for x in later_fields(answers)]+['mobile', 'full_name']
def field_spec(name,label,placeholder,options,doctor_lists=False):
    return {
        'label': label,
        'title': label,
        'field': name,
        'placeholder': placeholder,
        'options': options,
        'multiple': name in ('extraDr', 'extra_pirapezeshk'),
        'input_type': 'date' if name == 'EndTime' else None,
        # The four physician questions are intentionally presented together as
        # compact, scrollable lists. Paramedical retains its separate layout.
        'list_style': 'scroll' if doctor_lists or name in ('PirapezeskanList', 'doctorSpecial') else 'cards',
    }
def spec(step,answers):
    if step=='applicant_type': return {'label':'نوع بیمه','title':'نوع بیمه موردنظر خود را انتخاب کنید','field':'applicant_type','options':['مسئولیت پزشکان','مسئولیت پیراپزشکان']}
    if step==DETAILS_STEP:
        grouped = [field_spec(*item, doctor_lists=kind(answers) == 45) for item in detail_fields(answers)]
        return {'label':'اطلاعات بیمه‌نامه','title':'اطلاعات بیمه‌نامه را انتخاب کنید','field':DETAILS_STEP,'fields':grouped,'is_group':True}
    if step == 'mobile': return {'label':'شماره موبایل','title':'شماره موبایل خود را وارد کنید','field':'mobile','input_type':'tel','placeholder':'۰۹۱۲۱۲۳۴۵۶۷'}
    if step == 'full_name': return {'label':'نام و نام خانوادگی','title':'نام و نام خانوادگی را وارد کنید','field':'full_name','input_type':'text','placeholder':'نام و نام خانوادگی'}
    for item in fields(answers):
        if item[0]==step: return field_spec(*item)
    raise KeyError(step)
def _collect_item(request,item):
    if item.get('multiple'):
        value=[x.strip() for x in request.POST.getlist(item['field']) if x.strip()]
        return value if all(x in item['options'] for x in value) else None
    value=request.POST.get(item['field'],'').strip()
    if item.get('input_type')=='date': return value or None
    if item.get('input_type')=='tel': return value if __import__('re').fullmatch(r'09\d{9}', value.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹','0123456789'))) else None
    if item.get('input_type')=='text': return value if 3 <= len(value) <= 256 else None
    return value if value in item.get('options',[]) else None
def collect(request,step,answers):
    item=spec(step,answers)
    if item.get('is_group'):
        values = {}
        for child in item['fields']:
            value = _collect_item(request, child)
            if value is None:
                return None
            values[child['field']] = value
        return values
    return _collect_item(request,item)
def answered(step,answers):
    item=spec(step,answers)
    if item.get('is_group'):
        return all(child.get('multiple') or answers.get(child['field']) for child in item['fields'])
    return item.get('multiple') or bool(answers.get(item['field']))
