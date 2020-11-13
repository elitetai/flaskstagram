import peewee as pw
from peewee import Check
from models.base_model import BaseModel
from models.user import User
from models.image import Image

class Payment(BaseModel):
    sender = pw.ForeignKeyField(User, backref="payments")
    image = pw.ForeignKeyField(Image, backref="payments")
    amount = pw.DecimalField(decimal_places=2, constraints=[Check('amount > 9')])