DOCKER_ANALYZER_MAKE = docker/analyzer/
DOCKER_DASHBOARD_MAKE = docker/dashboard/
INIT_SCRIPT = ./init_boursorama.sh
DOCKER_COMPOSE = docker/docker-compose.yaml
DATA_DIR = docker/data
ONEDRIVE_LINK = https://epitafr-my.sharepoint.com/:u:/r/personal/alexandre_devaux-riviere_epita_fr/Documents/boursorama.tar
SITE_RICOU_LINK = https://www.lrde.epita.fr/~ricou/pybd/projet/boursorama.tar

# Targets
fast:
	@$(MAKE) -C $(DOCKER_ANALYZER_MAKE) fast
	@$(MAKE) -C $(DOCKER_DASHBOARD_MAKE) fast
	@sleep 8 && firefox 127.0.0.1:8050 &
	@cd docker && docker compose up

all:
	@$(MAKE) -C $(DOCKER_ANALYZER_MAKE)
	@$(MAKE) -C $(DOCKER_DASHBOARD_MAKE)
	@$(INIT_SCRIPT) $(SITE_RICOU_LINK) $(DATA_DIR)
	@firefox 127.0.0.1:8050 &
	@cd docker && docker compose up

.PHONY: fast all