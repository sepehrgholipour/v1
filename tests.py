from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from . import life_flow
from . import medical_liability_flow
from . import supplemental_flow


@override_settings(ALLOWED_HOSTS=['localhost', 'testserver'])
class QuoteFlowTests(TestCase):
    """Regression coverage for the shared quote journeys, theming and branding."""

    def client_for_flow(self):
        return Client(HTTP_HOST='localhost')

    def lookup_data(self):
        return {
            'plate_left': '12',
            'plate_letter': 'الف',
            'plate_middle': '345',
            'plate_city': '63',
            'national_code': '1234567890',
        }

    def history_data(self):
        return {
            'policy_status': 'دارم',
            'expiry_date': 'تا ۳۰ روز آینده',
            'discount_years': '۱ تا ۳ سال',
        }

    def owner_data(self):
        return {
            'full_name': 'کاربر آزمایشی',
            'national_code': '1234567890',
            'mobile': '09121234567',
        }

    def test_home_links_to_both_quote_flows(self):
        response = self.client_for_flow().get(reverse('home'))
        self.assertContains(response, reverse('third_party_lookup'))
        self.assertContains(response, reverse('body_lookup'))

    def test_home_lists_the_new_engineering_insurances(self):
        response = self.client_for_flow().get(reverse('home'))
        for insurance, icon in (('بیمه تجهیزات الکترونیکی', 'electronics'), ('بیمه مسئولیت پزشکان و پیراپزشکان', 'liability'), ('بیمه آسانسور', 'elevator')):
            with self.subTest(insurance=insurance):
                self.assertContains(response, f'<strong>{insurance}</strong>')
                self.assertContains(response, f'data-insurance="{insurance}"')
                self.assertContains(response, f'<symbol id="{icon}"')
                self.assertContains(response, f'href="#{icon}"')

    def test_lookup_back_keeps_plate_and_returns_to_lookup_for_both_flows(self):
        for kind in ('third_party', 'body'):
            with self.subTest(kind=kind):
                client = self.client_for_flow()
                lookup_url = reverse(f'{kind}_lookup')
                history_url = reverse(f'{kind}_history')
                response = client.post(lookup_url, self.lookup_data())
                self.assertRedirects(response, history_url)

                history = client.get(history_url)
                self.assertContains(history, f'href="{lookup_url}"')

                lookup = client.get(lookup_url)
                self.assertContains(lookup, 'value="12"')
                self.assertContains(lookup, 'value="345"')
                self.assertContains(lookup, 'value="63"')

    def test_manual_back_returns_to_manual_vehicle_entry_for_both_flows(self):
        for kind in ('third_party', 'body'):
            with self.subTest(kind=kind):
                client = self.client_for_flow()
                vehicle_url = reverse(f'{kind}_vehicle')
                details_url = reverse(f'{kind}_vehicle_details')
                history_url = reverse(f'{kind}_history')
                response = client.post(vehicle_url, {'vehicle_type': 'سواری'})
                self.assertRedirects(response, details_url)
                self.assertEqual(client.get(details_url).status_code, 200)
                response = client.post(details_url, {
                    'vehicle_usage': 'شخصی',
                    'cylinder_count': '۴ سیلندر',
                    'vehicle_year': '۱۳۹۵ تا ۱۴۰۳',
                })
                self.assertRedirects(response, history_url)
                self.assertContains(client.get(history_url), f'href="{vehicle_url}"')

    def test_complete_lookup_flow_for_third_party_and_body(self):
        for kind, title in (('third_party', 'بیمه شخص ثالث'), ('body', 'بیمه بدنه')):
            with self.subTest(kind=kind):
                client = self.client_for_flow()
                self.assertRedirects(client.post(reverse(f'{kind}_lookup'), self.lookup_data()), reverse(f'{kind}_history'))
                self.assertRedirects(client.post(reverse(f'{kind}_history'), self.history_data()), reverse(f'{kind}_history_dates'))
                self.assertRedirects(client.post(reverse(f'{kind}_history_dates'), {
                    'previous_start_date': '2025-01-01',
                    'expiry_date': '2026-01-01',
                }), reverse(f'{kind}_owner'))
                self.assertRedirects(client.post(reverse(f'{kind}_owner'), self.owner_data()), reverse(f'{kind}_result'))
                self.assertContains(client.get(reverse(f'{kind}_result')), title)

    def test_flows_keep_separate_session_data_and_guard_skipped_steps(self):
        client = self.client_for_flow()
        self.assertRedirects(client.get(reverse('body_history')), reverse('body_lookup'))
        self.assertRedirects(client.get(reverse('third_party_owner')), reverse('third_party_history'), fetch_redirect_response=False)

        client.post(reverse('third_party_lookup'), self.lookup_data())
        self.assertRedirects(client.get(reverse('body_history')), reverse('body_lookup'))

    def test_manual_vehicle_uses_only_the_selected_vehicle_type(self):
        client = self.client_for_flow()
        invalid = {
            'vehicle_type': 'سواری',
            'brand': 'ایران خودرو',
            'model': 'مدل ساختگی',
            'year': '1403',
        }
        response = client.post(reverse('third_party_vehicle'), invalid)
        self.assertRedirects(response, reverse('third_party_vehicle_details'))
        self.assertEqual(client.session['third_party_quote']['vehicle_type'], 'سواری')
        self.assertNotIn('brand', client.session['third_party_quote'])

    def completed_flow(self, kind):
        client = self.client_for_flow()
        client.post(reverse(f'{kind}_lookup'), self.lookup_data())
        client.post(reverse(f'{kind}_history'), self.history_data())
        client.post(reverse(f'{kind}_owner'), self.owner_data())
        return client, (
            reverse('home'),
            reverse(f'{kind}_lookup'),
            reverse(f'{kind}_vehicle'),
            reverse(f'{kind}_history'),
            reverse(f'{kind}_owner'),
            reverse(f'{kind}_result'),
        )

    def test_every_page_applies_the_shared_theme(self):
        for kind in ('third_party', 'body'):
            with self.subTest(kind=kind):
                client, pages = self.completed_flow(kind)
                for url in pages:
                    with self.subTest(url=url):
                        response = client.get(url)
                        self.assertEqual(response.status_code, 200)
                        self.assertContains(response, "localStorage.getItem('bimepro-theme')")
                        self.assertContains(response, 'class="theme-toggle"')
                        self.assertContains(response, 'js/theme.js')

    def test_every_page_renders_the_recreated_brand_logo(self):
        for kind in ('third_party', 'body'):
            with self.subTest(kind=kind):
                client, pages = self.completed_flow(kind)
                for url in pages:
                    with self.subTest(url=url):
                        response = client.get(url)
                        self.assertContains(response, 'class="logo-mark"')
                        self.assertContains(response, 'fill="var(--accent-strong)"')
                        self.assertContains(response, 'stroke="var(--mint)"')
                        self.assertContains(response, '<b>بیمه</b><i>&#8204;پرو</i>')

    def test_stylesheet_and_theme_script_share_one_theme_hook(self):
        style = (settings.BASE_DIR / 'Pages' / 'static' / 'css' / 'style.css').read_text(encoding='utf-8')
        script = (settings.BASE_DIR / 'Pages' / 'static' / 'js' / 'theme.js').read_text(encoding='utf-8')
        self.assertIn('html.light', style)
        self.assertNotIn('body.light', style)
        self.assertIn("document.documentElement.classList.toggle(THEME_CLASS", script)
        self.assertIn("const THEME_KEY = 'bimepro-theme'", script)

    def test_brand_palette_uses_discord_indigo_without_previous_yellow_accents(self):
        style = (settings.BASE_DIR / 'Pages' / 'static' / 'css' / 'style.css').read_text(encoding='utf-8')
        for gold in ('#d6a700', '#ffd052', '#b58900', '#c99800', '#a77f00', '#b48600', '#ffe07c', '#6b550a', '#987100', '#8c6800', '#fff0c2', '#faf0d2', '#f5ebd0', '#805f00', '#fff6d6'):
            self.assertNotIn(gold, style)
        self.assertIn('#5865f2', style)
        self.assertIn('#0a0d3a', style)
        self.assertIn('#1e2353', style)


