import pathlib

import sbase as sb
from config import *
import shutil
     
if __name__ == "__main__":
    
    #shutil.rmtree("profiles")
    
    # sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 16010})
    # time.sleep(1)
    # sb.server.start()
    # time.sleep(1)
    # sb.proxy = sb.server.create_proxy()
    # print("Server started")
    #
    # sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    script_directory = pathlib.Path().absolute()
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities, executable_path = 'C:\git\cft\driver\chromedriver.exe')
    sb.driver.get("https://chartink.com/login")
    time.sleep(10)
    sb.driver.find_element("id", "email").send_keys("rohit_51981@yahoo.co.in")
    sb.driver.find_element("id", "password").send_keys("qwER12#$")
    #sb.driver.find_element("css", "button.g-recaptcha").click()
    
    time.sleep(10)
    
    
    
    sb.driver.quit()
    
    shutil.copytree("profiles/p", "profiles/p1")
    shutil.copytree("profiles/p", "profiles/p2")
    shutil.copytree("profiles/p", "profiles/p3")
    shutil.copytree("profiles/p", "profiles/p4")
    shutil.copytree("profiles/p", "profiles/p5")
    shutil.copytree("profiles/p", "profiles/p6")
    shutil.copytree("profiles/p", "profiles/p7")
    shutil.copytree("profiles/p", "profiles/p8")
    
    