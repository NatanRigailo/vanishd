IMAGE_NAME ?= vanishd
PORT       ?= 8080
DATA_VOL   ?= vanishd_data

.PHONY: up down build lint clean logs shell dev

build:
	docker build -t $(IMAGE_NAME) .

up: build
	docker run -d --name $(IMAGE_NAME) \
		-p $(PORT):8080 \
		-v $(DATA_VOL):/data \
		--env-file .env \
		$(IMAGE_NAME)

down:
	docker rm -f $(IMAGE_NAME) || true

clean: down
	docker volume rm $(DATA_VOL) || true
	docker rmi $(IMAGE_NAME) || true

dev:
	pip install pre-commit
	pre-commit install

lint:
	flake8 app/
	hadolint Dockerfile

logs:
	docker logs -f $(IMAGE_NAME)

shell:
	docker exec -it $(IMAGE_NAME) /bin/sh
