#!/usr/bin/env python

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from oonipipeline.app import create_app
from oonipipeline.models import db


app = create_app('oonipipeline.config')

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
