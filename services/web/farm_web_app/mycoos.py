import uuid
from flask import Flask, render_template, url_for, redirect, session, flash, request, jsonify, Response, send_from_directory
from flask_security import (SQLAlchemyUserDatastore, Security, current_user, logout_user, auth_required, roles_required, roles_accepted)
from farm_web_app.config import DevConfig, ProdConfig
from farm_web_app.database import db
from farm_web_app.information import get_latest_data, get_last_10_data
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from flask_mail import Mail, Message
import os
from flask_sqlalchemy import SQLAlchemy
from farm_web_app.models.auth import User, Role, WebAuthn, roles_users
from flask_security.signals import user_registered
from dotenv import load_dotenv 

load_dotenv()
app = Flask(__name__)
state = os.getenv("STATE")

if state == 'development':
    app.config.from_object('config.DevConfig')
elif state == 'production':
    app.config.from_object('config.ProdConfig')

db.init_app(app)

  

mail = Mail(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role, WebAuthn)
security = Security(app, user_datastore)

mail = Mail(app)


@app.route("/robots.txt")
def send_robots():
    return send_from_directory("static", "robots.txt")

@user_registered.connect_via(app)
def user_registered_sighandler(sender, user, **extra):
    unauth_role = Role.query.filter_by(name='unauth').first()
    if unauth_role:
        user.roles.append(unauth_role)
        db.session.commit()
    return user

def get_users_by_role(role_id):
    users = []
    role_users = db.session.query(roles_users).filter_by(role_id=role_id) 
    for role_user in role_users:
        user = User.query.filter_by(id=role_user.user_id).first()
        users.append(user)# adds to array
    return users


@app.route('/admin/force_logout/<int:user_id>')
@auth_required('token', 'session')
@roles_required('admin')  
def force_logout(user_id):
    user = User.query.get_or_404(user_id)

    user.fs_uniquifier = str(uuid.uuid4()) #resets the fs_uniquifer in the user table forcing the user to logout
    db.session.commit()

    flash(f'User {user.email} will be need to relogin')
    return redirect(url_for('home'))

@app.route("/admin/authorise_user/<int:user_id>")
@auth_required('token', 'session')
@roles_required('admin')
def authorise_user(user_id):
    user = User.query.get_or_404(user_id)

    unauth_role = Role.query.filter_by(name='unauth').first()
    user_role = Role.query.filter_by(name='user').first()

    if unauth_role and user_role:
        if unauth_role in user.roles:
            user.roles.remove(unauth_role)
        if user_role not in user.roles:
            user.roles.append(user_role)  
        db.session.commit()
        flash('User authorised successfully.', 'success')
    else:
        flash('One or both roles not found.', 'danger')
    db.session.refresh(user)
    return redirect(url_for('home'))

@app.route("/admin/unauthorise_user/<int:user_id>")
@auth_required('token', 'session')
@roles_required('admin')
def unauthorise_user(user_id):
    user = User.query.get_or_404(user_id)

    unauth_role = Role.query.filter_by(name='unauth').first() 
    user_role = Role.query.filter_by(name='user').first() 

    if unauth_role and user_role: 
        if user_role in user.roles:
            user.roles.remove(user_role) 
        if unauth_role not in user.roles:
            user.roles.append(unauth_role) 
        db.session.commit()
        flash('User unauthorised successfully.', 'success')
    else:
        flash('One or both roles not found.', 'danger')
    
    db.session.refresh(user)
    return redirect(url_for('home'))



@app.route('/admin/delete_user/<int:user_id>')# takes user id 
@auth_required('token', 'session')
@roles_required('admin') 
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id) # returns the error if user id is not found 
        db.session.query(roles_users).filter_by(user_id=user_id).delete() #removes user role

        db.session.delete(user) #delete user from usr table
        db.session.commit()

        return redirect(url_for('home')) 
    except Exception as e:
        return jsonify({'error': str(e)}), 500

        

@app.route("/")
@auth_required('token', 'session')
@roles_accepted('admin', 'user') 
def home():
    date, time, temperature, humidity, heat_mat_state, mister_state, pump_state ,inline_fan_state, led_state  = get_latest_data()
    if current_user.has_role('admin'):
        if current_user.has_role('admin'):
            unauth_users = get_users_by_role(2)
            standard_users = get_users_by_role(1)
            admin_users = get_users_by_role(3) # for template
            
            # prevents crash if there are no users of a type
            unauth_users = [user for user in unauth_users if user is not None]
            standard_users = [user for user in standard_users if user is not None]
            admin_users = [user for user in admin_users if user is not None]
            temp=temperature
            return render_template('home.html', u_users=unauth_users, s_users=standard_users, 
                           current_user=current_user ,admin_users= admin_users)
         
    elif current_user.has_role('unauth'):
        flash("Your account has not yet been approved by an admin")
        return redirect(url_for('profile')) 
    else:
        return render_template('home.html')
    
@app.route('/_get_initial_data')
@auth_required('token', 'session')
@roles_accepted('admin', 'user') 
def get_initial_data():
  try:
    initial_data = get_last_10_data() 
    return jsonify({'initial_data': initial_data})
  except Exception as e:
    return jsonify({'error': str(e)}), 500


@app.route("/logout")
@auth_required('token', 'session')
@roles_accepted('admin', 'user') 
def logout():
    logout_user()

@app.route("/profile")
@auth_required('token', 'session')
@roles_accepted('admin', 'user', 'unauth') 
def profile():
    return render_template('profile.html')

@app.route('/_get_data')
@auth_required('token', 'session')
@roles_accepted('admin', 'user') 
def get_data():
    data = get_latest_data()
    if data[0] is not None:
        return jsonify({
            'date': data[0], #highchart line graph
            'time': data[1], #highchart line graph
            'temperature': data[2],
            'humidity': data[3],
            'box_fan_state' : data[4],
            'mister_state': data[5],
            'inline_fan_state': data[6],
            'pump_state': data[7]

        })
    else:
        return jsonify({'error': 'No data available'}), 404


def get_latest(directory="/usr/src/app/farm_web_app/images"):

  image_files = [
      f for f in os.listdir(directory) if f.endswith((".jpg"))
  ]
  if image_files:
      newest_image = max(
          image_files,
          key=lambda f: os.path.getctime(os.path.join(directory, f)),
      )
      return newest_image
  return None

@app.route('/_get_image')
@auth_required('token', 'session')
@roles_accepted('admin', 'user') 
def get_image():
  newest_image = get_latest()
  if newest_image:
      return send_from_directory("images", newest_image)
  else:
      return jsonify({"error": "No images found"}), 404

