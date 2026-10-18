"""Life insurance wizard matching the BimeBazar life-insurance flow."""
SESSION_KEY='life_quote'
TITLE='خرید بیمه عمر'
ORDER=['birth_year','contract_duration','premium_installment_num','premium','premium_increase_rate','annual_death_benefit_growth','death_benefit_ratio']
YEARS=list(range(1405,1305,-1))
INSTALLMENTS=[('سالانه',1),('سه ماهه',4),('شش ماهه',2)]
PERSIAN_DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')
STEPS={
 'birth_year':{'label':'سال تولد','title':'سال تولد','field':'birth_year','options':YEARS},
 'contract_duration':{'label':'مدت قرارداد','title':'مدت قرارداد','field':'contract_duration','options':list(range(5,31)),'labels':[f'{year} ساله' for year in range(5,31)]},
 'premium_installment_num':{'label':'نحوه پرداخت بیمه عمر','title':'نحوه پرداخت بیمه عمر','field':'premium_installment_num','options':[1,4,2],'labels':['سالانه','سه ماهه','شش ماهه']},
 'premium':{'label':'توان پرداخت در هر سال','title':'توان پرداخت در هر سال','field':'premium','input_type':'text','min':1,'max':100000000,'placeholder':'مثلاً ۱٬۲۰۰٬۰۰۰'},
 'premium_increase_rate':{'label':'افزایش سالانه حق بیمه','title':'افزایش سالانه حق بیمه','field':'premium_increase_rate','options':[0,.05,.1,.15,.2,.25],'labels':['افزایش 0 درصد','افزایش 5 درصد','افزایش 10 درصد','افزایش 15 درصد','افزایش 20 درصد','افزایش 25 درصد']},
 'death_benefit_ratio':{'label':'دریافتی ذی‌نفعان پس از فوت احتمالی در سال اول','title':'دریافتی ذی‌نفعان پس از فوت احتمالی در سال اول','field':'death_benefit_ratio','options':list(range(5,36)),'labels':[f'{ratio} (برابر حق بیمه)' for ratio in range(5,36)]},
 'annual_death_benefit_growth':{'label':'افزایش سالانه سرمایه فوت','title':'افزایش سالانه سرمایه فوت','field':'annual_death_benefit_growth','options':[0,.05,.1],'labels':['افزایش 0 درصد','افزایش 5 درصد','افزایش 10 درصد']},
}
def spec(step,answers=None):
 s=STEPS['premium' if step in ('premium_six','premium_three') else step].copy(); answers=answers or {}
 if step in ('premium','premium_six','premium_three'):
  s['field']='premium'; s['input_type']='text'; s['min']=1; s['max']=100000000
  s['label']={'premium':'توان پرداخت در هر سال','premium_six':'توان پرداخت در هر شش ماه','premium_three':'توان پرداخت در هر سه ماه'}[step]; s['title']=s['label']
 return s
def active_steps(answers):
 result=ORDER.copy(); pay=answers.get('premium_installment_num')
 if pay==2: result[result.index('premium')]='premium_six'
 elif pay==4: result[result.index('premium')]='premium_three'
 return result
def collect(request,step,answers):
 s=spec(step,answers); raw=request.POST.get(s['field'],'').strip()
 if s.get('field') == 'premium':
  normalized = raw.translate(PERSIAN_DIGITS).replace(',', '').replace('٬', '').replace('،', '').strip()
  if not normalized.isdecimal():
   return None
  value = int(normalized)
  return value if s['min'] <= value <= s['max'] else None
 try: value=float(raw) if '.' in raw else int(raw)
 except ValueError: return None
 return value if value in s.get('options',[]) else None
