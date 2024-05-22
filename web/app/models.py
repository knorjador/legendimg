
import sqlalchemy as sa
import sqlalchemy.orm as so

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from hashlib import md5
from typing import Optional

from app import db, login

class Member(UserMixin, db.Model):
    id: so.Mapped[int] = sa.Column(sa.Integer, primary_key=True, nullable=False)
    name: so.Mapped[str] = sa.Column(sa.String(256), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = sa.Column(sa.String(256))
    history: so.Mapped['History'] = so.relationship('History', back_populates='member')

    def __repr__(self):
        return '<Member {}>'.format(self.name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class History(UserMixin, db.Model):
    id: so.Mapped[int] = sa.Column(sa.Integer, primary_key=True, nullable=False)
    caption: so.Mapped[str] = sa.Column(sa.Text)
    trad: so.Mapped[str] = sa.Column(sa.Text)
    sentiment: so.Mapped[str] = sa.Column(sa.String(256))
    img: so.Mapped[str] = sa.Column(sa.Text)
    member_id: so.Mapped[int] = sa.Column(sa.ForeignKey(Member.id), index=True)
    member: so.Mapped[Member] = so.relationship('Member', back_populates='history')

    def __repr__(self):
        return '<Image( caption={}, trad={}, img={})>'.format(self.caption, self.trad, self.img)


@login.user_loader
def load_user(id):
    return db.session.get(Member, int(id))



