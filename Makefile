.PHONY: install run check clean

install:
	python -m pip install -r requirements.txt

run:
	streamlit run app.py

check:
	python -m py_compile app.py

clean:
	python -c "import shutil; shutil.rmtree('__pycache__', ignore_errors=True)"
