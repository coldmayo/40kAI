set -e
source "../../.venv/bin/activate"

scrapy crawl data -o links.json
python -u addData.py