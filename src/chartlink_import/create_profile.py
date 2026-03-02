import pathlib

import sbase as sb
from config import *
import shutil
from playwright.sync_api import sync_playwright
     
if __name__ == "__main__":
    # create a fresh profile directory if needed
    # shutil.rmtree("profiles")

    script_directory = pathlib.Path().absolute()

    # launch a persistent context using Playwright
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(script_directory / "profiles" / "p"),
            headless=False,  # make it visible so you can complete any captcha/login steps
            args=["--no-sandbox", "--disable-gpu"]
        )
        page = context.new_page()
        page.goto("https://chartink.com/login")

        # fill credentials and wait for manual actions if needed
        page.fill("#login-email", "rohit_51981@yahoo.co.in")
        page.fill("#login-password", "abc")
        # if there's a captcha you'll need to solve it manually in the opened browser
        page.wait_for_timeout(10000)  # 10s pause to allow manual interaction

        context.close()

    # after logging in copy the base profile for multiple instances
    for i in range(1, 9):
        shutil.copytree("profiles/p", f"profiles/p{i}")
    
    