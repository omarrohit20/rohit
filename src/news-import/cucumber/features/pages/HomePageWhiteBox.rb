class HomePageWhiteBox

  include BasePage

  def initialize
    @session = Capybara.current_session
  end

  def visit_home_page(url)
    puts url
    @session.visit(url)
  end

  def visit_env_link
    url = ENV['link']
    puts url
    @session.visit(url)
  end

  def page_title
    @session.title
  end

end


