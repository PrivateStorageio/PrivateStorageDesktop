.DEFAULT_GOAL := source
SHELL := /bin/bash

clean:
	rm -rf privatestorage

source:
	git clone --depth 1 -b 290.new-magic-folder https://github.com/gridsync/gridsync privatestorage
	cp assets/PrivateStorage* privatestorage/images/
	cp assets/PrivateStorage* privatestorage/gridsync/resources/
	cp assets/PrivateStorage.png privatestorage/gridsync/resources/tahoe-lafs.png
	cp privatestorage/gridsync/resources/laptop.png privatestorage/gridsync/resources/laptop-with-icon.png
	cp credentials/*.json privatestorage/gridsync/resources/providers/
	cp build/config.txt privatestorage/gridsync/resources/
	cp build/InnoSetup6.iss privatestorage/misc/
	cp scripts/* privatestorage/
