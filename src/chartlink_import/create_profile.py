import sbase as sb
from config import *
import shutil
     
if __name__ == "__main__":
    
    #shutil.rmtree("/Users/profilechrome/profiles")
    
    # sb.server = Server(sb.path, options={'existing_proxy_port_to_use': 16010})
    # time.sleep(1)
    # sb.server.start()
    # time.sleep(1)
    # sb.proxy = sb.server.create_proxy()
    # print("Server started")
    #
    # sb.option.add_argument('--proxy-server=%s' % sb.proxy.proxy)
    sb.option.add_argument("user-data-dir=/Users/profilechrome/profiles/p")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    sb.driver.get("https://chartink.com/login")
    time.sleep(10)
    sb.driver.find_element("id", "email").send_keys("rohit_51981@yahoo.co.in")
    sb.driver.find_element("id", "password").send_keys("1234567890")
    #sb.driver.find_element("css", "button.g-recaptcha").click()
    
    time.sleep(10)
    
    
    
    sb.driver.quit()
    
    shutil.copytree("/Users/profilechrome/profiles/p", "/Users/profilechrome/profiles/p1")
    shutil.copytree("/Users/profilechrome/profiles/p", "/Users/profilechrome/profiles/p2")
    shutil.copytree("/Users/profilechrome/profiles/p", "/Users/profilechrome/profiles/p3")
    shutil.copytree("/Users/profilechrome/profiles/p", "/Users/profilechrome/profiles/p4")
    shutil.copytree("/Users/profilechrome/profiles/p", "/Users/profilechrome/profiles/p5")
    shutil.copytree("/Users/profilechrome/profiles/p", "/Users/profilechrome/profiles/p6")
    shutil.copytree("/Users/profilechrome/profiles/p", "/Users/profilechrome/profiles/p7")
    shutil.copytree("/Users/profilechrome/profiles/p", "/Users/profilechrome/profiles/p8")
    
    