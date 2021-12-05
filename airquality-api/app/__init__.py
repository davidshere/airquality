from flask import Flask


def create_app(flask=Flask, test_config=None):
    # create and configure the app
    app = flask(
        __name__,
        instance_relative_config=True,
        template_folder='../build',
        static_folder='../build/static/'
    )

    app.config.from_mapping(
        SECRET_KEY='dev',
    ) 
  

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    from app import views 
    app.register_blueprint(views.bp)

    return app

