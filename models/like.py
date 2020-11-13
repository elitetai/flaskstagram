import peewee as pw
from models.base_model import BaseModel
from models.user import User
from models.image import Image
from playhouse.hybrid import hybrid_property

class Like(BaseModel):
    image = pw.ForeignKeyField(Image, backref="likes", on_delete="CASCADE")
    fan = pw.ForeignKeyField(User, backref="likes", on_delete="CASCADE")

    @hybrid_property
    def total_likes(self):
        return Like.select().where(Like.image==self.image)