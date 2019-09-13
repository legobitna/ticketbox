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
from flask_admin import Admin # 어드민 페이지를 제공하는 라이브러리 pip install flask_admin  설치필요 
from flask_admin.contrib.sqla import ModelView 
from sqlalchemy import func
#setting
app=Flask(__name__)
app.config['FLASK_ADMIN_SWATCH']='cerulean'#어드민 페이지를 위해 추가 
app.secret_key="total secret"
admin=Admin(app,name='my app', template_mode='bootstrap3') #어드민 페이지를 위해 추가 



#로그인 세팅
login=LoginManager(app)
login.login_view="login"
db=SQLAlchemy(app)

#DB 세팅
db=SQLAlchemy(app)
migrate=Migrate(app,db)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
# POSTGRES = {
#     'user': 'bitna',
#     'pw': '1234',
#     'db': 'ticketbox',
#     'host': 'localhost',
#     'port': 5000,
# }
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:\
# %(port)s/%(db)s' % POSTGRES


class Users(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True)
    password_hash=db.Column(db.String,nullable=False)
    username=db.Column(db.String, unique=True)
    tickests= db.relationship('Tickets', backref="users", lazy="dynamic")
    orders= db.relationship('Orders', backref="users", lazy="dynamic")

    def set_password(self, password):  # 패스워드를 그대로 저장하는게아닌 해쉬함수로 암호화시켜서 저장하기 때문에 필요 
        self.password_hash=generate_password_hash(password)
    
    def check_password(self, password): #내가 입력한 패스워드가 디비에 저장된 값과 같은지 확인하기위해 만듬 
        return check_password_hash(self.password_hash,password)
    
    def __repr__(self):  # 릴레이션십과 외래키  관계를 보여줌 
        return '<Users %r>' % self.username
class Events(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String)
    address=db.Column(db.String)
    date=db.Column(db.String)
    types=db.relationship('Types',backref="events",lazy="dynamic")


class Types(db.Model): # 테이블이름으로 언더바나 중간에 대문자 쓰면 forgien key reference 에러남 
    id=db.Column(db.Integer,primary_key=True)
    type_name=db.Column(db.String)
    event_id=db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    price=db.Column(db.Integer)
    qty=db.Column(db.Integer)
    tickets=db.relationship('Tickets', backref="types", lazy="dynamic")


class Orders(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    create_at=db.Column(db.DateTime, nullable=False)
    tickets=db.relationship('Tickets', backref="orders", lazy="dynamic")

class Tickets(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id=db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    type_id=db.Column(db.Integer, db.ForeignKey('types.id'), nullable=False)
    create_at=db.Column(db.DateTime, nullable=False)
 
#admin 페이지에 테이블볼 수 있는 메뉴 추가하기  
admin.add_view(ModelView(Users,db.session)) # 어드민페이지에 메뉴가 생김 user 테이블 볼수있음 
admin.add_view(ModelView(Tickets,db.session))
db.create_all()  #DB 테이블 생성

#form  정의하기 
class Register(FlaskForm): # 회원가입시 이메일이 유니크인지 유저내임에 유니크인지 패스워드와 컨펌 패스워드가 같은지 확인 
    username=StringField("User name", validators=[DataRequired("please input your user name"), Length(min=3, max=20, message="username must have at least 3 char and max 20 chars")])
    email=StringField("Email address", validators=[DataRequired(),Email("please input an appropriate email address")])
    password=StringField("password", validators=[DataRequired(),EqualTo("confirm")])
    confirm=StringField("confirm password", validators=[DataRequired()])
    submit=SubmitField("register")

    def validate_username(self,field): #유저내임 유니크인지 확인 
        if Users.query.filter_by(username=field.data).first():
            raise ValidationError("your name has been registered")
    def validate_email(self, field):# 이메일이 유니크인지 확인 
        if Users.query.filter_by(email=field.data).first():
            raise ValidationError("your email has been registerd")

class Login(FlaskForm): # 로그인 시에 확인해야되는 폼 
    email=StringField("Email address", validators=[DataRequired(),Email("please input an appropriate email address")])
    password=PasswordField("password", validators=[DataRequired()],)
    submit=SubmitField("Login")

class Event(FlaskForm): # 이벤트 등록시 확인해야되는 폼 
    name=StringField("name",validators=[DataRequired("please input your event name"),Length(min=2)])
    address=StringField("address",validators=[DataRequired("please input the event address"),Length(min=2)])
    date=StringField("date",validators=[DataRequired("please input the event date")])
    #country=StringField("country",validators=[DataRequired("please select the coutnry")])
    submit=SubmitField("register")

class Type(FlaskForm):
    type_name=StringField("name",validators=[DataRequired("please input your type name"),Length(min=2)])
    price=StringField("price",validators=[DataRequired("please input the price")])
    qty=StringField("Quantity",validators=[DataRequired("please input the Quantity")])
    submit=SubmitField("register")

@login.user_loader #질문 
def load_user(user_id):
    return Users.query.get(user_id)

@app.route('/register', methods=['POST','GET']) #회원가입 화면 
def register():
    form=Register()
    if request.method=="POST":
        if form.validate_on_submit():
            new_user=Users(username=form.username.data,
                           email=form.email.data,)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            for field_name,errors in form.errors.items():
                flash(errors,'danger')
                return redirect(url_for('register'))
    return render_template('register.html',form=form)

@app.route('/login', methods=['post','get']) #로그인화면 
def login():
    form=Login()
    if request.method=="POST":
       
        check=Users.query.filter_by(email=form.email.data).first()
       
        print(check,"==========================================")
        if check:
            if check.check_password(form.password.data):
                login_user(check)
                return redirect(url_for('home'))
            else:
                flash('wrong password','danger')
                return redirect(url_for('login'))
        else:
             flash('can not find this user','danger')
             return redirect(url_for('register'))
    return render_template('login.html',form=form)

@app.route('/home')
def home():
    data=Events.query.order_by(Events.id).all()
    price=Types.query.with_entities(func.min(Types.price),Types.event_id).group_by(Types.event_id).order_by(Types.event_id).all()
    
    print(price,"00000000000000000000000000000000000000000")    
    return render_template('home.html',data=data,price=price )

@app.route('/registerevent', methods=['post','get'])
def registerevent():
    form=Event()
    form2=Type()
    data=Events.query.filter_by().all()
    if request.method=="POST":
        if form.validate_on_submit():
             event=Events(name=form.name.data,
                          address=form.address.data+","+str(request.form.get('checkout_country')),
                          date=form.date.data)
            
             db.session.add(event)
             db.session.commit()
             flash('successfully registered','success')
             return redirect(url_for('registerevent'))
        elif form2.validate_on_submit():
            type=Types(event_id=request.form.get('checkout_event'),
                       price=form2.price.data,
                       qty=form2.qty.data,
                       type_name=form2.type_name.data)
            db.session.add(type)
            db.session.commit()
            flash('successfully registered','success')
            return redirect(url_for('registerevent'))

        else:
             for field_name,errors in form.errors.items():
                print(errors)
                return redirect(url_for('home'))
        
    return render_template('registerevent.html',form=form,form2=form2,data=data)

@app.route('/details/<event_id>', methods=['post','get'])# 상품 상세페이지 
def detail(event_id):
    data=Events.query.filter_by(id=event_id).first()
    typeinfo=Types.query.filter_by(event_id=event_id).order_by(Types.price).all()
    return render_template('details.html',data=data,typeinfo=typeinfo)


@app.route('/cart', methods=['post','get'])# 오더페이지  
def cart():
     return render_template('cart.html')



if __name__=='__main__':
    app.run(debug=True, port=5001)