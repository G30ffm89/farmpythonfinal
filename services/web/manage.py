from flask.cli import FlaskGroup
from farm_web_app.mycoos import app,db
from seed_data import create_admin_user, create_roles, create_user_1, create_user_2

cli = FlaskGroup(app)

@cli.command("seed")
def seed_db():
    """Seeds the database."""
    with app.app_context():
        db.create_all()
        create_roles()
        create_admin_user()
        print("Seeded the database.")


@cli.command("user1")
def user1():
    with app.app_context():
        create_user_1()
        print("User 1")

@cli.command("user2")
def user2():
    with app.app_context():
        create_user_2()
        print("User 2")

if __name__ == "__main__":
    cli()