@override_settings(ALLOWED_HOSTS=['localhost', 'testserver'])
class SupplementalWizardTests(TestCase):
    def test_individual_count_is_a_one_to_twenty_person_picker_with_numeric_values(self):
        client = Client(HTTP_HOST='localhost')
        client.post(reverse('supplemental_type'), {'insurance_type': 'انفرادی'})
        response = client.get(reverse('supplemental_count'))
        self.assertContains(response, 'value="1"')
        self.assertContains(response, '>1 نفر<')
        self.assertContains(response, 'value="20"')
        self.assertContains(response, '>20 نفر<')
        self.assertContains(response, 'person-count-picker')
        self.assertRedirects(client.post(reverse('supplemental_count'), {'number_of_person': '2'}), reverse('supplemental_dynamic', kwargs={'step': 'person_1'}))
        self.assertEqual(client.session[supplemental_flow.SESSION_KEY]['number_of_person'], '2')

    def test_individual_and_family_collect_each_person_before_contact_details(self):
        client = Client(HTTP_HOST='localhost')
        client.post(reverse('supplemental_type'), {'insurance_type': 'خانوادگی'})
        client.post(reverse('supplemental_count'), {'number_of_person': '2'})

        guardian = client.get(reverse('supplemental_dynamic', kwargs={'step': 'person_1'}))
        self.assertContains(guardian, 'اطلاعات سرپرست')
        response = client.post(reverse('supplemental_dynamic', kwargs={'step': 'person_1'}), {
            'age_range_1': 'از ۱۶ تا ۴۵ سال', 'base_insurance_1': 'فاقد بیمه‌گر پایه', 'chronic_illness_1': 'ندارم',
        })
        self.assertRedirects(response, reverse('supplemental_dynamic', kwargs={'step': 'person_2'}))
        response = client.post(reverse('supplemental_dynamic', kwargs={'step': 'person_2'}), {
            'age_range_2': 'از ۰ تا ۱۵ سال', 'base_insurance_2': 'فاقد بیمه‌گر پایه', 'chronic_illness_2': 'ندارم',
        })
        self.assertRedirects(response, reverse('supplemental_dynamic', kwargs={'step': 'mobile'}))

    def test_family_and_organisation_use_their_respective_count_rules(self):
        client = Client(HTTP_HOST='localhost')
        client.post(reverse('supplemental_type'), {'insurance_type': 'خانوادگی'})
        family = client.get(reverse('supplemental_count'))
        self.assertContains(family, 'value="2"')
        self.assertContains(family, '>15 نفر<')
        self.assertNotContains(family, 'value="1"')

        client = Client(HTTP_HOST='localhost')
        client.post(reverse('supplemental_type'), {'insurance_type': 'سازمانی'})
        organisation = client.get(reverse('supplemental_count'))
        self.assertContains(organisation, 'min="10"')
        self.assertContains(organisation, '>نفر<')
        self.assertEqual(client.post(reverse('supplemental_count'), {'number_of_person': '9'}).status_code, 400)

    def test_organisation_company_name_is_plain_text_without_currency_unit(self):
        client = Client(HTTP_HOST='localhost')
        client.post(reverse('supplemental_type'), {'insurance_type': supplemental_flow.TYPE_OPTIONS[2]})
        client.post(reverse('supplemental_count'), {'number_of_person': '10'})

        response = client.get(reverse('supplemental_dynamic', kwargs={'step': 'company_name'}))

        self.assertContains(response, 'name="company_name" type="text"')
        self.assertNotContains(response, 'name="company_name" type="text" inputmode="numeric"')
        self.assertNotContains(response, 'company_name-unit')


