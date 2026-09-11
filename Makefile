.PHONY: install run check test clean

install:
	python -m pip install -r requirements.txt

run:
	streamlit run app.py

check:
	python -m py_compile app.py

test:
	python -m unittest discover -s tests -v

clean:
	python -c "import shutil; shutil.rmtree('__pycache__', ignore_errors=True)"
