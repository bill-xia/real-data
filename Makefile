all: server

.PNOHY: server

server:
	python3 generate_site.py
	cd data; find . -name "*.csv"
	cd data; find . -name "*.csv" -exec cp --parents {} ../build/charts \;
	python3 -m http.server -d . 26919

clean:
	rm -rf build