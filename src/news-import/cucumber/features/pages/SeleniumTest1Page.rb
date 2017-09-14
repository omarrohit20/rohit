class SeleniumTest1Page

  include BasePage

  def init_selectors
    @verify_button = "id-012"
    @link_text = "selenium-test2"

  end

  def initialize
    @session = Capybara.current_session
    init_selectors
  end

  def click_button_presentByID_id012
    @session.click_button(@verify_button)
  end

  #Find and click selenium-test2
  def click_selenium_test2
    @session.click_link(@link_text)
  end

end


