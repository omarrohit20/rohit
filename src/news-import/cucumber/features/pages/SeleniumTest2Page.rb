class SeleniumTest2Page

  include BasePage

  def init_selectors
    @test_box = "q2"
    @link_text = "selenium-test1"

  end

  def initialize
    @session = Capybara.current_session
    init_selectors
  end

  def input_text_box(txt)
    @session.fill_in(@test_box, :with => txt)
  end

  #Find and click selenium-test2
  def click_selenium_test1
    @session.click_link(@link_text)
  end

end


