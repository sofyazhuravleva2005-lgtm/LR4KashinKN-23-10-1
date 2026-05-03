import os
import random
from django.test import TestCase, override_settings
from .views import run_pdp_simulation

class PDPContainerTests(TestCase):
                            """Модульные тесты для ПДП-Контейнера"""

                            def setUp(self):
                                os.environ['IMP_S1_KASHIN'] = 'testkey1'
                                os.environ['IMP_S2_KASHIN'] = 'testkey2'
                                os.environ['IMP_S3_KASHIN'] = 'testkey3'
                                # Сбрасываем THRESHOLD, чтобы тесты с дефолтным порогом работали корректно
                                if 'THRESHOLD' in os.environ:
                                    del os.environ['THRESHOLD']
                                random.seed(42)

                            def test_risk_calculation(self):
                                """Проверка правильности вычисления риска и решений"""
                                data = run_pdp_simulation()
                                self.assertEqual(data['total_requests'], 16)
                                self.assertGreater(data['blocked'], 0)
                                self.assertGreater(data['allowed'], 0)

                            def test_threshold_boundary_zero(self):
                                """Проверка, что при пороге 0 все запросы блокируются"""
                                os.environ['THRESHOLD'] = '0'
                                data = run_pdp_simulation()
                                self.assertEqual(data['blocked'], 16)
                                self.assertEqual(data['allowed'], 0)

                            def test_threshold_boundary_high(self):
                                """Проверка, что при очень высоком пороге все запросы разрешены"""
                                os.environ['THRESHOLD'] = '200'
                                data = run_pdp_simulation()
                                self.assertEqual(data['allowed'], 16)
                                self.assertEqual(data['blocked'], 0)

                            def test_secrets_loading(self):
                                """Проверка чтения секретных ключей"""
                                data = run_pdp_simulation()
                                self.assertEqual(data['secrets']['s1'], 'testkey1')
                                self.assertEqual(data['secrets']['s2'], 'testkey2')
                                self.assertEqual(data['secrets']['s3'], 'testkey3')

                            def test_chart_generation(self):
                                """Проверка создания графиков (без реальной записи на диск)"""
                                data = run_pdp_simulation()
                                paths = data['chart_paths']
                                self.assertIn('bar', paths)
                                self.assertIn('pie', paths)
                                self.assertIn('line', paths)

                            def tearDown(self):
                                for var in ['IMP_S1_KASHIN', 'IMP_S2_KASHIN', 'IMP_S3_KASHIN', 'THRESHOLD']:
                                    if var in os.environ:
                                        del os.environ[var]

class HTTPSTests(TestCase):
                            """Тесты для проверки работы ПДП-Контейнера с HTTPS"""

                            def setUp(self):
                                os.environ['IMP_S1_KASHIN'] = 'testkey1'
                                os.environ['IMP_S2_KASHIN'] = 'testkey2'
                                os.environ['IMP_S3_KASHIN'] = 'testkey3'
                                random.seed(42)

                            @override_settings(SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'))
                            def test_https_request_simulation(self):
                                """Проверка, что страница отдаётся с HTTPS-заголовком"""
                                response = self.client.get('/', HTTP_X_FORWARDED_PROTO='https')
                                self.assertEqual(response.status_code, 200)
                                self.assertContains(response, 'ПДП-Контейнер')

                            def test_direct_http_still_works(self):
                                """Проверка обратной совместимости"""
                                response = self.client.get('/')
                                self.assertEqual(response.status_code, 200)

                            def test_risk_calculation_via_https(self):
                                """Проверка, что расчёт риска работает при HTTPS-заголовке"""
                                response = self.client.get('/', HTTP_X_FORWARDED_PROTO='https')
                                self.assertContains(response, 'Заблокировано')
                                self.assertContains(response, 'Разрешено')