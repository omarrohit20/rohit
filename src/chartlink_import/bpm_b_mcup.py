import pathlib
import sbase as sb
from config import *
     
if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p2")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities, executable_path = 'C:\git\cft\driver\chromedriver.exe')
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_11_00):

        if (sb.nw >= time_09_40 and sb.nw <= time_10_30):
            # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 12  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute high > [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close > [=1] 5 minute open and [=1] 5 minute close > 1 day ago close and ( ( ( [=2] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) > 0.1 and ( ( ( 1 day ago close - 2 days ago open ) * 100 ) / 1 day ago close ) < 6 and 1 day ago close > 3 days ago close and [=1] 5 minute open < 1 day ago high and [=2] 30 minute low > 2 days ago high and ( {cash} ( [=2] 5 minute high > [=1] 5 minute high and [-1] 5 minute high > [=3] 5 minute close and [-1] 5 minute high > [=3] 5 minute open and [-1] 5 minute high > [=1] 5 minute open and [-1] 5 minute high > [=1] 5 minute close and [-1] 5 minute low > [-1] 5 minute vwap ) ) ) ) ) )
            process_url('https://chartink.com/screener/morning-volume-breakout-1-2', 'Bbuyy-morning-up-volume-breakout', time_09_30, time_10_00)

        if (sb.nw >= time_09_40 and sb.nw <= time_11_00):
            # ( {33489} ( ( {cash} ( [-1] 5 minute close < [=1] 30 minute high and [=1] 30 minute high > 1 day ago close and [=1] 30 minute high = [=1] 20 minute high and [-1] 5 minute vwap < [-3] 5 minute vwap and [=1] 5 minute close > [=1] 5 minute open and [=2] 5 minute close > [=1] 5 minute open and [=2] 5 minute open > [=1] 5 minute open and ( ( ( [=1] 15 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.75 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) > 0.5 and ( ( ( [-1] 5 minute close - [=-1] 5 minute high ) * 100 ) / 1 day ago close ) > 1.2 and ( ( ( [-1] 5 minute close - [=1] 5 minute low ) * 100 ) / [=1] 5 minute open ) > 0.75 ) ) and ( {cash} ( [=1] 3 minute volume > greatest(  1 day ago volume / 24  ) and [0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-breakup-intraday-9-25-to-10-30-06', '1-morningUp-downConsolidation-Bbuyy:UptrendOrHeavyUpInDowntrend\SellDowntrend', time_09_40, time_11_00)

        if (sb.nw >= time_10_00 and sb.nw <= time_10_45):
            """
            ({33489}(({cash}([=1] 5 minute volume > greatest(  1 day ago volume/ 24) and (
                        (([=1] 30 minute high - 1 day ago close) * 100) / 1 day ago close) > 1.5 and (
                                 (([-1] 5 minute close -[=-1] 5 minute close) * 100) / [=-1] 5 minute close) > 1.1 and (
                                 (([-1] 5 minute close -[=1] 5 minute low) * 100) / [=1] 5 minute open) < 4 and (
                                 (([-1] 5 minute close -[=1] 5 minute low) * 100) / [=1] 5 minute open) > 0.75 and (
                                 ((1 day ago close - 3 days ago close) * 100) / 1 day ago close) < 6 and (
                                 ((1 day ago close - 2 days ago close) * 100) / 2 days ago close) < 3 and (
                                 ((1 day ago close - 2 days ago high) * 100) / 1 day ago close) < 0.5 and (
                                 (([=1] 5 minute close -[=1] 5 minute open) * 100) / [=1] 5 minute open) > 0.1 and [0]
             30 minute "close - 1 candle ago close / 1 candle ago close * 100" > 0 and[0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" > -0.3 and[0] 15 minute high <[=1] 30 minute high and[-1] 5 minute high <[=1] 30 minute high and[=1] 15 minute low < 1 day ago high and[=2] 15 minute low >[=-1] 15 minute high) ) ) )
            """
            process_url_volBreakout('https://chartink.com/screener/buy-dayconsolidation-breakout-02', '0-Bbuyy-morningUp-downConsolidation', time_09_45, time_10_45)

        if (sb.nw >= time_09_30 and sb.nw <= time_10_15):
            # ( {33489} ( ( {cash} ( [=1] 5 minute volume < greatest(  1 day ago volume / 24  ) and [=1] 10 minute volume > greatest(  1 day ago volume / 12  ) and ( ( [=1] 10 minute high - 1 day ago close ) * 100 ) / 1 day ago close < 1.5 and ( ( ( 1 day ago close - 2 days ago close ) * 100 ) / 2 days ago close ) > -0.1 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago close ) < 0.75 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < 1 ) ) and ( {cash} ( [=1] 5 minute low < 1 day ago close and [-1] 5 minute high > 1 day ago close and ( ( [-1] 5 minute high - [-2] 5 minute high ) * 100 ) / [-1] 5 minute high < 0.1 and ( ( [-1] 5 minute high - [-3] 5 minute high ) * 100 ) / [-1] 5 minute high < 0.1 and ( ( [-1] 5 minute low - [-2] 5 minute low ) * 100 ) / [-1] 5 minute low > -0.1 and ( ( [-1] 5 minute low - [-3] 5 minute low ) * 100 ) / [-1] 5 minute low > -0.1 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-ema-up1', '0-Bbuyy-checkChart-ema-up', time_09_30, time_10_15)

        if (sb.nw >= time_09_40 and sb.nw <= time_10_15):
            # ( {33489} ( ( {cash} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and ( ( [=1] 5 minute high - [=1] 5 minute close ) * 100 ) / [=1] 5 minute close < 0.5 and [=1] 5 minute close > [=1] 5 minute open and [=1] 5 minute close > 1 day ago close and [=1] 5 minute close > [=-1] 5 minute high ) ) and ( {cash} ( [-1] 5 minute low > [=1] 5 minute close and [-1] 15 minute low > [=1] 5 minute close and [-1] 15 minute high < [=1] 15 minute high and ( ( [-1] 5 minute vwap - [-3] 5 minute vwap ) * 100 ) / [-4] 5 minute vwap < 0.1 and ( ( [-1] 5 minute vwap - [-3] 5 minute vwap ) * 100 ) / [-4] 5 minute vwap > -0.1 ) ) and ( {cash} ( ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open ) < 2 and ( ( ( [=1] 5 minute high - 2 days ago close ) * 100 ) / 2 days ago close ) < 2 and ( ( ( 1 day ago close - 2 days ago close ) * 100 ) / 2 days ago close ) > -0.1 and ( ( [=-1] 1 hour high - [=-3] 1 hour low ) * 100 ) / [=-3] 1 hour low < 2 and ( ( ( [-1] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) > 1.2 and ( ( ( [-1] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) < 3 and ( ( ( [=1] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) < 3 and ( ( ( [=1] 5 minute high - 1 day ago open ) * 100 ) / 1 day ago high ) < 5 and ( ( ( [=1] 5 minute high - 1 day ago low ) * 100 ) / 1 day ago high ) < 5 ) ) ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/buy-morning-down-1', '1-Bbuyy-checkChart-ema-up1(buy-above-cons-R2:followLastDayPostlunch-lt-R1R2)', time_09_40, time_10_00)




        #time.sleep(10)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    