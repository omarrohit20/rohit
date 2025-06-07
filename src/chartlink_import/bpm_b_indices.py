import pathlib
import sbase as sb
from config import *
     
if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p1")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities, executable_path = 'C:\git\cft\driver\chromedriver.exe')
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_11_00):
        #if (sb.nw >= time_09_40 and sb.nw <= time_10_30):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 22  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 15  ) and [-2] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0 and [-1] 5 minute "close - 1 candle ago close / 1 candle ago close * 100" > -0.1 and [-1] 5 minute close > [=2] 5 minute high and ( ( ( [0] 5 minute high - [-2] 5 minute low ) * 100 ) / 1 day ago close ) < 0.7 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago close ) < 0.5 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 1.3 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 3 and ( {cash} ( ( ( ( [=1] 15 minute high - [=-3] 2 hour low ) * 100 ) / 1 day ago close ) < 2 ) ) ) ) ) )
            #process_url_volBreakout('https://chartink.com/screener/buy-morning-volume-breakout-checknews-02', 'buy-morning-volume-breakout(Check-News)-02', time_09_50, time_11_00)

        #if (sb.nw >= time_09_40 and sb.nw <= time_10_30):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and abs ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open ) > 1.6 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.75 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 1 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 2.5 and ( ( ( [=1] 15 minute high - [=-3] 2 hour low ) * 100 ) / 1 day ago close ) < 2 and [-1] 5 minute open > [=1] 5 minute open and [-1] 5 minute close > [=1] 5 minute open and [-1] 5 minute high > [-2] 5 minute high and [0] 30 minute low > [=-1] 15 minute low ) ) ) )
            #process_url_volBreakout('https://chartink.com/screener/buy-morning-volume-breakout-checknews-01', 'buy-morning-volume-breakout(Check-News)-01', time_09_50, time_11_00)

        if (sb.nw >= time_09_45 and sb.nw <= time_11_00):
            # ( {33489} ( ( {cash} ( ( ( ( [0] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 1 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 4 and ( ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) > 0.75 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 1 and ( ( ( weekly high - 1 day ago high ) * 100 ) / 1 day ago close ) > 0.5 and ( ( ( 1 week ago high - [=1] 5 minute high ) * 100 ) / 1 day ago close ) > 0 and ( ( ( 1 week ago high - 1 day ago high ) * 100 ) / 1 day ago close ) > 0 and ( [=1] 15 minute high - [-1] 5 minute high ) < ( [-1] 5 minute low - [=1] 15 minute low ) and [-1] 5 minute close > [=2] 5 minute open and [-1] 5 minute close > [=2] 5 minute close and [0] 15 minute low > [=2] 5 minute open and [0] 15 minute low > [=2] 5 minute open and [=2] 15 minute low > [=-1] 5 minute low ) ) and ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 30  ) and ( ( ( [-1] 5 minute close - [-2] 5 minute open ) * 100 ) / [=1] 5 minute open ) < 0.7 and ( ( ( [-1] 5 minute close - [-3] 5 minute open ) * 100 ) / [=1] 5 minute open ) < 0.9 and ( ( ( [-1] 5 minute close - [-4] 5 minute open ) * 100 ) / [=1] 5 minute open ) < 1 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-volume-breakout-checknews', 'buy-morning-volume-breakout(Check-News)', time_09_50, time_10_50)


        #if (sb.nw >= time_09_40 and sb.nw <= time_10_30):
            # ( {cash} ( ( {cash} ( [=1] 15 minute volume > greatest(  1 day ago volume / 24  ) and [-1] 5 minute high > 1 day ago high and [-1] 5 minute high > 2 days ago high and [-1] 5 minute high > 3 days ago high and [=1] 10 minute low < 1 day ago high and [=1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0 and ( ( [-1] 5 minute high - 15 days ago high ) * 100 ) / 1 day ago close > 5 and abs ( ( [-1] 5 minute high - 7 days ago high ) * 100 ) / 1 day ago close > 3 and ( ( [=1] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close > 0 and ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close > 0.75 and ( {33489} not ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) ) ) and ( {45603} not ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) ) ) and ( {166311} not ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) ) ) ) ) ) )
            #process_url_volBreakout('https://chartink.com/screener/supertrend-morning-buy', 'cash-buy-morning-volume', time_09_40, time_10_30)

        time.sleep(10)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    
