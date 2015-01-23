build:
	docker build -t python-ubuntu .
	
run:
	-docker rm -f kuku
	docker run -d --name=kuku -v $(PWD):/app python-ubuntu
	
enter:
	docker exec -i -t kuku bash
	