@override_settings(ALLOWED_HOSTS=['localhost', 'testserver'])
class MedicalLiabilityWizardTests(TestCase):
    def setUp(self):
        medical_liability_flow._forms = dict(medical_liability_flow.FALLBACK)

    def submit(self, client, step, data):
        return client.post(reverse('medical_liability_field', kwargs={'step': step}), data)

    def test_doctor_flow_includes_its_own_specialty_and_optional_coverages(self):
        client = Client(HTTP_HOST='localhost')
        self.assertContains(client.get(reverse('medical_liability_type')), 'مسئولیت پزشکان')
        self.assertRedirects(client.post(reverse('medical_liability_type'), {'applicant_type': 'مسئولیت پزشکان'}), reverse('medical_liability_field', kwargs={'step': 'coverage_details'}))
        details = client.get(reverse('medical_liability_field', kwargs={'step': 'coverage_details'}))
        self.assertContains(details, 'پزشک عمومی')
        self.assertContains(details, 'متخصص قلب و عروق')
        self.assertContains(details, 'name="TedadDieDarkhasty_doc"')
        self.assertContains(details, 'name="AfzayeshMablaghRiyali"')
        self.assertContains(details, 'name="extraDr"')
        self.assertEqual(details.content.count(b'medical-option-list'), 4)
        response = self.submit(client, 'coverage_details', {
            'doctorSpecial': 'پزشک عمومی',
            'TedadDieDarkhasty_doc': 'یک دیه',
            'AfzayeshMablaghRiyali': 'فاقد پوشش',
            'extraDr': ['مسئولیت رزیدنت', 'پرداخت بدون اعمال تعرفه'],
        })
        self.assertRedirects(response, reverse('medical_liability_field', kwargs={'step': 'AdamKhesaratPezeshkan'}))
        next_step = self.submit(client, 'AdamKhesaratPezeshkan', {'AdamKhesaratPezeshkan': 'با خسارت'})
        self.assertRedirects(next_step, reverse('medical_liability_field', kwargs={'step': 'EndTime'}))

    def test_paramedical_flow_uses_its_own_fields_and_skips_prior_policy_date_for_first_issue(self):
        client = Client(HTTP_HOST='localhost')
        client.post(reverse('medical_liability_type'), {'applicant_type': 'مسئولیت پیراپزشکان'})
        specialty_page = client.get(reverse('medical_liability_field', kwargs={'step': 'coverage_details'}))
        self.assertContains(specialty_page, 'medical-option-list')
        self.assertContains(specialty_page, 'فیزیوتراپی')
        self.assertContains(specialty_page, 'name="TedadDieDarkhasty_doc"')
        self.assertRedirects(self.submit(client, 'coverage_details', {
            'PirapezeskanList': 'کارشناس پرستاری',
            'TedadDieDarkhasty_doc': 'یک دیه',
            'AfzayeshMablaghRiyali': 'فاقد پوشش',
            'extra_pirapezeshk': ['دانشجو هستم'],
        }), reverse('medical_liability_field', kwargs={'step': 'AdamKhesaratPezeshkan'}))
        next_step = self.submit(client, 'AdamKhesaratPezeshkan', {'AdamKhesaratPezeshkan': 'صدور اولیه'})
        self.assertRedirects(next_step, reverse('medical_liability_field', kwargs={'step': 'Modat_BimeName_Oezeshkan'}))


