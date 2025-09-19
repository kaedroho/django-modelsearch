#!/usr/bin/env bash

PROJECT_NAME=modelsearch

: ${PROJECT_DIR:=/vagrant}
: ${DEV_USER:=vagrant}

VIRTUALENV_DIR=/home/$DEV_USER/.virtualenvs/$PROJECT_NAME
PYTHON=$VIRTUALENV_DIR/bin/python
PIP=$VIRTUALENV_DIR/bin/pip
BASHRC=/home/$DEV_USER/.bashrc

apt update -y
apt install -y vim git curl gettext build-essential ca-certificates gnupg pkg-config
apt install -y python3 python3-dev python3-pip python3-venv python-is-python3
apt install -y postgresql libpq-dev
apt install -y mysql-server libmysqlclient-dev

# Create pgsql superuser
PG_USER_EXISTS=$(
    su - postgres -c \
    "psql postgres -tAc \"SELECT 'yes' FROM pg_roles WHERE rolname='vagrant' LIMIT 1\""
)

if [[ "$PG_USER_EXISTS" != "yes" ]];
then
    su - postgres -c "createuser -s vagrant"
fi

# Create mysql superuser
mysql -e "CREATE USER 'vagrant'@'localhost' IDENTIFIED BY 'vagrant'"
mysql -e "GRANT ALL ON test_modelsearch.* TO 'vagrant'@'localhost'"

su - $DEV_USER -c "python -m venv $VIRTUALENV_DIR"
su - $DEV_USER -c "$PIP install psycopg mysqlclient"
su - $DEV_USER -c "$PIP install -e $PROJECT_DIR[test]"

BASHRC_LINE_VENV="source $VIRTUALENV_DIR/bin/activate"
cat $BASHRC | grep -v "^$BASHRC_LINE_VENV" > "${BASHRC}.tmp" && mv ${BASHRC}.tmp $BASHRC
echo $BASHRC_LINE_VENV >> $BASHRC


# Elasticsearch 7
ES7_VERSION=7.17.29
ES7_DOWNLOAD_FILE=elasticsearch-$ES7_VERSION-linux-`uname -p`.tar.gz
ES7_DOWNLOAD_URL=https://artifacts.elastic.co/downloads/elasticsearch/$ES7_DOWNLOAD_FILE
ES7_ROOT=/home/$DEV_USER/elasticsearch-$ES7_VERSION
ES7_VIRTUALENV_DIR=/home/$DEV_USER/.virtualenvs/modelsearches7
ES7_PIP=$ES7_VIRTUALENV_DIR/bin/pip

su - $DEV_USER -c "wget $ES7_DOWNLOAD_URL -P /home/$DEV_USER"
su - $DEV_USER -c "cd /home/$DEV_USER && tar xzf $ES7_DOWNLOAD_FILE"
su - $DEV_USER -c "$ES7_ROOT/bin/elasticsearch-users useradd modelsearch -p modelsearch -r superuser"

su - $DEV_USER -c "python -m venv $ES7_VIRTUALENV_DIR"
su - $DEV_USER -c "$ES7_PIP install 'elasticsearch>=7.15.0,<8.0.0'"
su - $DEV_USER -c "$ES7_PIP install -e $PROJECT_DIR[test]"

# Add a separate venv for elasticsearch >=7.0,<7.15 (with the older api,
# so that coverage reports can cover both code paths)
ES70_VIRTUALENV_DIR=/home/$DEV_USER/.virtualenvs/modelsearches70
ES70_PIP=$ES70_VIRTUALENV_DIR/bin/pip
su - $DEV_USER -c "python -m venv $ES70_VIRTUALENV_DIR"
su - $DEV_USER -c "$ES70_PIP install 'elasticsearch==7.13.4'"
su - $DEV_USER -c "$ES70_PIP install -e $PROJECT_DIR[test]"

# Elasticsearch 8
ES8_VERSION=8.19.3
ES8_DOWNLOAD_FILE=elasticsearch-$ES8_VERSION-linux-`uname -p`.tar.gz
ES8_DOWNLOAD_URL=https://artifacts.elastic.co/downloads/elasticsearch/$ES8_DOWNLOAD_FILE
ES8_ROOT=/home/$DEV_USER/elasticsearch-$ES8_VERSION
ES8_VIRTUALENV_DIR=/home/$DEV_USER/.virtualenvs/modelsearches8
ES8_PIP=$ES8_VIRTUALENV_DIR/bin/pip

su - $DEV_USER -c "wget $ES8_DOWNLOAD_URL -P /home/$DEV_USER"
su - $DEV_USER -c "cd /home/$DEV_USER && tar xzf $ES8_DOWNLOAD_FILE"
su - $DEV_USER -c "$ES8_ROOT/bin/elasticsearch-users useradd modelsearch -p modelsearch -r superuser"

