import unittest
from subprocess import run


class TestInstall(unittest.TestCase):
    def test_library_installed(self):
        import autoetl

        self.assertIsNotNone(autoetl)

    def test_module(self):
        run(["python3", "-m", "autoetl", "--help"])

    def test_consolescript(self):
        run(["poetry", "shell", "-c", "autoetl", "--help"])
