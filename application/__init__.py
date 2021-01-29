import os

from flask import Flask

import click
from flask.cli import with_appcontext 


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database
    from application import db
    db.init_app(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from application import trainer
    app.register_blueprint(trainer.bp)

    # set trainer blueprint to index (no url_prefix)
    app.add_url_rule('/', endpoint='index')

    # add click command
    from application.internal_api import upload_craw_csv
    @app.cli.command('upload-craw-csv')
    @click.argument('filename')
    def upload_craw_csv_command(filename):
        """Clear the existing data and create new tables."""
        upload_craw_csv(filename)
        click.echo(f'Uploaded {filename} data to database.')

    return app
