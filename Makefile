# Определяем переменные
DOCKER_COMPOSE = docker compose
DOCKER_COMPOSE_FILE = docker-compose.yml


help:
	@echo "Доступные команды:"
	@echo "  make up      - Запустить приложение с помощью Docker Compose (первый запуск может потребовать немного времени)"
	@echo "  make down    - Остановить приложение и удалить контейнеры"
	@echo "  make logs    - Просмотр логов приложения"
	@echo "  make clean   - Удалить все контейнеры, тома и сети"

up:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d

down:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

logs:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f

clean:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down -v --rmi all --remove-orphans
