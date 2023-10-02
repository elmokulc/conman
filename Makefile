install:
	python setup.py install ; \
	$(MAKE) clean

dev-install:
	pip install --editable . ; \
	$(MAKE) clean

reinstall:
	$(MAKE) remove
	$(MAKE) dev-install

clean:
	rm -rf build conman.egg-info dist

remove:
	pip uninstall -y conman

sdist:
	python setup.py sdist ; \
	echo "conman sdist created."

bdist:
	python setup.py bdist_wheel --universal; \
	echo "conman universal bdist created."

help:
	@echo "install - install conman"
	@echo "dev-install - install conman in development mode"
	@echo "clean   - clean up build files"
	@echo "remove  - remove conman"
	@echo "sdist   - create a source distribution"
	@echo "bdist   - create a universal wheel"
	@echo "help    - print this help message"