And(/^input text box (.*)$/) do |txt|
  selenium_test_2_page.input_text_box(txt)
end

And(/^click on selenium-test1 link$/) do
  selenium_test_2_page.click_selenium_test1
end