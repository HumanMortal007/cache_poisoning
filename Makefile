.PHONY: help install up down exploit validate secure vulnerable logs clean

help:
	@echo "====================================================================="
	@echo " Host Header Cache Poisoning Exploitation Lab (MITRE T1584)          "
	@echo "====================================================================="
	@echo "Available commands:"
	@echo "  make install    - Create Python venv and install requirements"
	@echo "  make up         - Build and start the Docker environment (vulnerable)"
	@echo "  make down       - Stop and remove the Docker environment"
	@echo "  make exploit    - Run the cache poisoning exploit script"
	@echo "  make validate   - Run the validation script to test mitigation"
	@echo "  make secure     - Apply the secure Nginx configuration"
	@echo "  make vulnerable - Apply the vulnerable Nginx configuration"
	@echo "  make dashboard  - Launch the Presenter Web Dashboard"
	@echo "  make clean      - Remove venv and clean up"

install:
	python -m venv venv
	.\venv\Scripts\pip install -r requirements.txt
	@echo "[+] Environment setup complete. Run 'make up' to start the lab."

up:
	docker-compose up --build -d
	@echo "[+] Lab is running at http://localhost:8080"

down:
	docker-compose down

exploit:
	.\venv\Scripts\python exploit\exploit.py -t http://localhost:8080 -m evil-hacker.com

validate:
	.\venv\Scripts\python tests\validate.py -t http://localhost:8080 -m test-hacker.com

secure:
	copy nginx\nginx_secure_original.conf nginx\nginx_vulnerable.conf
	docker-compose restart nginx
	@echo "[+] Secure configuration applied."

vulnerable:
	copy nginx\nginx_vulnerable_original.conf nginx\nginx_vulnerable.conf
	docker-compose restart nginx
	@echo "[+] Vulnerable configuration applied."

dashboard:
	.\venv\Scripts\python control_panel.py

logs:
	docker logs -f cdn_nginx_edge

clean:
	docker-compose down
	rmdir /S /Q venv
	@echo "[+] Clean up complete."
