Then(/^I should see list of all resources loaded after a web page document has started to load$/) do
  page.driver.debug
  page.driver.network_traffic.each do |request|
    request.response_parts.uniq(&:url).each do |response|
      puts "\n Responce URL #{response.url}: \n Status #{response.status}"
    end
  end
end