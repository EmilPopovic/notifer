# Default compose file (can be overridden with COMPOSE_FILE=compose.dev.yaml)
COMPOSE_FILE ?= compose.yaml

.PHONY: up
up:
	docker compose -f $(COMPOSE_FILE) up --build

.PHONY: upd
upd:
	docker compose -f $(COMPOSE_FILE) up -d --build

.PHONY: down
down:
	docker compose -f $(COMPOSE_FILE) down

.PHONY: initdb
initdb:
	docker compose -f $(COMPOSE_FILE) run --build --rm notifer python -m src.db_manager create

.PHONY: resetdb
resetdb:
	docker compose -f $(COMPOSE_FILE) run --build --rm notifer python -m src.db_manager reset

.PHONY: dropdb
dropdb:
	docker compose -f $(COMPOSE_FILE) run --build --rm notifer python -m src.db_manager drop

.PHONY: checkdb
checkdb:
	docker compose -f $(COMPOSE_FILE) run --build --rm notifer python -m src.db_manager check

.PHONY: snapshot
snapshot:
	@echo "Ensuring postgres container is running..."
	@docker compose -f $(COMPOSE_FILE) up -d postgres
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S) && \
	POSTGRES_USER=$$(grep '^POSTGRES_USER=' .env | cut -d '=' -f2) && \
	BACKUP_FILE="snapshot_$${TIMESTAMP}.sql.gz" && \
	echo "Creating database snapshot: $${BACKUP_FILE}" && \
	docker compose -f $(COMPOSE_FILE) exec -T postgres pg_dumpall --clean --if-exists --username=$${POSTGRES_USER} | gzip > "$${BACKUP_FILE}" && \
	echo "Snapshot created successfully: $${BACKUP_FILE}"
