"""One-time reset: legacy approval flags were not enforced in the prior release."""
from sqlalchemy import update
from .models import SchemaMigration, Medicine

def apply(db):
    if db.get_bind().dialect.name=='postgresql':
        from sqlalchemy.dialects.postgresql import insert
    else:
        from sqlalchemy.dialects.sqlite import insert
    result=db.execute(insert(SchemaMigration).values(name='v4_review_medicine_sources').on_conflict_do_nothing())
    if result.rowcount:
        db.execute(update(Medicine).values(approved=False,approved_by=None))
    db.commit()
