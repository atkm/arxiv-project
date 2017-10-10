- `pip install -r requirements`

- db (local):
     * install and initialize postgres. enable and start in systemctl
     * add user via createuser --interactive after sudo -u postgres -i
     * create project\_name table in psql
     * edit DATABASE\_URL in .envrc
     * python manage.py {init,migrate,upgrade}
     * metha_to_postgres.py to populate rows

- run (local):
     * start redis-server and python worker.py
     * python manage.py runserver

- deploy:
     * heroku create appname-{stage,pro}
     * git remote add {stage,pro} git@heroku.com:appname-{stage,pro}.git; then push.
     * heroku config:set APP_SETTINGS=config.StagingConfig --remote stage
     * heroku addons:create heroku-postgresql:hobby-dev --app appname-stage
     * (heroku config --app appname-stage to check config)
     * heroku run python manage.py db upgrade --app appname-stage ( migrations/ should be pushed )
     * heroku addons:create redistogo:nano --app appname-stage
     * Procfile calls heroku.sh to run gunicorn and worker.py

- extra:
     * nltk.txt in root to fetch corpora (or create and push nlkt\_data dir)
      
- Reference:
     * Real Python - Flask by Example
     * Alembic Tutorial (official)
     * Vuejs guide (official)
