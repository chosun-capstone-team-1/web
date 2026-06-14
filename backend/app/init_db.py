import time

from sqlalchemy.exc import OperationalError

from app.database.connection import engine
from app.db_persistence.analysis import Base as AnalysisBase
import app.db_model.users  # noqa: F401 - register User model on metadata


def init_db(max_attempts: int = 10, delay_seconds: int = 2) -> None:
	last_error = None
	for attempt in range(1, max_attempts + 1):
		try:
			AnalysisBase.metadata.create_all(bind=engine)
			return
		except OperationalError as exc:
			last_error = exc
			if attempt < max_attempts:
				time.sleep(delay_seconds)
			else:
				raise

	if last_error is not None:
		raise last_error
