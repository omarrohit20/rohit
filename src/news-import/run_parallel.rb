require 'logger'

FLAG = '@regression'
APPENV = 'qa'
RETRYCOUNT = 3
CONTAINER = 'my_test'

$testcases = Hash.new
$dids_tc = Hash.new
$dids_users = Hash.new
$users_queue = Queue.new

$PASSED = 0
$FAILED = 0

startTime = Time.now

$logger = Logger.new("../logfile#{Time.now.strftime('%Y-%m-%d_%H-%M-%S')}.log")

# Populate user pool queue
users = Array["test1India@mailinator.com, test1US@mailinator.com",
              "test2India@mailinator.com, test2US@mailinator.com",
              "test3India@mailinator.com, test3US@mailinator.com",
              "test4India@mailinator.com, test4US@mailinator.com"
             ]
users.each{|user| $users_queue.push(user)}

def time_diff(start_time, end_time)
  seconds_diff = (start_time - end_time).to_i.abs

  hours = seconds_diff / 3600
  seconds_diff -= hours * 3600

  minutes = seconds_diff / 60
  seconds_diff -= minutes * 60

  seconds = seconds_diff

  "#{hours.to_s.rjust(2, '0')}:#{minutes.to_s.rjust(2, '0')}:#{seconds.to_s.rjust(2, '0')}"
end

# Process finished container for log and reports
# Reattempt\Retry failed scenario for specified number of time
# Removed processed\finished container
def process_container
  for did in $dids_tc.keys
    state = `sudo docker inspect -f {{.State.Running}} #{did}`

    if state.strip == false || state.strip == 'false'
      testcase = $dids_tc[did]
      users = $dids_users[did]
      $dids_tc.delete(did)
      $dids_users.delete(did)
      $testcases[testcase] -= 1

      output = `sudo docker logs #{did} | sed "s,\x1B\[[0-9;]*[a-zA-Z],,g"`
      p testcase
      output.split(/\n/).each{|line| p line}

      if (!output.include? "failed,") && (output.include? "passed)")
        $logger.info("#######################################")
        $logger.info(testcase)
        $logger.info(output)
        $testcases[testcase] = 0
        $users_queue.push(users)
        $PASSED += 1
      else
        if $testcases[testcase] > 0
          p "### RETRYING ... #{RETRYCOUNT-$testcases[testcase]} TEST #{testcase}"

          user = (!testcase.include? 'US') ? users.split(',')[0] : users.split(',')[1]
          didtemp = `sudo docker run -d #{CONTAINER} "cucumber -p selenium #{testcase} app_env=#{APPENV} username=#{user}"`
          $dids_tc[didtemp.strip] = testcase
          $dids_users[didtemp.strip] = users
        else
          $logger.info("#######################################")
          $logger.info(testcase)
          $logger.info(output)
          #`docker cp #{did}:/opt/saas-shipping-ui/qa-automation/temp ../reports`
          $users_queue.push(users)
          $FAILED += 1
        end
      end

      `sudo docker rm #{did}`
    end
  end
end

# Build docker image and pull automation latest source
`sudo docker build -t my_test .`
# $logger.info(output)


# Dry run to get list of test scenario
output = `sudo docker run -a stdout -i #{CONTAINER} "cucumber -p selenium --tags #{FLAG} app_env=#{APPENV} dry_run=true -f rerun" | sed "s,\x1B\[[0-9;]*[a-zA-Z],,g"`
output.split(/ /).each{ |testcase|
  $testcases[testcase] = RETRYCOUNT
}
$logger.info("Total Test Scenario #{$testcases.length}")



# Iterate each test case, pop user credentials from pool queue
# And run scenario in docker container
count = 0
for testcase in $testcases.keys[0..$testcases.length] do
  while $users_queue.empty?
    process_container
  end
  count += 1
  p "### #{count} ### RUNNING TEST #{testcase}"

  users = $users_queue.pop
  user = (!testcase.include? 'US') ? users.split(',')[0] : users.split(',')[1]
  p "sudo docker run -d #{CONTAINER} \"cucumber -p selenium #{testcase} app_env=#{APPENV} username=#{user}\""
  did = `sudo docker run -d #{CONTAINER} "cucumber -p selenium #{testcase} app_env=#{APPENV} username=#{user}"`
  $dids_tc[did.strip] = testcase
  $dids_users[did.strip] = users
end

while not $dids_tc.empty?
  process_container
end

$logger.info("#######################################")
$logger.info("Scenario Passed:#{$PASSED} Failed:#{$FAILED}")
p "Scenario Passed:#{$PASSED} Failed:#{$FAILED}"

endTime = Time.now
$logger.info(time_diff(startTime, endTime))

$logger.close
#`sudo docker rm $(sudo docker ps -a -q)`

