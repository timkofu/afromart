.PHONY: test migrate dev_server prod_server shell db_shell update_ui_components update_all export_dependencies tunnel release

test:
	@cd afromart && pytest --config-file=../pytest.ini || [ $$? -eq 5 ]

migrate:
	@cd afromart && python manage.py makemigrations && python manage.py migrate && python manage.py createcachetable > /dev/null
	@export DATABASE_URL=$(DATABASE_URL); psql $$DATABASE_URL -c "DROP DATABASE IF EXISTS test_afromart;" > /dev/null 2>&1

dev_server:
	@cd afromart && python manage.py runserver 127.0.0.1:${PORT}

prod_server:
	@cd afromart && gunicorn afromart.wsgi:application --bind 0.0.0.0:${PORT} --workers 4 --worker-class gthread --threads 4 --max-requests 1024 --max-requests-jitter 144 --timeout 89 --keep-alive 34 --access-logfile - --error-logfile -

shell:
	@cd afromart && python manage.py shell

dbshell:
	@cd afromart && python manage.py dbshell

update_ui_components:
	@cd third_party/ui && npm update
	@sass -q third_party/ui/scss/app.scss afromart/static_global/css/ui.css --style compressed --no-source-map
	@cat third_party/ui/node_modules/bootstrap-icons/font/bootstrap-icons.min.css > afromart/static_global/css/ui-icons.css
	@cp -ru third_party/ui/node_modules/bootstrap-icons/font/fonts afromart/static_global/css/
	@cat third_party/ui/node_modules/bootstrap/dist/js/bootstrap.bundle.min.js > afromart/static_global/js/ui.js
	@sed --in-place '$$d' afromart/static_global/js/ui.js
	@cat third_party/ui/node_modules/htmx.org/dist/htmx.min.js > afromart/static_global/js/dune.js
	@cat third_party/ui/node_modules/jquery/dist/jquery.min.js > afromart/static_global/js/spice.js

update_all:
	@uv lock --upgrade
	@$(MAKE) update_ui_components
	@git add third_party/ui afromart/static_global uv.lock

export_dependencies:
	@uv export --no-hashes > requirements.pip
	@uv export --no-hashes --group dev > dev_requirements.pip
	@git add requirements.pip dev_requirements.pip

tunnel:
	@ngrok http --url=${NGROK_DOMAIN} 65535 --host-header=rewrite

release: test export_dependencies
