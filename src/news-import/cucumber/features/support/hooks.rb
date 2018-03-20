require_relative './pages'

File.delete('temp/newslink.txt') if File.exist?('temp/newslink.txt')

Before do
  ## setup code
end

After do
  ## teardown code
end

Before('@wip, @ci') do
  # This will only run before scenarios tagged
  # with @wip OR @ci.
end

AfterStep('@wip', '@ci') do
  # This will only run after steps within scenarios tagged
  # with @wip AND @ci.
end

Before do |scenario|
  if ENV['dry_run'] == 'true'
    Capybara.current_session.driver.browser.quit
    raise 'Fail each test immediately'
  end
end


instantiate_pages


