And(/^User navigate to (.*)$/) do |url|
  home_page_white_box.visit_home_page(url)
end

And(/^Verify User navigated to (.*)$/) do |title|
  expect(home_page_white_box.page_title).to eq(title)
end
