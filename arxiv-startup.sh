apt-get update
apt-get install git python3-pip redis-server postgresql

cd /opt
git clone $REPO
cd arxiv-project
pip3 install -r requirements.txt
source .envrc # => will complain that the venv dir cannot be found, but the necessary env vars will be set regardless.

# ensure the migrations dir is not present
rm -r migrations
python3 manage.py db init
python3 manage.py db migrate # need to have permissions to postgres. e.g. sudo -u postgres createuser username.
python3 manage.py db upgrade

# how to run `create database arxiv_project` non-interactively?
redis-server &
