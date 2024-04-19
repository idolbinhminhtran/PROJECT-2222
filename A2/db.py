'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *
from datetime import datetime


from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

msg_counter = MessageCounter()

# inserts a user to the database
def insert_user(username: str, hash: str, salt: str):
    with Session(engine) as session:
        user = User(username=username, hash=hash, salt=salt)
        session.add(user)
        session.commit()

def insert_association(left_user_id: str, right_user_id: str, status: str):
    with Session(engine) as session:
        association = Association(left_user_id=left_user_id, right_user_id=right_user_id, status=status)
        session.add(association)
        session.commit()

def insert_message(room_id: str, text: str):
    id = str(msg_counter.get_counter())
    with Session(engine) as session:
        message = Message(id=id, room_id=room_id, text=text)
        session.add(message)
        session.commit()
        
# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)
    
def get_salt(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        return user.salt
    
def get_friends(username: str, status: str):
    with Session(engine) as session:
        friends_left_query = session.query(User.username).join(Association, User.username == Association.right_user_id).filter(Association.left_user_id == username, Association.status == status)
        friends_right_query = session.query(User.username).join(Association, User.username == Association.left_user_id).filter(Association.right_user_id == username, Association.status == status)
        friends = friends_left_query.union(friends_right_query).all()

        return [friend.username for friend in friends]
    
def get_invitation_sented_list(username: str):
    with Session(engine) as session:
        friends = session.query(User.username).join(Association, User.username == Association.right_user_id).filter(Association.left_user_id == username, Association.status == "1").all()
        return [friend.username for friend in friends]
    
def get_invitation_received_list(username: str):
    with Session(engine) as session:
        friends = session.query(User.username).join(Association, User.username == Association.left_user_id).filter(Association.right_user_id == username, Association.status == "1").all()
        return [friend.username for friend in friends]
    
def modify_association_status(username: str, friend_name: str, new_status: str):
    with Session(engine) as session:
        association = session.query(Association).filter(
        ((Association.left_user_id == username) & (Association.right_user_id == friend_name)) | 
        ((Association.left_user_id == friend_name) & (Association.right_user_id == username))
        ).first()
        association.status = new_status
        session.commit()


