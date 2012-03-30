push:
	git commit -a 
	git push

pull:
	git pull 

install:
	sudo easy_install dist/futuregrid.cloud.metric-*.egg 

pip:
	make -f Makefile distall
	sudo pip install dist/futuregrid.cloud.metric-*.tar.gz 

upgrade:
	make -f Makefile distall
	sudo pip install --upgrade dist/futuregrid.cloud.metric-*.tar.gz 


distall:
	make -f Makefile egg
	make -f Makefile tar
#	make -f Makefile rpm


gitgregor:
	git config --global user.name "Gregor von Laszewski"
	git config --global user.email laszewski@gmail.com

# #####################################################################
# Creating the distribution
# #####################################################################
egg:
	python setup.py bdist_egg

tar:
	python setup.py sdist

rpm:
	python setup.py bdist_rpm


clean:
	pip uninstall dist/futuregrid.cloud.metric-*.tar.gz
	rm -rf build dist *.egg-info *~ \#*
