from datetime import datetime

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app import db


class Indicator(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    name = db.Column(db.String(120), nullable=False, index=True)
    source = db.Column(db.JSON(), nullable=False)
    unit = db.Column(db.String(20), nullable=False, default='')

    product_id = db.Column(db.Integer(), db.ForeignKey('product.id'), nullable=False)

    targets = db.relationship('Target', backref=db.backref('indicator', lazy='joined'), lazy='dynamic')
    values = db.relationship('IndicatorValue', backref='indicator', lazy='dynamic', cascade="all, delete")

    username = db.Column(db.String(120), default='')
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('name', 'product_id', name='indicator_name_product_id_key'),
    )

    def __repr__(self):
        return '<SLI %s | %s>'.format(self.product.name, self.name)


class IndicatorValue(db.Model):
    __tablename__ = 'IndicatorValue'

    timestamp = db.Column(db.DateTime(), nullable=False)
    value = db.Column(db.Numeric(), nullable=False)

    indicator_id = db.Column(db.Integer(), db.ForeignKey('indicator.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('timestamp', 'indicator_id', name='indicatorvalue_timestamp_indicator_id_pkey'),
    )

    def as_dict(self):
        return {
            'timestamp': self.timestamp,
            'value': self.value,
            'indicator_id': self.indicator_id
        }

    def update_dict(self):
        return {'value': self.value}

    def __repr__(self):
        return '<SLI value %s | %s: %s>'.format(self.indicator.name, self.timestamp, self.value)


# Source: http://stackoverflow.com/questions/41636169/how-to-use-postgresqls-insert-on-conflict-upsert-feature-with-flask-sqlal  # noqa
def insert_indicator_value(session: db.Session, sli_value: IndicatorValue) -> None:
    """
    Upsert indicator value.

    Note: Does not perform ``session.commit()``.
    """
    statement = (
        pg_insert(IndicatorValue)
        .values(**sli_value.as_dict())
        .on_conflict_do_update(constraint='indicatorvalue_timestamp_indicator_id_pkey', set_=sli_value.update_dict())
    )

    session.execute(statement)
