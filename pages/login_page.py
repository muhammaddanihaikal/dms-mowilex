import os
from playwright.sync_api import Page, expect
from dotenv import load_dotenv

load_dotenv()

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username_input = page.get_by_placeholder("name@company.com")
        self.password_input = page.get_by_placeholder("Enter your password")
        self.sign_in_button = page.get_by_role("button", name="Sign In")

    def navigate(self):
        url = os.getenv("BASE_URL", "https://dms.mowilex.id/")
        self.page.goto(url)

    def login(self, username, password):
        self.username_input.fill(username)
        self.password_input.fill(password)
        # Sign in button might be disabled until filled
        self.sign_in_button.click()
