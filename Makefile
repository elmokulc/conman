install:
	python setup.py install ; \
	$(MAKE) clean

clean:
	rm -rf build conman.egg-info dist

remove:
	pip uninstall -y conman

help:
	@echo "install - install conman"
	@echo "clean   - clean up build files"
	@echo "remove  - remove conman"
	@echo "help    - print this help message"