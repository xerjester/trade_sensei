"""CLI: batch Prophet training for all stocks."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.services.predictor_service import run_batch_train_all

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        result = run_batch_train_all()
        print(
            f"Done: {result['success_count']} ok, {result['failed_count']} failed"
        )
        for f in result['failed']:
            print(f"  - {f['symbol']}: {f['error']}")
