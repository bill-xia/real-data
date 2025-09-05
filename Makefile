all: server

.PNOHY: server

server:
	python3 generate_site.py
	cp -r data build/
	python3 -m http.server -d build 26919