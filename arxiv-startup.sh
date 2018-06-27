apt-get update
apt-get install git python3-pip redis-server postgresql

cd /opt
git clone $REPO
cd arxiv-project
pip3 install -r requirements.txt
python3 -c "import nltk; nltk.download('stopwords')"
source .envrc # => will complain that the venv dir cannot be found, but the necessary env vars will be set regardless.

# ensure the migrations dir is not present
rm -r migrations
python3 manage.py db init
python3 manage.py db migrate # need to have permissions to postgres. e.g. sudo -u postgres createuser username.
python3 manage.py db upgrade

gsutil cp gs://arxiv-3121/metha.backup20170925.tgz .
tar xzf metha.backup20170925.tgz
mv .metha/b* xmls  # the directory has an ugly name
python3 metha_to_postgres.py /opt/arxiv-project/xmls/*.xml.gz  # ensure permissions to 

# how to run `create database arxiv_project` non-interactively?
redis-server &

python3 worker.py &
python3 manage.py runserver -h 0.0.0.0 -p 8080
