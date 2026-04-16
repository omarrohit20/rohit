# coding: utf-8
import sys
sys.path.append(r'src\data-import')
import nse_options_data_fetcher
print('fetch RELIANCE')
df=nse_options_data_fetcher.fetch_nse_options_data('RELIANCE')
print('result', df)
