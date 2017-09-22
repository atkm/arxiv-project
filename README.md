- `pip install -r requirements`
- db instructions:
     * install and initialize postgres. enable and start in systemctl
     * add user via createuser --interactive after sudo -u postgres -i
     * create project\_name table in psql
     * edit DATABASE\_URL in .envrc
     * python manage.py {init,migrate,upgrade}
