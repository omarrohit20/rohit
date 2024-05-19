import pathlib
import sbase as sb
from config import *
     
if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p4")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities, executable_path = 'C:\git\cft\driver\chromedriver.exe')
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_14_00):
        if (sb.nw >= time_10_00 and sb.nw <= time_11_00):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and ( ( ( [=1] 15 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > 0.5 and ( ( ( [=1] 15 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > 1 and ( ( ( [=1] 15 minute high - 1 day ago close ) * 100 ) / [=1] 5 minute open ) > -0.3 and ( ( ( [-1] 5 minute close - [-3] 5 minute open ) * 100 ) / [=1] 5 minute open ) < -0.5 and ( [=1] 30 minute high - [0] 5 minute low ) > ( [0] 5 minute low - 1 day ago close ) and [0] 5 minute close < [=1] 15 minute close and [0] 5 minute close < [=3] 5 minute low ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-morning-up-0', '9_30:checkChartSell-morningup(LastDaybeforeLT0)', time_10_00, time_11_00)

        if (sb.nw >= time_09_30 and sb.nw <= time_10_30):
            # ( {cash} ( ( {cash} ( [=1] 15 minute volume > greatest(  1 day ago volume / 24  ) and [-1] 5 minute low < 1 day ago low and [-1] 5 minute low < 2 days ago low and [-1] 5 minute low < 3 days ago low and [=1] 10 minute high > 1 day ago low and [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0 and abs ( ( 1 day ago close - 7 days ago low ) * 100 ) / 1 day ago close > 3 and ( ( [=1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close < 0 and ( {33489} not ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) ) ) and ( {45603} not ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) ) ) and ( {166311} not ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) ) ) ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/supertrend-morning-sell', 'cash-sell-morning-volume', time_09_30, time_10_30)

        time.sleep(5)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    