@get_news
Feature: Moneycontrol news extractor

  Scenario Outline: get news link
    Given User navigate to <newslink>
    And User get news <symbol>
    Examples:
      |	company	|	symbol	| newslink  |
      | ADANI ENTERPRISES LIMITED | ADANIENT | http://www.moneycontrol.com/company-article/adanienterprises/news/AE13#AE13 |
      | ADANI PORT & SEZ LTD | ADANIPORTS | http://www.moneycontrol.com/company-article/adaniportsspecialeconomiczone/news/MPS#MPS |
      | ADANI POWER LTD | ADANIPOWER | http://www.moneycontrol.com/company-article/adanipower/news/AP11#AP11                       |
