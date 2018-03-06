import time
from flask_script import Manager
from app import create_app, db
from app.models.todo import Todo
from app.api_v1.webhook import list_todo_items, handle_message

app = create_app()
manager = Manager(app)

@manager.command
def createdb():
    db.create_all()

@manager.command
def dropdb():
    db.drop_all()

@manager.command
def resetdb():
    db.drop_all()
    db.create_all()

@manager.command
def makeAdmin(user_id):
    time_start = time.time()
    from app.models.user import User
    user = User.query.get(user_id)
    user.isAdmin = True
    db.session.add(user)
    db.session.commit()
    time_end = time.time()
    print("user :",user.username,"is now admin. \n")
    print("temps nécessaire =",str(time_end - time_start),"seconds. \n")

@manager.command
def scheduleTask():
    t = "i am a scheduled action, yeah"
    print(t)
    app.logger.debug(t)

@manager.command
def get_list_by_user_id():
    userIdList = db.session.query(Todo.user_id).distinct()
    for userId in userIdList:
        resp = list_todo_items(userId)
        print(resp)
        send_message(userId,resp)
        

# manager's doc = https://flask-script.readthedocs.io/en/latest/

if __name__ == "__main__":
    manager.run()
