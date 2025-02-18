import pathlib
import sbase as sb
from config import *

if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p6")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities,
                                 executable_path='C:\git\cft\driver\chromedriver.exe')
    print('Started')
    sb.nw = datetime.now()

    if (sb.nw >= time_00_15 and sb.nw <= time_24_00):
        # ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 10 minute close > [=1] 5 minute open and [=1] 10 minute close > [=-1] 5 minute high and abs ( ( ( [=1] 10 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0 and ( ( ( [=1] 10 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 0.5 and ( ( ( [=1] 10 minute high - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 0.75 and [=-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < 1 ) )
        process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-buy-2', 'test', time_00_15, time_24_00)
        print('Hello')
        process_url_volBreakout('https://chartink.com/screener/buy-morning-volume-breakout-checknews','test', time_00_15, time_24_00)
    time.sleep(10)

    #if (sb.nw >= time_10_00 and sb.nw <= time_24_00):
        # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and ( ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close ) > 1.1 and ( ( ( [-1] 5 minute close - [=1] 5 minute low ) * 100 ) / [=1] 5 minute open ) < 2 and ( ( ( [-1] 5 minute close - [=1] 5 minute low ) * 100 ) / [=1] 5 minute open ) > 0.75 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.1 and ( ( ( 1 day ago close - 3 days ago close ) * 100 ) / 1 day ago close ) < 6 and ( ( ( 1 day ago close - 2 days ago close ) * 100 ) / 2 days ago close ) < 3 and [0] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0 and [0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" > -0.3 and [0] 5 minute high < [=1] 15 minute high and [=1] 15 minute low < 1 day ago high and [=2] 15 minute low > [=-1] 15 minute high ) ) ) )
        #process_url('https://chartink.com/screener/buy-dayconsolidation-breakout-02', 'test_process_url', time_09_00, time_15_30)


    sb.driver.quit()
