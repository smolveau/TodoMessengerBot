import requests, json
from flask import Response, request, current_app
from . import api
from .. import db
from ..controllers.todo import add_todo_item, list_todo_items, delete_todo_item, find_todo_items
from ..controllers.user import change_reminder, get_status
import os

verify_token = os.getenv('FB_VERIFY_TOKEN', None)
access_token = os.getenv('FB_ACCESS_TOKEN', None)


@api.route('/privacy', methods=['GET'])
def privacy():
    # needed route if you need to make your bot public
    return "This facebook messenger bot's only purpose is to list your things and remind you of doing it. That's all. We don't use it in any other way."


@api.route('/webhook', methods=['GET'])
def webhook_verify():
    if request.args.get('hub.verify_token') == verify_token:
        return request.args.get('hub.challenge')
    return "Wrong verify token"


@api.route('/webhook', methods=['POST'])
def webhook_action():
    data = json.loads(request.data.decode('utf-8'))
    for entry in data['entry']:
        try:
            user_message = entry['messaging'][0]['message']['text']
        except KeyError:
            continue
        user_id = entry['messaging'][0]['sender']['id']
        text = action(user_id, user_message)
        send_message(user_id, text)
    return Response(response="EVENT RECEIVED",status=200)


def action(user_id, user_message):
    message_parsed = user_message.split()
    action = message_parsed[0]

    if action in ["/add", "/a"]:
        if len(message_parsed) < 2:
            return "sorry your todo item is empty ¯\_(ツ)_/¯"
        todo_item_content = " ".join(message_parsed[1:])
        return add_todo_item(user_id, todo_item_content)

    if action in ["/list", "/l"]:
        return list_todo_items(user_id)

    if action in ["/delete", "/d"]:
        if len(message_parsed) < 2:
            return "sorry your todo item ID is empty ¯\_(ツ)_/¯"
        try:
            todo_item_id = int(message_parsed[1])
        except ValueError:
            return "sorry your todo item ID is not valid ¯\_(ツ)_/¯"
        return delete_todo_item(user_id, todo_item_id)

    if action in ["/remind", "/r"]:
        if len(message_parsed) < 2:
            return "sorry the reminder hours is empty ¯\_(ツ)_/¯"
        try:
            remind_timer_hours = int(message_parsed[1])
        except ValueError:
            return "sorry the reminder is not valid, it should be a number of hours ¯\_(ツ)_/¯"
        return change_reminder(user_id, remind_timer_hours)

    if action in ["/status", "/s"]:
        return get_status(user_id)

    if action in ["/find", "/f"]:
        if len(message_parsed) < 2:
            return "sorry your search is empty ¯\_(ツ)_/¯"
        search = message_parsed[1]
        return find_todo_items(user_id, search)

    return show_usage()


def show_usage():
    usage = "Please choose between: \n"
    usage += "/a /add, buy some milk -- add a new task \n"
    usage += "/d /delete 1 -- delete task by order \n"
    usage += "/l /list -- list all your tasks \n"
    usage += "/r /remind 4 -- change the remind timer, every X hours \n"
    usage += "/s /status -- get the number of tasks and remind-timer \n"
    usage += "/f /find buy -- find tasks that contains your search \n"
    usage += "thx ! :)"
    return usage

def send_message(user_id, user_message):
    response = {
        'recipient': {'id': user_id},
        'message': {'text': user_message}
    }
    r = requests.post(
        'https://graph.facebook.com/v2.6/me/messages/?access_token=' + access_token, json=response)
