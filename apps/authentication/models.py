# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
import pandas as pd

from sqlalchemy.orm import relationship
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from apps import login_manager

from apps.authentication.util import hash_pass

users = [{'id': 1, 'username': "don", "email": "muralidharb@gmail.com",
          "password": "xxx" , "oauth_github": "asfafasd"}]

df = pd.DataFrame(users)

class Users():

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

    def get_id(self):
        return self.id       

    @classmethod
    def find_by_email(cls, email: str) -> "Users":
        found = df.loc[df['email'] == email]
        if found.empty:
            return None
        kwargs = found.iloc[0].to_dict()
        return Users(**kwargs)

    @classmethod
    def find_by_username(cls, username: str) -> "Users":
        found = df.loc[df['username'] == username]
        if found.empty:
            return None
        kwargs = found.iloc[0].to_dict()
        return Users(**kwargs)
    
    @classmethod
    def find_by_id(cls, _id: int) -> "Users":
        found = df.loc[df['id'] == id]
        if found.empty:
            return None
        kwargs = found.iloc[0].to_dict()
        return Users(**kwargs)
   
    def save(self) -> None:
        df.to_csv("users.csv")
    
    def delete_from_db(self) -> None:
        # Drop the row
        return

    def is_active(self) -> bool:
        return True

    def is_authenticated(self) -> bool:
        return True

@login_manager.user_loader
def user_loader(id):
    user = df.loc[df['id'] == id]
    if user.empty:
        return None
    kwargs = user.iloc[0].to_dict()
    return Users(**kwargs)

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = df.loc[df['username'] == username]
    if user.empty:
        return None
    kwargs = user.iloc[0].to_dict()
    return Users(**kwargs)

class OAuth():
    pass
