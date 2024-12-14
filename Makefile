.PHONY: build run stop logs clean

# Сборка образов
build:
    docker-compose build

# Запуск сервисов в фоновом режиме
run:
    docker-compose up -d

# Остановка сервисов
stop:
    docker-compose stop

# Подключение к логам всех сервисов
logs:
    docker-compose logs -f

# Удаление всех контейнеров, сетей и томов
clean:
    docker-compose down -v --remove-orphans
