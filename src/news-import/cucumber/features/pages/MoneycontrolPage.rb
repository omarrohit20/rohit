class MoneycontrolPage

  include BasePage

  def init_selectors
    @verify_button = "id-012"
    @link_text = "selenium-test2"
    @search_text_box = "search_str";
    @search_text_submit = "//a[@onclick=\"$('#form_topsearch').submit();\"]"
    @suggestion_link = "a > span";
    @news_link = "NEWS";
    @news_content = "div[class=\"\"] > div[class=\"FL\"] > div[class=\"MT15 PT10 PB10\"] > div[class=\"FL\"]"

  end

  def initialize
    @session = Capybara.current_session
    init_selectors
  end

  def search_company(company)
    #expect(@session).to have_selector(@search_text_box, visible: true)
    @session.fill_in(@search_text_box, :with => company)
  end

  def click_search_company
    Capybara.default_selector = :xpath
    @session.find(@search_text_submit).click
  end

  def click_first_suggestion
    Capybara.default_selector = :css
    @session.find(@suggestion_link).click
  end

  def click_news_link
    Capybara.default_selector = :link
    @session.find(@news_link).click
  end

  def get_url_and_log(company, symbol)
    url = @session.current_url
    open('temp/newslink.txt', 'a') { |f|
      f.puts '| ' + company + ' | ' + symbol + ' | ' + url + ' | '
    }
  end

  def get_news_and_log(symbol)
    client = Mongo::Client.new([ '127.0.0.1:27017' ], :database => 'Nsedata')
    news = Array.new

    Capybara.default_selector = :css
    logfile = 'temp/' + symbol
    File.delete(logfile) if File.exist?(logfile)
    open(logfile, 'a') { |f|
      f.puts '{'
      f.puts ' newsItems:['
      @session.all(@news_content).each { |a|
        f.puts '  {'
        attr = a.find("p[class=\"PT3 a_10dgry\"]").text.split('|')
        timestamp = attr[0].strip + ' ' + attr[1].strip
        date = attr[1].strip
        time = attr[0].strip
        summary = a.find("a[class=\"g_14bl\"] > strong").text
        link = a.find("a[class=\"g_14bl\"]")[:href]
        f.puts '   timestamp:"' + timestamp + '"'
        f.puts '   date:"' + date + '"'
        f.puts '   time:"' + time + '"'
        f.puts '   summary:"' + summary + '"'
        f.puts '   link:"' + link + '"'
        f.puts '  },'

        news.push({ :timestamp => timestamp, :date => date, :time => time, :summary => summary, :link => link})
      }
      f.puts ' ]'
      f.puts '}'
    }

    client[:news].insert_one({:scrip => symbol, :news => news})
    client.close
  end

end