import pathlib
import sbase as sb
from config import *
     
if __name__ == "__main__":
    script_directory = pathlib.Path().absolute()
    sb.option.add_experimental_option('excludeSwitches', ['enable-logging'])
    sb.option.add_argument(f"user-data-dir={script_directory}/profiles/p6")
    sb.driver = webdriver.Chrome(options=sb.option, desired_capabilities=sb.capabilities, executable_path = 'C:\git\cft\driver\chromedriver.exe')
    print('Started')
    sb.nw = datetime.now()
    
    while (sb.nw <= time_10_45):


        if (sb.nw >= time_09_35 and sb.nw <= time_10_00):
            # ( {cash} ( [=1] 5 minute open < 1 day ago high and [=1] 5 minute close < 1 day ago high and [-1] 5 minute low <= [-2] 15 minute low and [-1] 5 minute low <= [-3] 15 minute low and [-1] 5 minute low < [=1] 15 minute low and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low < -0.3 and ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close < -0.3 and ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close > -2.5 and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low > -2.5 and ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open > -3 and ( ( 1 day ago low - 1 day ago open ) * 100 ) / 1 day ago low > -4 and ( ( 1 day ago low - 1 day ago high ) * 100 ) / 1 day ago high > -5 and ( ( [=-3] 15 minute close - 1 day ago open ) * 100 ) / 1 day ago open < -1 and ( ( 1 day ago low - [=-12] 30 minute low ) * 100 ) / [=-12] 30 minute low < -1 and ( ( [=-3] 15 minute low - 2 days ago close ) * 100 ) / 2 days ago close < -1 and ( ( [=-2] 1 hour low - 2 days ago close ) * 100 ) / 2 days ago close < -1.5 and [-1] 5 minute high < [-1] 5 minute vwap and [-2] 5 minute high < [-2] 5 minute vwap and ( ( [-2] 5 minute high - [-1] 5 minute low ) * 100 ) / [-2] 5 minute high > -0.5 and ( ( [-1] 5 minute high - [0] 5 minute low ) * 100 ) / [-1] 5 minute high > -0.5 ) )
            process_url('https://chartink.com/screener/sell-breakdown-intraday-9-30-to-10-3', '(midcapdown-0.3)SSSsell--breakdown-intraday-9:40-to-10:10-01', time_09_35, time_10_00, True)
            # ( {cash} ( [=1] 5 minute open < 1 day ago high and [=1] 5 minute close < 1 day ago high and [-1] 5 minute low <= [-2] 15 minute low and [-1] 5 minute low < [=1] 15 minute low and ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close > -2.5 and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low > -2.5 and ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open > -2 and ( ( 1 day ago close - 2 days ago open ) * 100 ) / 2 days ago open > -3 and ( ( 1 day ago close - 3 days ago close ) * 100 ) / 3 days ago close > -3 and ( ( 1 day ago low - 1 day ago open ) * 100 ) / 1 day ago low > -4 and ( ( 1 day ago low - 1 day ago high ) * 100 ) / 1 day ago high > -5 and ( ( [=-3] 15 minute close - 1 day ago open ) * 100 ) / 1 day ago open < -1 and ( ( 1 day ago low - [=-12] 30 minute low ) * 100 ) / [=-12] 30 minute low < -1 and ( ( [=-3] 15 minute low - 2 days ago close ) * 100 ) / 2 days ago close < -1 and ( ( [=-2] 1 hour low - 2 days ago close ) * 100 ) / 2 days ago close < -1.5 and [0] 5 minute low < 1 day ago low and [-1] 5 minute high < [-1] 5 minute vwap and [-2] 5 minute high < [-2] 5 minute vwap and ( ( [-2] 5 minute high - [-1] 5 minute low ) * 100 ) / [-2] 5 minute high > -0.5 and ( ( [-1] 5 minute high - [0] 5 minute low ) * 100 ) / [-1] 5 minute high > -0.5 ) )
            process_url('https://chartink.com/screener/sell-breakdown-intraday-9-50-to-10-10-01', '(midcapdown-0.3)SSSsell-breakdown-intraday-9:40-to-10:10-01', time_09_35, time_10_00, True)

        if (sb.nw >= time_09_20 and sb.nw <= time_10_30):
            # ( {33489} ( ( {cash} ( 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" > -0.5 and 2 days ago "close - 1 candle ago close / 1 candle ago close * 100" > 0 and 3 days ago "close - 1 candle ago close / 1 candle ago close * 100" > 0 and ( ( 2 days ago close - 2 days ago open ) * 100 ) / 2 days ago open > 1 and ( ( 3 days ago close - 3 days ago open ) * 100 ) / 3 days ago open > 1.5 and ( ( 1 day ago close - 4 days ago close ) * 100 ) / 3 days ago close > 3 and ( ( 1 day ago close - 3 days ago open ) * 100 ) / 3 days ago open > 3 and abs ( ( 1 day ago high - 1 day ago open ) * 100 ) / 1 day ago open > 0.5 and [0] 5 minute low < 1 day ago low ) ) ) )
            process_url('https://chartink.com/screener/sell-uptrend-01', 'uplast3day: SSSsell-lastDayDoji/sell-first10minutelow-above-2-day-ago-close/BUY-first10minutelow-lt-2day-ago-close)', time_09_25, time_10_30, True)

        if (sb.nw >= time_10_00 and sb.nw <= time_11_30):
            # ( {33489} ( ( {cash} ( ( ( ( [=1] 5 minute low - [=1] 30 minute high ) * 100 ) / [=1] 5 minute open ) < -1 and ( ( ( [=1] 30 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.3 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -1 and ( ( ( 1 day ago low - [-1] 30 minute low ) * 100 ) / 1 day ago close ) > -0.5 and ( ( ( 1 day ago close - 2 days ago close ) * 100 ) / 1 day ago close ) < -1 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < 0 and [-1] 5 minute close < [=1] 5 minute low and [=1] 30 minute high >= [=1] 15 minute high and [=1] 30 minute high >= [=1] 1 hour high and [=3] 15 minute low > [=1] 15 minute low and [=2] 5 minute low > [-1] 5 minute low and [=2] 10 minute low > [-1] 5 minute low and [=2] 15 minute low > [-1] 5 minute low and [=1] 30 minute low < [=-1] 15 minute low and abs ( 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" ) > 0.75 and ( ( ( [-1] 5 minute close - [-2] 5 minute open ) * 100 ) / [=1] 5 minute open ) > -0.7 and ( ( ( [-1] 5 minute close - [-3] 5 minute open ) * 100 ) / [=1] 5 minute open ) > -1 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / [=1] 5 minute open ) < -0.5 ) ) ) )
            process_url_volBreakout('https://chartink.com/screener/sell-dayconsolidation-breakout-04', 'sell-dayconsolidation-breakout-02', time_10_00, time_12_15)


        # if (sb.nw >= time_09_40 and sb.nw <= time_10_30):
        # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute low < [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close < [=1] 5 minute open and [=1] 5 minute close < 1 day ago close and ( ( ( [-1] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( [=2] 5 minute high - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and ( ( ( [=1] 5 minute close - [=1] 5 minute open ) * 100 ) / 1 day ago close ) < -0.1 and ( ( ( 1 day ago close - 2 days ago open ) * 100 ) / 1 day ago close ) > -6 and [=1] 5 minute low < 3 days ago close and [=1] 5 minute open > 1 day ago low and [=2] 30 minute high < 2 days ago low and ( {cash} ( [=2] 5 minute low < [=1] 5 minute low and [-1] 5 minute low < [=3] 5 minute close and [-1] 5 minute low < [=3] 5 minute open and [-1] 5 minute low < [=1] 5 minute open and [-1] 5 minute low < [=1] 5 minute close and [-1] 5 minute high < [-1] 5 minute vwap ) ) ) ) ) )
        # process_url('https://chartink.com/screener/sell-morning-volume-breakout-after10', 'Sselll-morning-down-volume-breakout', time_09_30, time_10_30)


        # if(sb.nw>= time_09_45 and sb.nw <= time_11_15):
        #   ( {33489} ( ( {cash} ( ( ( [-1] 5 minute vwap - [-9] 5 minute vwap ) * 100 ) / [-9] 5 minute vwap < 0.1 and ( ( [-1] 5 minute vwap - [-9] 5 minute vwap ) * 100 ) / [-9] 5 minute vwap > -0.1 and [-1] 15 minute high < [=1] 5 minute open and [-1] 15 minute high < [=1] 15 minute high and [-1] 15 minute high > [=1] 1 hour low and [-1] 15 minute high < [=-1] 1 hour low and [-2] 15 minute high < [=1] 5 minute open and [-2] 15 minute high < [=1] 15 minute high and [-2] 15 minute high > [=1] 1 hour low and ( {cash} ( ( ( [-1] 5 minute high - [-12] 5 minute high ) * 100 ) / [-12] 5 minute high < 1 and ( ( [-1] 5 minute low - [-12] 5 minute low ) * 100 ) / [-12] 5 minute low < 1 and ( ( [-8] 5 minute high - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high < 1 and ( ( [-8] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low < 1 and ( ( [-1] 5 minute high - [-12] 5 minute high ) * 100 ) / [-12] 5 minute high > -1 and ( ( [-1] 5 minute low - [-12] 5 minute low ) * 100 ) / [-12] 5 minute low > -1 and ( ( [-8] 5 minute high - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high > -1 and ( ( [-8] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low > -1 and ( ( [=1] 5 minute low - [=-1] 15 minute low ) * 100 ) / [=-1] 15 minute low > -4 and ( ( [-1] 5 minute low - [=-1] 15 minute low ) * 100 ) / [=-1] 15 minute low > -4 and ( [-1] 5 minute low - [=1] 5 minute low ) < ( [=1] 5 minute low - [=1] 5 minute high ) and ( [=1] 1 hour high - [-1] 5 minute close ) > ( [-1] 5 minute close - [=1] 1 hour low ) and ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close < -1 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < 1 and [=-2] 2 hour low < [=-3] 2 hour low and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 0 and ( ( ( [-1] 5 minute close - [=-7] 1 hour high ) * 100 ) / [=-7] 1 hour high ) > -5 and ( ( ( [=1] 1 hour low - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open ) > -2 and ( ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open ) > -2 and [=2] 1 hour low < [=1] 1 hour low ) ) ) ) ) )
        # process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-01', 'QuickShot:sell-dayconsolidation-breakout-01', time_09_45, time_11_30, True)

        # if(sb.nw>= time_10_15 and sb.nw <= time_14_00):
        # process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-03', 'sell-dayconsolidation-breakout-03', time_10_15, time_14_00, True)

        # if(sb.nw>= time_09_35 and sb.nw <= time_10_30):
        # ( {33489} ( ( {cash} ( [-1] 5 minute low > [=1] 5 minute low and [-1] 5 minute low > [=1] 15 minute low and [-1] 30 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0 and [-1] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < 0 and [0] 15 minute "close - 1 candle ago close / 1 candle ago close * 100" < -0.3 and [=1] 1 hour high > [=-1] 5 minute low and [=1] 20 minute high = [=1] 1 hour high and [-1] 10 minute high < [=1] 15 minute high and ( ( [=3] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open > 0 and ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open > -2 and ( ( [-1] 5 minute close - [=1] 5 minute open ) * 100 ) / [=1] 5 minute open < 2 and ( ( [-1] 5 minute close - [=1] 5 minute high ) * 100 ) / [=1] 5 minute high > -2 and [0] 5 minute low < [0] 5 minute ema ( [0] 5 minute close , 20 ) and [-1] 5 minute high < [-1] 5 minute vwap and [-2] 5 minute high < [-2] 5 minute vwap and [-1] 5 minute low < [-1] 5 minute vwap and [-2] 5 minute low < [-2] 5 minute vwap and [-3] 5 minute low < [-3] 5 minute vwap and [-4] 5 minute low < [-4] 5 minute vwap ) ) ) )
        # process_url('https://chartink.com/screener/sell-check-morning-up-breakdown-02', 'check-morning-up-breakdown-02', time_09_35, time_10_45, True)


        # if(sb.nw>= time_09_40 and sb.nw <= time_10_30):
        # ( {33489} ( ( {cash} ( [=1] 5 minute open < 1 day ago high and [=1] 5 minute close < 1 day ago high and [-1] 5 minute low <= [-2] 15 minute low and [-1] 5 minute low <= [-3] 15 minute low and [-1] 5 minute low < [=1] 15 minute low and [-1] 5 minute low < [=2] 15 minute low and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low < -0.5 and ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close > -2.5 and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low > -1.5 and ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open > -4 and ( ( 1 day ago low - 1 day ago open ) * 100 ) / 1 day ago low > -4 and ( ( 1 day ago low - 1 day ago high ) * 100 ) / 1 day ago high > -5 and [-1] 5 minute low > 1 day ago low and [-1] 5 minute low > 2 days ago low and ( ( 3 days ago low - [-1] 5 minute low ) * 100 ) / [-1] 5 minute low < -1 and ( ( 4 days ago low - [-1] 5 minute low ) * 100 ) / [-1] 5 minute low < -2.5 ) ) ) )
        # process_url('https://chartink.com/screener/03-sellbreakdownintraday-01', 'sell-(==Reversal-lastDayLowNotReached==)03-BreakdownIntraday', time_09_40, time_10_15, True)
        # https://chartink.com/screener/03-sellbreakdownintraday-02

        # if(sb.nw>= time_10_00 and sb.nw <= time_11_30):
        #     process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-04', 'sell-dayconsolidation-breakout-04(10:00-to-12:00)', time_10_00, time_11_30, True)

        # if (sb.nw >= time_09_25 and sb.nw <= time_09_45):
        #
        # process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-4', 'sell-cash-breakout-morning-volume', time_09_25, time_09_45)

        # time.sleep(30)

        # if(sb.nw>= time_09_30 and sb.nw <= time_10_30):
        # ( {33489} ( ( {cash} ( [=1] 2 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 2 minute volume > greatest(  2 days ago volume / 24  ) and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1.5 and ( ( ( [=1] 1 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -0.5 and [0] 5 minute high > [=1] 5 minute open ) ) ) )
        # process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-3', 'SSSsell-downtrend-breakout-morning-volume', time_09_30, time_10_30, 'breakout-morning-volume-sell')

        # if(sb.nw>= time_09_25 and sb.nw <= time_09_45):
        # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute close < [=1] 5 minute open and [=2] 5 minute close < [=2] 5 minute open and ( ( ( [=2] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 1 ) ) ) )
        # process_url_volBreakout('https://chartink.com/screener/morning-volume-bs-2', 'morning-volume-bs', time_09_00, time_09_30, 'morning-volume-sell*2')

        # if (sb.nw >= time_09_45 and sb.nw <= time_11_00):
        # ( {46553} ( ( {cash} ( ( ( ( [=1] 15 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -2 and [=1] 30 minute low < 1 day ago close and [=1] 30 minute low = [=1] 20 minute low and [-1] 5 minute vwap > [-3] 5 minute vwap and ( ( [-1] 5 minute vwap - [=1] 5 minute vwap ) * 100 ) / [=1] 5 minute vwap > 0 and [=1] 5 minute close < [=1] 5 minute open and [=2] 5 minute open < [=1] 5 minute open and [=2] 5 minute close < [=1] 5 minute open and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 1.5 and ( ( ( 1 day ago close - 2 days ago open ) * 100 ) / 1 day ago close ) < 4 and ( {cash} ( ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.75 and [-1] 5 minute high > [=2] 5 minute high and [-1] 5 minute low > [=2] 5 minute low and [-1] 5 minute close > [=2] 5 minute low and [-1] 5 minute close > [=1] 5 minute open and [-1] 5 minute close > [=1] 5 minute close ) ) ) ) ) )
        # process_url_volBreakout('https://chartink.com/screener/buy-morning-down-2', 'checkChartSell-morningDown', time_09_45, time_11_00)
        # FIX
        #
        # if (sb.nw >= time_09_00 and sb.nw <= time_10_30):
        # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 12  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 18  ) and [=1] 5 minute high > [=1] 5 minute sma ( [=1] 5 minute close , 200 ) and [=1] 5 minute close > 1 day ago close and ( ( ( [=2] 5 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and ( ( ( [=1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > 0.5 and ( {cash} ( [=2] 5 minute high < [=1] 5 minute high and [-1] 5 minute high < [=1] 5 minute open and [-1] 5 minute high < [=1] 5 minute close and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" > 2 and 1 day ago "close - 1 candle ago close / 1 candle ago close * 100" < 5 and 2 days ago "close - 1 candle ago close / 1 candle ago close * 100" < 0.5 ) ) ) ) ) )
        # process_url_volBreakout('https://chartink.com/screener/sell-check-morning-up-breakdown-01', 'sell-morning-up-volume-breakout(wait-till-9:45/10)', time_09_00, time_10_30)

        # if(sb.nw>= time_09_40 and sb.nw <= time_10_30):
        # ( {33489} ( ( {cash} ( [=1] 5 minute open < 1 day ago high and [=1] 5 minute close < 1 day ago high and [-1] 5 minute low <= [-2] 15 minute low and [-1] 5 minute low <= [-3] 15 minute low and [-1] 5 minute low < [=1] 15 minute low and [-1] 5 minute low < [=2] 15 minute low and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low < -0.5 and ( ( [-1] 5 minute close - [=-1] 5 minute close ) * 100 ) / [=-1] 5 minute close > -2.5 and ( ( [-1] 5 minute low - [=1] 5 minute low ) * 100 ) / [=1] 5 minute low > -1.5 and ( ( 1 day ago close - 1 day ago open ) * 100 ) / 1 day ago open > -4 and ( ( 1 day ago low - 1 day ago open ) * 100 ) / 1 day ago low > -4 and ( ( 1 day ago low - 1 day ago high ) * 100 ) / 1 day ago high > -5 and [-1] 5 minute low > 1 day ago low and [-1] 5 minute low > 2 days ago low and ( ( 3 days ago low - [-1] 5 minute low ) * 100 ) / [-1] 5 minute low < -1 and ( ( 4 days ago low - [-1] 5 minute low ) * 100 ) / [-1] 5 minute low < -2.5 ) ) ) )
        # process_url('https://chartink.com/screener/03-sellbreakdownintraday-01', 'sell-(==Reversal-lastDayLowNotReached==)03-BreakdownIntraday', time_09_40, time_10_15, True)
        # https://chartink.com/screener/03-sellbreakdownintraday-02

        # if(sb.nw>= time_10_00 and sb.nw <= time_11_30):
        #     process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-04', 'sell-dayconsolidation-breakout-04(10:00-to-12:00)', time_10_00, time_11_30, True)

        # if (sb.nw >= time_09_25 and sb.nw <= time_09_45):
        #
        # process_url_volBreakout('https://chartink.com/screener/morning-volume-breakout-sell-4', 'sell-cash-breakout-morning-volume', time_09_25, time_09_45)

        # time.sleep(30)

       # if(sb.nw>= time_09_25 and sb.nw <= time_09_45):
        # ( {57960} ( ( {cash} ( [=1] 5 minute volume > greatest(  1 day ago volume / 24  ) and [=1] 15 minute volume > greatest(  1 day ago volume / 18  ) and [=1] 5 minute volume > greatest(  2 days ago volume / 24  ) and [=1] 5 minute close < [=1] 5 minute open and [=2] 5 minute close < [=2] 5 minute open and ( ( ( [=2] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 1 ) ) ) )
        # process_url_volBreakout('https://chartink.com/screener/morning-volume-bs-2', 'morning-volume-bs', time_09_00, time_09_30, 'morning-volume-sell*2')

        # if (sb.nw >= time_09_45 and sb.nw <= time_11_00):
        # ( {46553} ( ( {cash} ( ( ( ( [=1] 15 minute low - 1 day ago close ) * 100 ) / 1 day ago close ) < -2 and [=1] 30 minute low < 1 day ago close and [=1] 30 minute low = [=1] 20 minute low and [-1] 5 minute vwap > [-3] 5 minute vwap and ( ( [-1] 5 minute vwap - [=1] 5 minute vwap ) * 100 ) / [=1] 5 minute vwap > 0 and [=1] 5 minute close < [=1] 5 minute open and [=2] 5 minute open < [=1] 5 minute open and [=2] 5 minute close < [=1] 5 minute open and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < 1.5 and ( ( ( 1 day ago close - 2 days ago open ) * 100 ) / 1 day ago close ) < 4 and ( {cash} ( ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) < -1 and ( ( ( [-1] 5 minute close - 1 day ago close ) * 100 ) / 1 day ago close ) > -1.75 and [-1] 5 minute high > [=2] 5 minute high and [-1] 5 minute low > [=2] 5 minute low and [-1] 5 minute close > [=2] 5 minute low and [-1] 5 minute close > [=1] 5 minute open and [-1] 5 minute close > [=1] 5 minute close ) ) ) ) ) )
        # process_url_volBreakout('https://chartink.com/screener/buy-morning-down-2', 'checkChartSell-morningDown', time_09_45, time_11_00)

        #time.sleep(10)
        sb.nw = datetime.now()
        
    sb.driver.quit()
    