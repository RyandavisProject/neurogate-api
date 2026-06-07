import unittest

from neurogate_usage_overlay.browser_reader import BrowserSettings, NeurogateUsageReader


class BrowserReaderModeTest(unittest.TestCase):
    def test_keep_browser_open_updates_settings_before_start(self):
        reader = NeurogateUsageReader(BrowserSettings())

        reader.set_keep_browser_open(True)

        self.assertTrue(reader.keep_browser_open)
        self.assertFalse(reader.settings.hide_after_successful_login)

        reader.set_keep_browser_open(False)

        self.assertFalse(reader.keep_browser_open)
        self.assertTrue(reader.settings.hide_after_successful_login)

    def test_keep_browser_open_switches_running_context(self):
        reader = NeurogateUsageReader(BrowserSettings(headless=True))
        launches: list[bool] = []
        reader._playwright = object()
        reader._current_headless = True

        def fake_launch_context(*, headless: bool) -> None:
            launches.append(headless)
            reader._current_headless = headless

        reader._launch_context = fake_launch_context  # type: ignore[method-assign]

        reader.set_keep_browser_open(True)
        reader.set_keep_browser_open(False)

        self.assertEqual(launches, [False, True])


if __name__ == "__main__":
    unittest.main()