@override_settings(ALLOWED_HOSTS=['localhost', 'testserver'])
class TravelWizardTests(TestCase):
    def test_searchable_country_and_step_submissions_complete_the_travel_flow(self):
        client = Client(HTTP_HOST='localhost')
        country_page = client.get(reverse('travel_country'))
        self.assertContains(country_page, 'type="search"')
        self.assertContains(country_page, 'travel-destination')
        self.assertContains(country_page, 'آلمان')

        invalid_country = client.post(reverse('travel_country'), {'country': 'نیوزیلند'})
        self.assertEqual(invalid_country.status_code, 400)

        self.assertRedirects(client.post(reverse('travel_country'), {'country': 'آمریکا'}), reverse('travel_persons'))
        self.assertRedirects(client.post(reverse('travel_persons'), {
            'u12_persons': '1',
            'u65_persons': '1',
            'u70_persons': '0',
            'u75_persons': '0',
            'u80_persons': '0',
            'u85_persons': '0',
            'u100_persons': '0',
            'others_persons': '0',
        }), reverse('travel_duration'))
        self.assertRedirects(client.post(reverse('travel_duration'), {'duration': '۱ الی ۷ روز'}), reverse('travel_result'))
        self.assertEqual(client.session['travel_quote']['country'], 'آمریکا')
        self.assertEqual(client.get(reverse('travel_result')).status_code, 200)


