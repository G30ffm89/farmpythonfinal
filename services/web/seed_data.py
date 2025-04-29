from farm_web_app.mycoos import app, db, user_datastore
from farm_web_app.models.auth import User, Role, WebAuthn
from flask_security.utils import hash_password
from dotenv import load_dotenv
import os 

load_dotenv()


def create_roles():
    
    roles = ['user', 'unauth', 'admin']
    try:
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=role_name.capitalize())
                db.session.add(role)
    except Exception as e:
        print(f"error: {e}")
    db.session.commit()
    print

def create_admin_user():
    with app.app_context():
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        admin_username = os.getenv('ADMIN_USERNAME')
        user_datastore.create_user(
        username=admin_username,
        email=admin_email,
        password=hash_password(admin_password),
        roles=['admin']
    )

        db.session.commit()
        print("Admin user created successfully!")

def create_user_1():
    with app.app_context():
        test1_email = os.getenv('TEST1_EMAIL')
        test1_password = os.getenv('TEST1_PASSWORD')
        test1_username = os.getenv('TEST1_USERNAME')
        user_datastore.create_user(
        username=test1_username,
        email=test1_email,
        password=hash_password(test1_password),
        roles=['user']
    )
        db.session.commit()

def create_user_2():
    with app.app_context():
        test2_email = os.getenv('TEST2_EMAIL')
        test2_password = os.getenv('TEST2_PASSWORD')
        test2_username = os.getenv('TEST2_USERNAME')
        user_datastore.create_user(
        username=test2_username,
        email=test2_email,
        password=hash_password(test2_password),
        roles=['unauth']
    )

        db.session.commit()
        print("Admin user created successfully!")


  