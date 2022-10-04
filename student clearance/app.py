from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user,LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///clearance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']= 'secretkey'
db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)


class Requirement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    library = db.Column(db.String(10), nullable=False)
    bursary = db.Column(db.String(10), nullable=False)
    directorate = db.Column(db.String(10), nullable=False)
    academic = db.Column(db.String(10), nullable=False)
    support = db.Column(db.String(10), nullable=False)
    department = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('clearance.id'))

class Clearance(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),  nullable=False)
    matric = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(50),  nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    course = db.Column(db.String(20))
    phone = db.Column(db.String(20), nullable=False)
    status = db.relationship('Requirement', backref='user')
    
admin = Admin(app)
admin.add_view(ModelView(Requirement, db.session))
admin.add_view(ModelView(Clearance, db.session))


@login_manager.user_loader
def load_user(id):
    return Clearance.query.get(int(id))
    
@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == "POST":
        _name = request.form['name']
        _matric = request.form['matric']
        _password = request.form['password']
        _email = request.form['email']
        _course = request.form['course']
        _phone = request.form['phone']
        
        user = Clearance.query.filter_by(email=_email).first()
        if user: 
            flash('Email already exist', category='error')
        elif len(_email) < 4:
            flash("Email must be greater than 4 characters", category='error')
            
        elif len(_name) < 5:
            flash("Enter your full name", category='error')
            
        elif len(_phone) > 11 or len(_phone) < 11:
             flash("Wrong phone number", category='error')
            
        elif len(_password) < 6:
             flash("Password must be at least 7 characters",category='error')
             
        else:
            hash_password = generate_password_hash(_password, method='sha256')
            flash('Account created successfully', category='success')
            register = Clearance(name=_name,matric=_matric,phone=_phone, password=hash_password, email=_email, course=_course)
            db.session.add(register)
            db.session.commit()
            return redirect('/login')
        
        return render_template('register.html')
    else:
        details = Clearance.query.all()
        return render_template('register.html', user=details)

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        
        user = Clearance.query.filter_by(email=email).first()
       
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect('/mydashboard') 

            else:
                flash("Invalid login details", category='error')
        else:
            flash("Email doesn\'t exist", category='error')
    return render_template('index.html')

@app.route('/status', methods=['POST','GET'])
@login_required
def upload():
    if request.method == 'POST':
        library = request.form['library']
        bursary = request.form['bursary']
        directorate = request.form['directorate']
        academic = request.form['academic']
        support =  request.form['support']
        department = request.form['department']
        
        user = current_user.id
        r = Requirement(library=library, bursary=bursary, directorate=directorate, academic=academic,support =support, department=department, user_id=user)
        db.session.add(r)
        db.session.commit()
        return redirect('/mydashboard')
    else:
        return render_template('upload.html', user=current_user)

@app.route('/mydashboard', methods=['POST','GET'])
@login_required
def dashboard():
    user = current_user.status
    for i in user:
        if i.library != "cleared":
            point = "pending"
        elif i.bursary != "cleared":
            point = "pending"
        elif i.directorate != "cleared":
            point = "pending"
        elif i.academic != "cleared":
            point = "pending"
        elif i.support != "cleared":
            point = "pending"
        elif i.department != "cleared":
            point = "pending"
        else:
            point = "fully cleared"
    return render_template('dashboard.html',user=current_user,name=current_user.name.split(" ")[1])

@app.route('/logout', methods=['POST','GET'])
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/profile', methods=['POST','GET'])
@login_required
def profile():
    return render_template('profile.html', user=current_user)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)