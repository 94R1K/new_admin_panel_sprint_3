FROM docker.elastic.co/elasticsearch/elasticsearch:8.6.2

USER root

RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=elasticsearch:elasticsearch movies.json /usr/share/elasticsearch/config/movies.json
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

USER elasticsearch

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]