@override_settings(ALLOWED_HOSTS=['localhost', 'testserver'])
class LifeWizardTests(TestCase):
    def test_life_steps_six_and_seven_are_in_the_requested_order(self):
        self.assertEqual(
            life_flow.ORDER[-2:],
            ['annual_death_benefit_growth', 'death_benefit_ratio'],
        )

    def test_death_benefit_options_explain_their_premium_multiple(self):
        spec = life_flow.spec('death_benefit_ratio')
        self.assertEqual(spec['labels'][0], '5 (برابر حق بیمه)')
        self.assertEqual(spec['labels'][-1], '35 (برابر حق بیمه)')

    def test_six_month_premium_submits_to_the_next_step(self):
        client = Client(HTTP_HOST='localhost')
        session = client.session
        session['life_quote'] = {
            'birth_year': 1370,
            'contract_duration': 10,
            'premium_installment_num': 2,
        }
        session.save()

        premium_url = reverse('life_field', kwargs={'step': 'premium_six'})
        response = client.get(premium_url)
        self.assertContains(response, 'name="premium"')

        response = client.post(premium_url, {'premium': '5000000'})
        self.assertRedirects(
            response,
            reverse('life_field', kwargs={'step': 'premium_increase_rate'}),
        )
        self.assertEqual(client.session['life_quote']['premium'], 5000000)

    def test_non_annual_payment_sessions_render_the_life_flow(self):
        client = Client(HTTP_HOST='localhost')
        for payment, premium_step in ((2, 'premium_six'), (4, 'premium_three')):
            with self.subTest(payment=payment):
                session = client.session
                session['life_quote'] = {
                    'birth_year': 1370,
                    'contract_duration': 10,
                    'premium_installment_num': payment,
                }
                session.save()

                first_page = client.get(reverse('life_birth_year'))
                self.assertEqual(first_page.status_code, 200)
                self.assertContains(first_page, 'توان پرداخت')

                premium_page = client.get(reverse('life_field', kwargs={'step': premium_step}))
                self.assertEqual(premium_page.status_code, 200)
                self.assertContains(premium_page, 'توان پرداخت')


