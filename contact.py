from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

sqldb = SQLAlchemy()  # type: ignore


class Contact(sqldb.Model):  # type: ignore
    __tablename__ = "Contact"

    id = sqldb.Column(sqldb.Integer, primary_key=True, autoincrement=True)

    phoneNumber = sqldb.Column(sqldb.String, nullable=True)
    email = sqldb.Column(sqldb.String, nullable=True)

    linkedId = sqldb.Column(sqldb.Integer, nullable=True)

    linkPrecedence = sqldb.Column(sqldb.String, nullable=False)

    createdAt = sqldb.Column(
        sqldb.DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
    )

    updatedAt = sqldb.Column(
        sqldb.DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    deletedAt = sqldb.Column(sqldb.DateTime, nullable=True)
