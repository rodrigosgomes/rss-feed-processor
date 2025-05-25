python -m pytest $args -v --cov=src --cov-report=term-missing --cov-report=html:reports/coverage --html=reports/test_report.html --self-contained-html --junitxml=reports/junit.xml
