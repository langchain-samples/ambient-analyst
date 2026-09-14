import unittest

from agent.harness.visualization import (
    FAVICON,
    VISUALIZATION_LINK_TTL_SECONDS,
    sandbox_path,
    share_visualization,
    visualization_path,
)


class FakeSandbox:
    def __init__(self):
        self.args = None
        self.html = "<html><head></head><body>chart</body></html>"
        self.written = None

    def read(self, path):
        return self.html.encode()

    def write(self, path, content):
        self.written = path, content

    def generate_download_url(self, *args, **kwargs):
        self.args = args, kwargs
        return object()


class VisualizationTest(unittest.TestCase):
    def test_share_visualization_mints_inline_hour_link(self):
        sandbox = FakeSandbox()

        share_visualization(sandbox, "/analysis/chart.html")

        self.assertEqual(
            sandbox.args,
            (
                ("/chart.html",),
                {
                    "expires_in_seconds": VISUALIZATION_LINK_TTL_SECONDS,
                    "content_type": "text/html",
                    "content_disposition": "inline",
                },
            ),
        )
        self.assertEqual(sandbox.written, ("/chart.html", sandbox.html.replace("<head>", f"<head>{FAVICON}")))

    def test_sandbox_path_removes_virtual_analysis_mount(self):
        self.assertEqual(sandbox_path("/analysis/chart.html"), "/chart.html")

    def test_visualization_path_rejects_non_analysis_html(self):
        for path in (
            "chart.html",
            "/tmp/chart.html",
            "/analysis/chart.svg",
            "/analysis/../secret.html",
        ):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    visualization_path(path)


if __name__ == "__main__":
    unittest.main()
