.PHONY: lint vagrantcoverage

lint:
	pre-commit run --all-files

vagrantcoverage:
	coverage erase
	DATABASE_URL="sqlite:///test_modelsearch.sqlite" ~/.virtualenvs/modelsearch/bin/coverage run -p runtests.py --backend db
	DATABASE_URL="postgres:///modelsearch" ~/.virtualenvs/modelsearch/bin/coverage run -p runtests.py --backend db
	DATABASE_URL="mysql://vagrant:vagrant@localhost/modelsearch" ~/.virtualenvs/modelsearch/bin/coverage run -p runtests.py --backend db

	/home/vagrant/elasticsearch-7.17.29/bin/elasticsearch -q &
	sleep 10
	~/.virtualenvs/modelsearches70/bin/coverage run -p runtests.py --backend elasticsearch7
	~/.virtualenvs/modelsearches7/bin/coverage run -p runtests.py --backend elasticsearch7
	killall java

	/home/vagrant/elasticsearch-8.19.3/bin/elasticsearch -q &
	sleep 20
	ELASTICSEARCH_URL=https://modelsearch:modelsearch@localhost:9200 ELASTICSEARCH_CA_CERTS=~/elasticsearch-8.19.3/config/certs/http_ca.crt ~/.virtualenvs/modelsearches8/bin/coverage run -p runtests.py --backend elasticsearch8
	killall java

	/home/vagrant/elasticsearch-9.1.4/bin/elasticsearch -q &
	sleep 20
	ELASTICSEARCH_URL=https://modelsearch:modelsearch@localhost:9200 ELASTICSEARCH_CA_CERTS=~/elasticsearch-9.1.4/config/certs/http_ca.crt ~/.virtualenvs/modelsearches9/bin/coverage run -p runtests.py --backend elasticsearch9
	killall java

	/home/vagrant/opensearch-2.19.3/bin/opensearch -q &
	sleep 10
	~/.virtualenvs/modelsearchopensearch2/bin/coverage run -p runtests.py --backend opensearch2
	killall java

	/home/vagrant/opensearch-3.2.0/bin/opensearch -q &
	sleep 10
	~/.virtualenvs/modelsearchopensearch3/bin/coverage run -p runtests.py --backend opensearch3
	killall java

	coverage combine
	coverage html
