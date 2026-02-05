import pytest
import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": { "width": 1280, "height": 720 },
    }

@pytest.fixture(scope="function")
def login_page(page):
    from pages.login_page import LoginPage
    return LoginPage(page)

@pytest.fixture(scope="function")
def faktur_pajak_page(page):
    from pages.faktur_pajak_page import FakturPajakPage
    return FakturPajakPage(page)
