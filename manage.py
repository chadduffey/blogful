import os
from flask_script import Manager

from blog import app

manager = Manager(app)

@manager.command
def run():
    app.run()

if __name__ == '__main__':
    manager.run()