export ENV_FILE_LOCATION=/home/vesko
export DEVELOP=True

sudo mkdir /var/run/mysqld
sudo chown mysql:mysql /var/run/mysqld/
sudo mysqld_safe --user=mysql &
