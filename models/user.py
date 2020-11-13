import peewee as pw
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from playhouse.hybrid import hybrid_property
from models.base_model import BaseModel

class User(BaseModel, UserMixin):
    username = pw.CharField(unique=True)
    email = pw.CharField(unique=True)
    password = None
    hashed_password = pw.TextField(null=True)
    image_path = pw.TextField(null=True)
    is_private = pw.BooleanField(default=False)

    @hybrid_property
    def sorted_images(self):
        from models.image import Image
        return Image.select().where(Image.user == self).order_by(Image.created_at.desc())

    def follow(self, idol): 
        from models.fanidol import FanIdol
        # check whether the relationship already existed
        if self.id != idol.id:
            if self.follow_status(idol) == None:
                relationship = FanIdol(fan=self.id, idol=idol)
                if not idol.is_private:
                    relationship.is_approved = True
                return relationship.save()
        else:    
            return 0
    
    def follow_status(self,idol):
        from models.fanidol import FanIdol
        return FanIdol.get_or_none(FanIdol.fan==self.id, FanIdol.idol==idol.id)

    def approve_request(self, fan):
        from models.fanidol import FanIdol
        # get the relationship
        relationship = fan.follow_status(self)
        # update the is_approved to true
        relationship.is_approved = True
        return relationship.save()

    def unfollow(self, idol):
        from models.fanidol import FanIdol
        return FanIdol.delete().where(FanIdol.fan==self.id, FanIdol.idol==idol).execute()

    @hybrid_property
    def idols(self):
        from models.fanidol import FanIdol
        # get a list of idol users
        idols = FanIdol.select(FanIdol.idol).where(FanIdol.fan==self.id, FanIdol.is_approved==True)
        return User.select().where(User.id.in_(idols))

    @hybrid_property
    def idol_requests(self):
        from models.fanidol import FanIdol
        idols = FanIdol.select(FanIdol.idol).where(FanIdol.fan==self.id, FanIdol.is_approved==False)
        return User.select().where(User.id.in_(idols))

    @hybrid_property
    def fans(self):
        # get a list fan users
        from models.fanidol import FanIdol
        fans = FanIdol.select(FanIdol.fan).where(FanIdol.idol==self.id, FanIdol.is_approved==True)
        return User.select().where(User.id.in_(fans))

    @hybrid_property
    def fan_requests(self):
        from models.fanidol import FanIdol
        fans = FanIdol.select(FanIdol.fan).where(FanIdol.idol==self.id, FanIdol.is_approved==False)
        return User.select().where(User.id.in_(fans))


    @hybrid_property
    def full_image_path(self):
        from app import app
        if self.image_path:
            return app.config.get('S3_LOCATION') + self.image_path
        else: 
            return app.config.get('S3_LOCATION') + "default.png"

    def validate(self):
        # Must fill in the fields provided
        if self.username.strip()=="" or self.email.strip()=="":
            self.errors.append("You can't leave empty fields!")


        # Check for case-insensitive username
        def check_duplicate_username(self):
            for user in User.select():
                result = re.search(self.username, user.username, re.IGNORECASE)
                if result:
                    return user
                    break
            else:
                return None

        # Username should be unique
        if check_duplicate_username(self) and check_duplicate_username(self).id != self.id:
            self.errors.append(f'{self.username} has already existed!')

        # Email should be unique
        existing_email = User.get_or_none(User.email == self.email)
        if existing_email and existing_email.id != self.id:
            self.errors.append(f'{self.email} has already existed')

        # Check if there's password
        if self.password != None:
        # Password should be longer than 5 characters
            if len(self.password) <= 5:
                self.errors.append('Password must be longer than 5 characters')
            
            if self.hashed_password:
                if check_password_hash(self.hashed_password, self.password):
                    self.errors.append('The password must not be the same as current!')

            # Password should have consists of both uppercase and lowercase characters, digit and at least one special character 
            has_lower = re.search(r"[a-z]", self.password)
            has_upper = re.search(r"[A-Z]", self.password)
            has_digit = re.search(r"[0-9]", self.password)
            has_special = re.search(r"[\!\@\#\$\%\^\&\*\(\)\_\+\=\[\]]", self.password)

            if has_lower and has_upper and has_digit and has_special:
                self.hashed_password = generate_password_hash(self.password)
            else:
                self.errors.append('The password must consists of one upper, lower, special character and digit each!')

            


