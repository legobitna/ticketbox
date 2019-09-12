from flask import Flask,render_template,url_for, redirect,request, flash 
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user,login_required #로그인시에 쓰임 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_migrate import Migrate # db 수정용 pip install flask-migrate 먼저 해야함 
from datetime import datetime #DB 에 create 데이 찍을려고 
from flask_wtf import FlaskForm # form  밸리데이트 하기위해 
from wtforms import StringField, SubmitField, PasswordField # 폼에 validate 할때 쓰이는 필드들 
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
import os 