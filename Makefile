DOCKER_ANALYZER_MAKE = docker/analyzer/
DOCKER_DASHBOARD_MAKE = docker/dashboard/
INIT_SCRIPT = init_boursorama.sh
DOCKER_COMPOSE = docker/docker-compose.yaml
DATA_DIR = docker/data
ONEDRIVE_LINK = https://acxpcq.db.files.1drv.com/y4m1rZorPP2kN8W6PGekjlKsY5CbZ4L2jhg4iXMGWWhe8xMIbmnDBYlZYJTnrH4_T_eCrjM_Ree83dgW-GkXhuyMHEuM5jMXnO4qewwjyOl_jXJMxiNvLI0QXu7Nau9Y4ynzQVg3TaEkQJTH9x6YP9FijI04pJsgGfhk-vCu2nWDqeA5CsFyfQG5Ks0JY6AyO918TiEm_IOxtt4yIiHsdhrQQ
SITE_RICOU_LINK = https://www.lrde.epita.fr/~ricou/pybd/projet/boursorama.tar

# Targets
fast:
	@$(MAKE) -C $(DOCKER_ANALYZER_MAKE) fast
	@$(MAKE) -C $(DOCKER_DASHBOARD_MAKE) fast
	@cd docker && docker compose up

all:
	@$(MAKE) -C $(DOCKER_ANALYZER_MAKE)
	@$(MAKE) -C $(DOCKER_DASHBOARD_MAKE)
	@if ! bash $(INIT_SCRIPT) $(SITE_RICOU_LINK) $(DATA_DIR); then \
		echo "Download failed on the Ricou's Website, trying to Download from our OneDrive"; \
		bash $(INIT_SCRIPT) $(ONEDRIVE_LINK) $(DATA_DIR); \
	fi
	@cd docker && docker compose up

.PHONY: fast all