su - $DEV_USER -c "python -m venv $ES8_VIRTUALENV_DIR"
su - $DEV_USER -c "$ES8_PIP install 'elasticsearch>=8.0.0,<9.0.0'"
su - $DEV_USER -c "$ES8_PIP install -e $PROJECT_DIR[test]"

# Opensearch 1
OPENSEARCH1_VERSION=1.3.20
OPENSEARCH1_DOWNLOAD_FILE=opensearch-min-$OPENSEARCH1_VERSION-linux-arm64.tar.gz
OPENSEARCH1_DOWNLOAD_URL=https://artifacts.opensearch.org/releases/core/opensearch/$OPENSEARCH1_VERSION/$OPENSEARCH1_DOWNLOAD_FILE
OPENSEARCH1_ROOT=/home/$DEV_USER/opensearch-$OPENSEARCH1_VERSION
OPENSEARCH1_VIRTUALENV_DIR=/home/$DEV_USER/.virtualenvs/modelsearchopensearch1
OPENSEARCH1_PIP=$OPENSEARCH1_VIRTUALENV_DIR/bin/pip

su - $DEV_USER -c "wget $OPENSEARCH1_DOWNLOAD_URL -P /home/$DEV_USER"
su - $DEV_USER -c "cd /home/$DEV_USER && tar xzf $OPENSEARCH1_DOWNLOAD_FILE"

su - $DEV_USER -c "python -m venv $OPENSEARCH1_VIRTUALENV_DIR"
su - $DEV_USER -c "$OPENSEARCH1_PIP install 'opensearch-py>=1,<2'"
su - $DEV_USER -c "$OPENSEARCH1_PIP install 'requests>=2.4.0, <3.0.0'"  # missing from opensearch-py 1 dependencies - https://github.com/opensearch-project/opensearch-py/pull/142
su - $DEV_USER -c "$OPENSEARCH1_PIP install -e $PROJECT_DIR[test]"

# Opensearch 2
OPENSEARCH2_VERSION=2.19.3
OPENSEARCH2_DOWNLOAD_FILE=opensearch-min-$OPENSEARCH2_VERSION-linux-arm64.tar.gz
OPENSEARCH2_DOWNLOAD_URL=https://artifacts.opensearch.org/releases/core/opensearch/$OPENSEARCH2_VERSION/$OPENSEARCH2_DOWNLOAD_FILE
OPENSEARCH2_ROOT=/home/$DEV_USER/opensearch-$OPENSEARCH2_VERSION
OPENSEARCH2_VIRTUALENV_DIR=/home/$DEV_USER/.virtualenvs/modelsearchopensearch2
OPENSEARCH2_PIP=$OPENSEARCH2_VIRTUALENV_DIR/bin/pip

su - $DEV_USER -c "wget $OPENSEARCH2_DOWNLOAD_URL -P /home/$DEV_USER"
su - $DEV_USER -c "cd /home/$DEV_USER && tar xzf $OPENSEARCH2_DOWNLOAD_FILE"

su - $DEV_USER -c "python -m venv $OPENSEARCH2_VIRTUALENV_DIR"
su - $DEV_USER -c "$OPENSEARCH2_PIP install 'opensearch-py>=2,<3'"
su - $DEV_USER -c "$OPENSEARCH2_PIP install -e $PROJECT_DIR[test]"

# Opensearch 3
OPENSEARCH3_VERSION=3.2.0
OPENSEARCH3_DOWNLOAD_FILE=opensearch-min-$OPENSEARCH3_VERSION-linux-arm64.tar.gz
OPENSEARCH3_DOWNLOAD_URL=https://artifacts.opensearch.org/releases/core/opensearch/$OPENSEARCH3_VERSION/$OPENSEARCH3_DOWNLOAD_FILE
OPENSEARCH3_ROOT=/home/$DEV_USER/opensearch-$OPENSEARCH3_VERSION
OPENSEARCH3_VIRTUALENV_DIR=/home/$DEV_USER/.virtualenvs/modelsearchopensearch3
OPENSEARCH3_PIP=$OPENSEARCH3_VIRTUALENV_DIR/bin/pip

su - $DEV_USER -c "wget $OPENSEARCH3_DOWNLOAD_URL -P /home/$DEV_USER"
su - $DEV_USER -c "cd /home/$DEV_USER && tar xzf $OPENSEARCH3_DOWNLOAD_FILE"

su - $DEV_USER -c "python -m venv $OPENSEARCH3_VIRTUALENV_DIR"
su - $DEV_USER -c "$OPENSEARCH3_PIP install 'opensearch-py>=3,<4'"
su - $DEV_USER -c "$OPENSEARCH3_PIP install -e $PROJECT_DIR[test]"