@override_settings(ALLOWED_HOSTS=['localhost', 'testserver'])
class MotorcycleWizardTests(TestCase):
    """The motorcycle journey walks the bike itself instead of the plate."""

    def client_for_flow(self):
        return Client(HTTP_HOST='localhost')

    def start(self, client, model='تک سیلندر'):
        return client.post(reverse('motorcycle_model'), {'model': model})

    def to_policy_step(self, client, policy_status='دارم'):
        self.start(client)
        client.post(reverse('motorcycle_year'), {'year': '1400'})
        return client.post(reverse('motorcycle_policy_status'), {'policy_status': policy_status})

    def test_home_card_opens_the_motorcycle_wizard(self):
        response = self.client_for_flow().get(reverse('home'))
        self.assertContains(response, reverse('motorcycle_model'))
        self.assertNotContains(response, 'data-insurance="بیمه موتورسیکلت"')

    def test_first_step_asks_for_the_model_instead_of_a_plate(self):
        response = self.client_for_flow().get(reverse('motorcycle_model'))
        self.assertContains(response, 'مدل موتورسیکلت')
        for model in ('برقی', 'تک سیلندر', 'دو سیلندر و بیش از دو سیلندر', 'سه چرخ'):
            self.assertContains(response, f'value="{model}"')
        self.assertNotContains(response, 'iran-plate')
        self.assertNotContains(response, 'شماره پلاک')
        self.assertNotContains(response, 'کد ملی')

    def test_wizard_walks_the_renewal_branch_to_the_quote(self):
        client = self.client_for_flow()
        self.assertRedirects(self.start(client), reverse('motorcycle_year'))
        self.assertRedirects(client.post(reverse('motorcycle_year'), {'year': '1400'}), reverse('motorcycle_policy_status'))
        self.assertRedirects(self.to_policy_step(client), reverse('motorcycle_previous_policy'))

        response = client.post(reverse('motorcycle_previous_policy'), {
            'previous_company': 'ایران',
            'policy_start_date': 'بیش از ۱ سال گذشته',
            'policy_end_date': 'منقضی شده',
        })
        self.assertRedirects(response, reverse('motorcycle_plate_change'))
        self.assertRedirects(client.post(reverse('motorcycle_plate_change'), {'plate_changed': 'بله'}), reverse('motorcycle_discount_source'))
        self.assertRedirects(client.post(reverse('motorcycle_discount_source'), {'discount_source': 'با پلاک دیگر'}), reverse('motorcycle_discount'))
        self.assertRedirects(client.post(reverse('motorcycle_discount'), {
            'third_party_discount': '۲۰٪',
            'driver_discount': '۲۰٪',
            'has_damage': 'بله',
            'property_damage_count': 'یک',
            'life_damage_count': 'بدون خسارت',
            'driver_damage_count': 'یک',
        }), reverse('motorcycle_coverage'))
        self.assertRedirects(client.post(reverse('motorcycle_coverage'), {
            'financial_coverage': '۷۰ میلیون تومان',
            'policy_term': 'یک‌ساله',
        }), reverse('motorcycle_contact'))
        self.assertRedirects(client.post(reverse('motorcycle_contact'), {
            'full_name': 'کاربر آزمایشی',
            'national_code': '1234567890',
            'mobile': '09121234567',
        }), reverse('motorcycle_result'))

        result = client.get(reverse('motorcycle_result'))
        self.assertContains(result, 'بیمه شخص ثالث موتورسیکلت')
        self.assertContains(result, 'تک سیلندر · سال 1400')
        self.assertContains(result, 'ایران · منقضی شده')
        self.assertContains(result, '۷۰ میلیون تومان · یک‌ساله')

    def test_wizard_skips_the_policy_history_for_a_new_motorcycle(self):
        client = self.client_for_flow()
        self.assertRedirects(self.to_policy_step(client, 'ندارم'), reverse('motorcycle_coverage'))

        coverage = client.get(reverse('motorcycle_coverage'))
        self.assertContains(coverage, 'مرحله 4 از 5')
        self.assertNotContains(coverage, 'تعویض پلاک')
        self.assertRedirects(client.get(reverse('motorcycle_previous_policy')), reverse('motorcycle_coverage'), fetch_redirect_response=False)
        self.assertRedirects(client.get(reverse('motorcycle_plate_change')), reverse('motorcycle_coverage'), fetch_redirect_response=False)

        self.assertRedirects(client.post(reverse('motorcycle_coverage'), {
            'financial_coverage': '۱۴ میلیارد تومان',
            'policy_term': '۶ ماهه',
        }), reverse('motorcycle_contact'))
        result = client.get(reverse('motorcycle_result'))
        self.assertRedirects(result, reverse('motorcycle_contact'), fetch_redirect_response=False)

    def to_discount_step(self, client):
        self.to_policy_step(client)
        client.post(reverse('motorcycle_previous_policy'), {
            'previous_company': 'سامان',
            'policy_start_date': 'بیش از ۱ سال گذشته',
            'policy_end_date': 'بیش از ۳۰ روز',
        })
        client.post(reverse('motorcycle_plate_change'), {'plate_changed': 'خیر'})
        return client

    def test_damage_counts_are_only_asked_after_a_claim(self):
        without_claim = self.to_discount_step(self.client_for_flow()).post(reverse('motorcycle_discount'), {
            'third_party_discount': '۳۰٪',
            'driver_discount': 'بدون تخفیف',
            'has_damage': 'خیر',
        })
        self.assertRedirects(without_claim, reverse('motorcycle_coverage'))

        incomplete = self.to_discount_step(self.client_for_flow()).post(reverse('motorcycle_discount'), {
            'third_party_discount': '۳۰٪',
            'driver_discount': 'بدون تخفیف',
            'has_damage': 'بله',
        })
        self.assertEqual(incomplete.status_code, 400)
        self.assertContains(incomplete, 'گزینه‌های انتخاب‌شده معتبر نیست', status_code=400)

    def test_wizard_rejects_an_answer_outside_the_offered_options(self):
        client = self.client_for_flow()
        response = client.post(reverse('motorcycle_model'), {'model': 'پژو ۲۰۶'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(client.session.get('motorcycle_quote'), None)

        year = self.client_for_flow()
        self.start(year)
        self.assertEqual(year.post(reverse('motorcycle_year'), {'year': '1300'}).status_code, 400)

    def test_every_wizard_page_keeps_the_theme_and_the_logo(self):
        client = self.client_for_flow()
        pages = [reverse('motorcycle_model')]
        self.to_policy_step(client)
        pages.append(reverse('motorcycle_previous_policy'))
        client.post(reverse('motorcycle_previous_policy'), {
            'previous_company': 'سامان',
            'policy_start_date': 'بیش از ۱ سال گذشته',
            'policy_end_date': 'بیش از ۳۰ روز',
        })
        pages.append(reverse('motorcycle_plate_change'))
        client.post(reverse('motorcycle_plate_change'), {'plate_changed': 'بله'})
        pages.append(reverse('motorcycle_discount_source'))
        client.post(reverse('motorcycle_discount_source'), {'discount_source': 'با همین پلاک'})
        pages.append(reverse('motorcycle_discount'))
        client.post(reverse('motorcycle_discount'), {
            'third_party_discount': '۱۰٪',
            'driver_discount': '۱۰٪',
            'has_damage': 'خیر',
        })
        pages.append(reverse('motorcycle_coverage'))
        client.post(reverse('motorcycle_coverage'), {
            'financial_coverage': '۳ میلیارد تومان',
            'policy_term': '۹ ماهه',
        })
        pages += [reverse('motorcycle_contact'), reverse('motorcycle_result')]
        client.post(reverse('motorcycle_contact'), {
            'full_name': 'کاربر آزمایشی',
            'mobile': '09121234567',
        })

        for url in pages:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "localStorage.getItem('bimepro-theme')")
                self.assertContains(response, 'class="logo-mark"')
                self.assertContains(response, 'class="wizard-progress"')


@override_settings(ALLOWED_HOSTS=['localhost', 'testserver'])
class PropertyInsuranceWizardTests(TestCase):
    def client_for_flow(self):
        return Client(HTTP_HOST='localhost')

    def test_elevator_flow_has_its_own_copy_and_preserves_a_previous_answer(self):
        client = self.client_for_flow()
        first = client.get(reverse('elevator_usage'))
        self.assertContains(first, 'مشخصات آسانسور را وارد کنید')
        self.assertNotContains(first, 'مشخصات ساختمان را وارد کنید')
        self.assertRedirects(client.post(reverse('elevator_usage'), {'usage': 'مسکونی'}), reverse('elevator_capacity'))
        previous = client.get(reverse('elevator_usage'))
        self.assertContains(previous, 'value="مسکونی" checked')

    def test_fire_flow_has_its_own_copy_and_result_page_context(self):
        client = self.client_for_flow()
        first = client.get(reverse('fire_usage'))
        self.assertContains(first, 'مشخصات ساختمان را وارد کنید')
        self.assertNotContains(first, 'مشخصات آسانسور را وارد کنید')
        answers = {
            'usage': 'مسکونی', 'property_type': 'آپارتمان', 'units': 'یک واحد',
            'structure': 'بتنی', 'age': 'کمتر از ۵ سال', 'area': '120',
            'insured_item': 'بنا و لوازم', 'building_value': 'تا ۱۵ میلیون تومان',
            'contents_value': 'تا ۵۰۰ میلیون تومان', 'coverage': 'آتش‌سوزی به‌همراه زلزله',
        }
        for route, field in (
            ('fire_usage', 'usage'), ('fire_property_type', 'property_type'), ('fire_units', 'units'),
            ('fire_structure', 'structure'), ('fire_age', 'age'), ('fire_area', 'area'),
            ('fire_insured_item', 'insured_item'), ('fire_building_value', 'building_value'),
            ('fire_contents_value', 'contents_value'), ('fire_coverage', 'coverage'),
        ):
            client.post(reverse(route), {field: answers[field]})
        result = client.get(reverse('fire_result'))
        self.assertContains(result, 'مشخصات ساختمان ثبت شده')
        self.assertContains(result, 'مرحله 10 از 10')


@override_settings(ALLOWED_HOSTS=['localhost', 'testserver'])
class LifeInsuranceWizardTests(TestCase):
    def client_for_premium_step(self):
        client = Client(HTTP_HOST='localhost')
        session = client.session
        session['life_quote'] = {
            'birth_year': 1370,
            'contract_duration': 10,
            'premium_installment_num': 1,
        }
        session.save()
        return client

    def test_premium_step_uses_positive_toman_amount_input(self):
        response = self.client_for_premium_step().get(reverse('life_field', kwargs={'step': 'premium'}))

        self.assertContains(response, 'name="premium"')
        self.assertContains(response, 'type="text"')
        self.assertContains(response, 'inputmode="numeric"')
        self.assertContains(response, 'pattern="[0-9۰-۹٠-٩٬,،]+"')
        self.assertContains(response, '&#1578;&#1608;&#1605;&#1575;&#1606;')

    def test_premium_must_be_positive_integer_above_zero(self):
        for invalid in ('0', '-1', '1.5', '', '1e6', '+1000'):
            with self.subTest(value=invalid):
                response = self.client_for_premium_step().post(
                    reverse('life_field', kwargs={'step': 'premium'}),
                    {'premium': invalid},
                )
                self.assertEqual(response.status_code, 400)

    def test_premium_accepts_persian_digits_and_toman_separators(self):
        client = self.client_for_premium_step()
        response = client.post(
            reverse('life_field', kwargs={'step': 'premium'}),
            {'premium': '۱٬۲۰۰٬۰۰۰'},
        )

        self.assertRedirects(response, reverse('life_field', kwargs={'step': 'premium_increase_rate'}))
        self.assertEqual(client.session['life_quote']['premium'], 1200000)
