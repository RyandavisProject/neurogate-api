import unittest

from neurogate_usage_overlay.parser import parse_usage_text


class UsageParserTest(unittest.TestCase):
    def test_parse_usage_text_from_russian_page_copy(self):
        text = """
        Лимиты
        ascend
        МОДЕЛЬ
        Все модели
        ИСПОЛЬЗОВАНО
        1 718 659 626 токены
        Приблизительно осталось: 9 639 782 853
        24 часа · сброс 09:00 UTC
        Сброс через 14 ч 26 мин
        ТОКЕНЫ
        135 285 661
        КЕШ
        125 790 976
        ЛИМИТЫ ТАРИФА
        37 940 599 / 120 000 000
        7 дней
        Сброс через 2 д 10 ч
        ТОКЕНЫ
        985 751 421
        КЕШ
        923 269 248
        ЛИМИТЫ ТАРИФА
        249 659 909 / 600 000 000
        """

        snapshot = parse_usage_text(text)

        self.assertEqual(snapshot.account, "ascend")
        self.assertEqual(snapshot.model_group, "Все модели")
        self.assertEqual(snapshot.total_used, 1_718_659_626)
        self.assertEqual(snapshot.remaining, 9_639_782_853)
        self.assertEqual(len(snapshot.windows), 2)
        self.assertEqual(snapshot.windows[0].title, "24 часа")
        self.assertEqual(snapshot.windows[0].tokens, 135_285_661)
        self.assertEqual(snapshot.windows[0].cache, 125_790_976)
        self.assertEqual(snapshot.windows[0].limit_used, 37_940_599)
        self.assertEqual(snapshot.windows[0].limit_total, 120_000_000)
        self.assertEqual(snapshot.windows[1].title, "7 дней")
        self.assertEqual(snapshot.windows[1].tokens, 985_751_421)
        self.assertEqual(snapshot.windows[1].cache, 923_269_248)
        self.assertEqual(snapshot.windows[1].limit_used, 249_659_909)
        self.assertEqual(snapshot.windows[1].limit_total, 600_000_000)

    def test_parse_new_credit_limits_page(self):
        text = """
        КАБИНЕТ КЛИЕНТА
        Лимиты
        Подробная информация о Вашем тарифе
        ascend
        активен ещё 2 д 20 ч
        ПЛАТНЫЙ СБРОС
        30 USDT
        Сбрасывает: 7 дней, 5 часов. Месячный лимит сохраняется.
        5 часов
        Сброс через 4 ч 53 мин
        118 492 616
        Кредитов осталось
        7 дней
        Сброс через 1 д 20 ч
        331 363 335
        Кредитов осталось
        ИСТОРИЯ
        Последние списания
        """

        snapshot = parse_usage_text(text)

        self.assertEqual(snapshot.account, "ascend")
        self.assertIsNone(snapshot.model_group)
        self.assertEqual(snapshot.plan_status, "активен ещё 2 д 20 ч")
        self.assertEqual(len(snapshot.windows), 2)
        self.assertEqual(snapshot.windows[0].title, "5 часов")
        self.assertEqual(snapshot.windows[0].credits_remaining, 118_492_616)
        self.assertEqual(snapshot.windows[0].reset_text, "4 ч 53 мин")
        self.assertEqual(snapshot.windows[1].title, "7 дней")
        self.assertEqual(snapshot.windows[1].credits_remaining, 331_363_335)
        self.assertEqual(snapshot.windows[1].reset_text, "1 д 20 ч")

    def test_parse_dynamic_plan_name(self):
        text = """
        КАБИНЕТ КЛИЕНТА
        Лимиты
        Оплата
        Рефералы
        КАБИНЕТ КЛИЕНТА
        Лимиты
        Подробная информация о Вашем тарифе
        Обновить
        pro max
        активен ещё 10 д
        5 часов
        Сброс через 4 ч 56 мин
        118 755 192
        Кредитов осталось
        """

        snapshot = parse_usage_text(text)

        self.assertEqual(snapshot.account, "pro max")

    def test_parse_plan_name_skips_refresh_loading_state(self):
        text = """
        КАБИНЕТ КЛИЕНТА
        Лимиты
        Подробная информация о Вашем тарифе
        Обновление
        ascend
        активен ещё 29 д 2 ч
        5 часов
        109 292 654
        Кредитов осталось
        7 дней
        490 367 816
        Кредитов осталось
        """

        snapshot = parse_usage_text(text)

        self.assertEqual(snapshot.account, "ascend")

    def test_stale_cabinet_error_does_not_reuse_old_limit_cards(self):
        text = """
        КАБИНЕТ КЛИЕНТА
        Лимиты
        Подробная информация о Вашем тарифе
        Сессия больше недействительна.
        ascend
        активен ещё 28 д 8 ч
        5 часов
        117 888 444
        Кредитов осталось
        7 дней
        421 381 328
        Кредитов осталось
        """

        snapshot = parse_usage_text(text)

        self.assertFalse(snapshot.has_data)
        self.assertIsNone(snapshot.account)
        self.assertEqual(snapshot.status_note, "нужен вход")

    def test_cabinet_load_error_does_not_reuse_old_limit_cards(self):
        text = """
        КАБИНЕТ КЛИЕНТА
        Лимиты
        Подробная информация о Вашем тарифе
        Could not load cabinet data.
        ascend
        активен ещё 28 д 8 ч
        5 часов
        117 888 444
        Кредитов осталось
        7 дней
        421 381 328
        Кредитов осталось
        """

        snapshot = parse_usage_text(text)

        self.assertFalse(snapshot.has_data)
        self.assertIsNone(snapshot.account)
        self.assertEqual(snapshot.status_note, "нет данных")


if __name__ == "__main__":
    unittest.main()
