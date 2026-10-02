"""CLI: batch scrape all target stocks (Admin pipeline)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.services.scraper_service import run_batch_scrape

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        total = run_batch_scrape()
        print(f'Batch scrape finished. New price records: {total}')
