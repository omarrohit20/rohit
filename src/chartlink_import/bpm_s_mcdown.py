import pathlib
import sbase as sb
from config import *
     
if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p5")
    sb.option.add_argument('--headless=new')
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities)
    print('Started')
    sb.nw = datetime.now()

    while (sb.nw <= time_11_00):

        if (sb.nw >= time_09_40 and sb.nw <= time_10_30):
            # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute low < [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close < [=1] 5 minute open and [=1] 5 minute close < 1 day ago close and ( ( ( [-1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( [=2] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) < -0.1 and ( ( ( 1 day ago close - 2 days ago open ) * 100 ) / 1 day ago close ) > -6 and [=1] 5 minute low < 3 days ago close and [=1] 5 minute open > 1 day ago low and [=2] 30 minute high < 2 days ago low and ( {cash} ( [=2] 5 minute low < [=1] 5 minute low and [-1] 5 minute low < [=3] 5 minute close and [-1] 5 minute low < [=3] 5 minute open and [-1] 5 minute low < [=1] 5 minute open and [-1] 5 minute low < [=1] 5 minute close and [-1] 5 minute high < [-1] 5 minute vwap ) ) ) ) ) )
            process_url('https://chartink.com/screener/sell-morning-volume-breakout-after10', '0-Sselll-morning-down-volume-breakout', time_09_30, time_10_30)

        if (sb.nw >= time_09_30 and sb.nw <= time_10_30):
            # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute low < [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close < 1 day ago close and ( ( ( [=2] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1.5 and ( {cash} ( [=2] 5 minute low < [=1] 5 minute low and [-1] 5 minute low < [=1] 5 minute open and [-1] 5 minute low < [=1] 5 minute close and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < -2 ) ) ) ) ) )
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-04', '1-Sselll-morning-down-volume-breakout', time_09_30, time_10_15)

        if (sb.nw >= time_09_30 and sb.nw <= time_10_00):
            #( {33489} ( ( {cash} ( ( ( ( [=1] 15 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.75 and [=1] 30 minute low < 1 day ago close and [=1] 30 minute low = [=1] 20 minute low and [-1] 5 minute vwap > [-3] 5 minute vwap and [=1] 5 minute close < [=1] 5 minute open and [=2] 5 minute open < [=1] 5 minute open and [=2] 5 minute close < [=1] 5 minute open and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [-1] 5 minute close - [=-1] 5 minute low ) * 100 ) / 1 day ago close ) < -1.2 ) ) and ( {cash} ( [=1] 2 minute volume > greatest(  1 day ago volume / 24  ) and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 ) ) ) )
            process_url('https://chartink.com/screener/sell-breakdown-intraday-9-50-to-10-10-04', 'Sselll-morningDown-upConsolidation', time_09_30, time_10_00)

        if (sb.nw >= time_09_30 and sb.nw <= time_10_15):
            # ( {cash} ( ( latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago high)" - [=1] 15 minute low ) > ( [=1] 15 minute low - latest "(1 candle ago high + 1 candle ago low + 1 candle ago close / 3)" ) and ( latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago low )" - [-1] 5 minute low ) > ( [-1] 5 minute low - latest "(1 candle ago high + 1 candle ago low + 1 candle ago close / 3)" ) and [=1] 1 hour high > [=1] 15 minute high and [=1] 2 hour high > latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago low )" and [-1] 5 minute low < latest "(1 candle ago high + 1 candle ago low + 1 candle ago close / 3)" and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < -0.5 and 2 days ago "close - 1 candle ago close / 1 candle ago close * 100" < -0.5 and ( latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago low )" - latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago high)" ) * 100 / latest "( (1 candle ago high + 1 candle ago low + 1 candle ago close / 3 ) * 2 - 1 candle ago high)" > 2 ) )
            process_url('https://chartink.com/screener/sell-ema-down1', 'Sselll-checkChart-ema-down0', time_09_30, time_10_15)

        if (sb.nw >= time_09_40 and sb.nw <= time_10_15):
            # ( {33489} ( ( {cash} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and ( ( [=1] 5 minute low - [=1] 5 minute close ) * 100 ) / [=1] 5 minute close > -0.5 and [=1] 5 minute close < [=1] 5 minute open and [=1] 5 minute close < 1 day ago close and [=1] 5 minute close < [=-1] 5 minute low ) ) and ( {cash} ( [-1] 5 minute high < [=1] 5 minute close and [-1] 15 minute high < [=1] 5 minute close and [-1] 15 minute low > [=1] 15 minute low and ( ( [-1] 5 minute vwap - [-3] 5 minute vwap ) * 100 ) / [-4] 5 minute vwap < 0.1 and ( ( [-1] 5 minute vwap - [-3] 5 minute vwap ) * 100 ) / [-4] 5 minute vwap > -0.1 ) ) and ( {cash} ( ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open ) > -2 and ( ( ( 1 day ago close - 2 days ago close ) * 100 ) / 2 days ago close ) < 0.1 and ( ( [=-1] 1 hour low - [=-3] 1 hour high ) * 100 ) / [=-3] 1 hour high > -2 and ( ( ( [-1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( [-1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > -3 and ( ( ( [=1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > -3 and ( ( ( [=1] 5 minute low - 1 day ago open ) * 100 ) / 1 day ago high ) > -5 and ( ( ( [=1] 5 minute low - 1 day ago high ) * 100 ) / 1 day ago high ) > -5 ) ) ) ) ) )
            process_url('https://chartink.com/screener/sell-morning-up-1', 'Sselll-checkChart-ema-down1(sell-bellow-cons-S2:followLastDayPostlunch-gt-S1S2)', time_09_40, time_10_00)




        #time.sleep(10)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    