'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db

room = Room()

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))

# send message event handler
@socketio.on("send")
def send(username, message, room_id):
    emit("incoming", (f"{username}: {message}"), to=room_id)
    db.insert_message(str(room_id), message)
    
# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)

    # if the user is already inside of a room 
    if room_id is not None:
        
        room.join_room(sender_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit("incoming", (f"{sender_name} has joined the room.", "green"), to=room_id, include_self=False)
        # emit only to the sender
        emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"))
        return room_id

    # if the user isn't inside of any room, 
    # perhaps this user has recently left a room
    # or is simply a new user looking to chat with someone
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", (f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green"), to=room_id)
    return room_id

@socketio.on("get_salt")
def get_salt(sender_name):
    return db.get_salt(sender_name)

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)

@socketio.on("show friend list")
def show_friend_list(sender_name):
    list_friend = db.get_friends(sender_name, "2")
    print(list_friend)
    return list_friend

#send friend request
@socketio.on("send friend request")
def send_friend_request(sender_name, receiver_name):
    room_id = room.get_room_id(receiver_name)
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver"
    
    db.insert_association(sender_name, receiver_name, "1")
    emit("incoming", (f"{sender_name} successfully send a friend request to {receiver_name}"), to=room_id)

@socketio.on("show invitation sented")
def show_invitation_sented(sender_name):
    list_of_invitation_sented = db.get_invitation_sented_list(sender_name)
    return list_of_invitation_sented

@socketio.on("show invitation received")
def show_invitation_received(sender_name):
    list_of_invitation_received = db.get_invitation_received_list(sender_name)
    return list_of_invitation_received

@socketio.on("accept friend request")
def accept_friend_request(user_name, friend_name):
    db.modify_association_status(user_name, friend_name, "2")

@socketio.on("decline friend request")
def accept_friend_request(user_name, friend_name):
    db.modify_association_status(user_name, friend_name, "0")


    



# @socketio.on("accept friend request")

    



