from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    # Attributes
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Relationships
    recipes = relationship('Recipe', backref='user', lazy=True)

    # SerializerMixin config (if you want to hide the password hash in serialized data)
    serialize_rules = ('-recipes.user', '-_password_hash')

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes are not readable.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    @validates('username')
    def validate_username(self, key, username):
        assert username is not None, "Username must be present."
        return username
    
    
class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    # Attributes
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    # Foreign key linking the recipe to a user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # SerializerMixin config (if you want to hide the user in serialized data)
    serialize_rules = ('-user.recipes',)

    @validates('title')
    def validate_title(self, key, title):
        assert title is not None, "Title must be present."
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        assert instructions is not None, "Instructions must be present."
        assert len(instructions) >= 50, "Instructions must be at least 50 characters long."
        return instructions

