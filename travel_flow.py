SESSION_KEY = 'travel_quote'
TITLE = 'بیمه مسافرتی'
COUNTRIES = ['آذربایجان','آرژانتین','آفریقای جنوبی','آلمان','آمریکا','آلبانی','امارات متحده عربی','ارمنستان','استرالیا','افغانستان','انگلستان','اندونزی','ایتالیا','اسپانیا','اتریش','بلژیک','بلغارستان','تاجیکستان','ترکیه','چین','دانمارک','روسیه','سوئیس','عراق','فرانسه','قطر','کانادا','کره جنوبی','گرجستان','مالزی','مصر','هلند','هند','یونان','ژاپن']
AGES = [('u12_persons','از ۰ تا ۱۲ سال'),('u65_persons','از ۱۳ تا ۶۵ سال'),('u70_persons','از ۶۶ تا ۷۰ سال'),('u75_persons','از ۷۱ تا ۷۵ سال'),('u80_persons','از ۷۶ تا ۸۰ سال'),('u85_persons','از ۸۱ تا ۸۵ سال'),('u100_persons','از ۸۶ تا ۱۰۰ سال'),('others_persons','بالای ۱۰۰ سال')]
DURATIONS = [('7','۱ الی ۷ روز'),('15','۷ الی ۱۵ روز'),('23','۱۵ الی ۲۳ روز'),('31','۲۳ الی ۳۱ روز'),('45','۳۱ الی ۴۵ روز'),('62','۴۵ الی ۶۲ روز'),('92','۶۲ الی ۹۲ روز'),('180','۹۲ الی ۱۸۰ روز'),('365','۱۸۰ الی ۳۶۵ روز')]
STEPS = ['country','persons','duration']
def spec(step):
    if step == 'country': return {'label':'کشور یا کشورهای مقصد','title':'کشور یا کشورهای مقصد','field':'country','options':COUNTRIES}
    if step == 'persons': return {'label':'تعداد افراد','title':'تعداد افراد','fields':[{'field':k,'label':v,'input_type':'number','min':0,'max':99} for k,v in AGES]}
    return {'label':'مدت سفر','title':'مدت سفر','field':'duration','options':[v for _,v in DURATIONS]}
def collect(request, step):
    s=spec(step)
    if step == 'persons':
        result={}
        for f in s['fields']:
            value=request.POST.get(f['field'],'0').strip()
            if not value.isdigit() or int(value)>99: return None
            result[f['field']]=value
        return result if any(int(v) for v in result.values()) else None
    value=request.POST.get(s['field'],'').strip()
    if step == 'country':
        selected=[item.strip() for item in value.split(',') if item.strip()]
        if not selected or any(item not in COUNTRIES for item in selected): return None
        return ','.join(dict.fromkeys(selected))
    return value or None
