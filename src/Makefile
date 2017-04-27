dependencies:
	virtualenv venv
	test -h gaelib || ln -s venv/lib/python2.7/site-packages gae-lib
	source venv/bin/activate ; \
	pip install -r requirements.txt ; \
	deactivate

clean:
	rm -rf venv
	rm -f gaelib
	rm -f *.pyc
	rm -f */*.pyc