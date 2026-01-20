.PHONY: create-folder create-docker run-docker run-debug-docker permission-folder stop-docker clean-docker

# criacao da pasta pgdata
create-folder:
	mkdir -p data/postgres/pgdata

permission-folder:
	sudo chmod 777 data/postgres/pgdata -R

# subir o projeto
create-clear-docker:
	docker compose build --no-cache

create-docker:
	docker compose build

run-docker:
	docker compose up -d

run-debug-docker:
	docker compose up

# parar o projeto
stop-clear-docker:
	docker compose down -v

stop-docker:
	docker compose down

clean-docker:
	sudo rm -r data/postgres -R