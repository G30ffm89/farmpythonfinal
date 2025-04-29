from flask_security.models import fsqla_v3 as fsqla
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref, mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr
from farm_web_app.database import db

fsqla.FsModels.db = db
# models 
class Role(db.Model, fsqla.FsRoleMixin):
    pass

class WebAuthn(db.Model, fsqla.FsWebAuthnMixin):
    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("user.id", ondelete="CASCADE")
        )
    user = relationship("User", back_populates="webauthn") 
    pass

class User(db.Model, fsqla.FsUserMixin):
    username = db.Column(db.String(255), unique=True, nullable=True)
    active = db.Column(db.Boolean(), default=False)
    confirmed_at = db.Column(db.DateTime())
    @declared_attr
    def webauthn(cls):
        return relationship(
            "WebAuthn", back_populates="user", cascade="all, delete"
        )
    roles = relationship(
        "Role", secondary="roles_users", backref=backref("users", lazy="dynamic")
    )
    pass
class roles_users(db.Model):
    __tablename__ = "roles_users"
    id = Column(Integer(), primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey("user.id"))
    role_id = Column("role_id", Integer(), ForeignKey("role.id"))

