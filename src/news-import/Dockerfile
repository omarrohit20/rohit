FROM ruby:2.3.0

MAINTAINER Rohit Omar <omarrohit20@gmail.com>

RUN apt-get update
RUN apt-get install -y wget
RUN apt-get install -y git
RUN apt-get install -y curl

ENV PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y build-essential xvfb chrpath libssl-dev libxft-dev libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev && \
    curl -L -O https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOM_JS.tar.bz2 && \
    tar xvjf $PHANTOM_JS.tar.bz2 && \
    mv $PHANTOM_JS /usr/local/share && \
    ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin

RUN apt-get update && apt-get install -y \
  build-essential \
  nodejs

# cleanup
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

CMD []

RUN gem install bundler rake

WORKDIR /opt
RUN cd /opt
COPY cucumber /opt/cucumber
WORKDIR /opt/cucumber
RUN cd /opt/cucumber
RUN ls
RUN bundle install
RUN bundle update

# install xvfb init script
#RUN apt-get install -y xvfb
COPY xvfb-run /usr/local/bin/
RUN chmod +x /usr/local/bin/xvfb-run
ENTRYPOINT ["/usr/local/bin/xvfb-run"]