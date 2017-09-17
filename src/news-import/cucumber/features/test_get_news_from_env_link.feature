@get_news_from_link
Feature: Moneycontrol news extractor from link

  Scenario: get news link
    Given User navigate env link
    And User get news <symbol>