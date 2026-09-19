import datetime
import pytest
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, validates

from space_station_stc.relic_transmission.validate_dt import SafeDateTime

class Base(DeclarativeBase):
    pass

class ExternalDB(Base):
    __tablename__ = 'external_db'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Model configuration using the custom type
    expires_at: Mapped[datetime.datetime | None] = mapped_column(
        SafeDateTime, 
        index=True, 
        nullable=True
    )

    @validates('expires_at')
    def validate_expires_at(self, key, value):
        # Prevent ORM from writing empty strings or whitespaces
        if isinstance(value, str) and value.strip() == '':
            return None
        return value


@pytest.fixture(scope="function")
def db_session():
    """Set up an in-memory SQLite database and return a session for each test."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    engine.dispose()


class TestExternalDBModelIntegration:

    def test_orm_write_converts_empty_string_to_null(self, db_session):
        """
        GIVEN an ExternalDB model instance initialized with an empty string
        WHEN saving the record to the database via SQLAlchemy ORM
        THEN the model validator should convert it to None and save it as NULL.
        """
        record = ExternalDB(expires_at="   ")
        db_session.add(record)
        db_session.commit()
        
        # Verify that the value stored in the database resolves to None
        db_session.expire_all()
        fetched = db_session.scalar(select(ExternalDB).where(ExternalDB.id == record.id))
        
        assert fetched.expires_at is None

    def test_orm_write_and_read_valid_datetime(self, db_session):
        """
        GIVEN a valid python datetime object
        WHEN saving and retrieving the record via SQLAlchemy ORM
        THEN the datetime object should be preserved exactly.
        """
        test_date = datetime.datetime(2026, 9, 19, 15, 45, 0)
        record = ExternalDB(expires_at=test_date)
        db_session.add(record)
        db_session.commit()
        
        db_session.expire_all()
        fetched = db_session.scalar(select(ExternalDB).where(ExternalDB.id == record.id))
        
        assert fetched.expires_at == test_date

    @pytest.mark.parametrize(
        "corrupted_raw_value",
        [
            "",             # Empty string (the original culprit)
            "   ",          # Spaces
            "corrupted",    # Text garbage
            "0000-00-00",   # Broken ISO format
            "null",         # Text string literal
            "$$@#%!*",      # Special characters
        ]
    )
    def test_model_safely_reads_corrupted_data_from_real_sqlite(self, db_session, corrupted_raw_value):
        """
        GIVEN a raw corrupted text value inserted directly into the SQLite database
        WHEN SQLAlchemy queries the ExternalDB model using the select() statement
        THEN the SafeDateTime decorator must intercept the raw data and return None without crashing.
        """
        # Inject raw corrupted data directly into SQLite bypassing the SQLAlchemy ORM validation layer
        insert_query = text("INSERT INTO external_db (expires_at) VALUES (:val)")
        db_session.execute(insert_query, {"val": corrupted_raw_value})
        db_session.commit()
        
        # Execute the query that originally crashed the application
        db_session.expire_all()
        query_result = db_session.execute(select(ExternalDB)).scalars().all()
        
        # Verify that the application didn't crash and correctly maps the row to None
        assert len(query_result) == 1
        assert query_result[0].expires_at is None
