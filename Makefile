.PHONY: venv install deploy-streamlit


venv:
	if [ ! -d "venv" ]; then \
		python3 -m venv venv; \
	fi

install: venv
	. venv/bin/activate; \
	pip install -r requirements.txt

deploy-streamlit:
	. venv/bin/activate; \
	streamlit run app.py
