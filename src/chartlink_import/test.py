# # from browsermobproxy import Server
# # import psutil
# # import time
# #
# # for proc in psutil.process_iter():
# #     #check whether the process name matches
# #     if proc.name() == "browsermob-proxy":
# #         proc.kill()
# #
# # portno = 19030
# # dict = {'port': portno}
# # server = Server(path="./browsermob/bin/browsermob-proxy", options=dict)
# # server.start()
# # time.sleep(1)
# # proxy = server.create_proxy()
# # time.sleep(1)
# # from selenium import webdriver
# # profile = webdriver.FirefoxProfile()
# # selenium_proxy = proxy.selenium_proxy()
# # profile.set_proxy(selenium_proxy)
# # # profile.set_preference("network.proxy.type",1);
# # # profile.set_preference("network.proxy.ftp","192.168.1.255");
# # # profile.set_preference("network.proxy.http","192.168.1.255");
# # # profile.set_preference("network.proxy.socks","192.168.1.255");
# # # profile.set_preference("network.proxy.ssl","192.168.1.255");
# # # profile.set_preference("network.proxy.ftp_port",portno);
# # # profile.set_preference("network.proxy.http_port",portno);
# # # profile.set_preference("network.proxy.socks_port",portno);
# # # profile.set_preference("network.proxy.ssl_port",portno);
# # # profile.set_preference("network.proxy.share_proxy_settings", True);
# # driver = webdriver.Firefox(firefox_profile=profile)
# #
# #
# # proxy.new_har("google")
# # driver.get("https://www.google.co.uk")
# # print (proxy.har) # returns a HAR JSON blob
# #
# # server.stop()
# # driver.quit()
#
# # from seleniumwire import webdriver  # Import from seleniumwire
# #
# # # Create a new instance of the Chrome driver
# # driver = webdriver.Firefox()
# #
# # # Go to the Google home page
# # driver.get('https://www.google.com')
# #
# # # Access requests via the `requests` attribute
# # for request in driver.requests:
# #     if request.response:
# #         print(
# #             request.url,
# #             request.response.status_code,
# #             request.response.headers['Content-Type']
# #         )
#
# # from selenium import webdriver
# # from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# #
# # capabilities = DesiredCapabilities.CHROME
# # # capabilities["loggingPrefs"] = {"performance": "ALL"}  # chromedriver < ~75
# # capabilities["goog:loggingPrefs"] = { 'browser':'ALL' }
# #
# # driver = webdriver.Chrome(
# #     desired_capabilities=capabilities,
# # )
# #
# # driver.get("https://chartink.com/screener/buy-dayconsolidation-breakout-01")
# # logs = driver.get_log("browser")
# # print(logs)
# #
# # scriptToExecute = "var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;";
# # logs = driver.execute_script(scriptToExecute)
# # print(logs)
# #
# # #driver.quit()
#
# from selenium import webdriver
# from browsermobproxy import Server
# import psutil
# import time
# from selenium.webdriver import DesiredCapabilities
#
# # for proc in psutil.process_iter():
# #     #check whether the process name matches
# #     if proc.name() == "browsermob-proxy":
# #         proc.kill()
#
#
# server = Server(path="./browsermob/bin/browsermob-proxy", options={'existing_proxy_port_to_use': 8099})
# server.start()
# time.sleep(1)
# proxy = server.create_proxy()
# time.sleep(1)
#
# option = webdriver.ChromeOptions()
# print(proxy.proxy)
# option.add_argument('--proxy-server=%s' % proxy.proxy)
#
# prefs = {"profile.managed_default_content_settings.images": 2}
# option.add_experimental_option("prefs", prefs)
# #option.add_argument('--headless')
# #option.add_argument('--no-sandbox')
# #option.add_argument('--disable-gpu')
#
# capabilities = DesiredCapabilities.CHROME.copy()
# capabilities['acceptSslCerts'] = True
# capabilities['acceptInsecureCerts'] = True
#
# driver = webdriver.Chrome(options=option,
#                            desired_capabilities=capabilities)
#
# #proxy.new_har("google")
# proxy.new_har("file_name", options={'captureHeaders': False, 'captureContent': True, 'captureBinaryContent': True})
# driver.get("https://chartink.com/screener/buy-dayconsolidation-breakout-01")
# print (proxy.har) # returns a HAR JSON blob
#
# import
#
# server.stop()
# driver.quit()



# install_certifi.py
#
# sample script to install or update a set of default Root Certificates
# for the ssl module.  Uses the certificates provided by the certifi package:
#       https://pypi.python.org/pypi/certifi

import os
import os.path
import ssl
import stat
import subprocess
import sys

STAT_0o775 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
             | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
             | stat.S_IROTH |                stat.S_IXOTH )


def main():
    openssl_dir, openssl_cafile = os.path.split(
        ssl.get_default_verify_paths().openssl_cafile)

    print(" -- pip install --upgrade certifi")
    subprocess.check_call([sys.executable,
        "-E", "-s", "-m", "pip", "install", "--upgrade", "certifi"])

    import certifi

    # change working directory to the default SSL directory
    os.chdir(openssl_dir)
    relpath_to_certifi_cafile = os.path.relpath(certifi.where())
    print(" -- removing any existing file or link")
    try:
        os.remove(openssl_cafile)
    except FileNotFoundError:
        pass
    print(" -- creating symlink to certifi certificate bundle")
    os.symlink(relpath_to_certifi_cafile, openssl_cafile)
    print(" -- setting permissions")
    os.chmod(openssl_cafile, STAT_0o775)
    print(" -- update complete")

if __name__ == '__main__':
    main()





