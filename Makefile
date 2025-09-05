all: server

.PNOHY: server

server:
	python3 generate_site.py
	find data -name "*.csv" -exec cp --parents {} build/ \;
	python3 -m http.server -d . 26919

clean:
	rm -rf build