from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json
import os
import math
from werkzeug.utils import secure_filename
local_server=True
with open('config.json','r') as c:
    params=json.load(c) [ "params"]
app=Flask(__name__)
app.secret_key="super-secret-key"
app.config['UPLOAD_FOLDER']=params['upload_location']
# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     mail_port='465',
#     mail_use_ssl="True",
#     mail_username=params["gmail_user"],
#     mail_password=params["gmail_password"]
# )
mail=Mail(app)
if(local_server):

    app.config["SQLALCHEMY_DATABASE_URI"] = params[ "local_uri"]
else:
     app.config["SQLALCHEMY_DATABASE_URI"] = params[ "prod_uri"]
db = SQLAlchemy(app)
class Contacts(db.Model):
    # sl_no,name,email,phone_no,message,date

    sl_no= db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String,  nullable=False)
    email = db.Column(db.String(20))
    phone_no=db.Column(db.String(12), nullable=False)
    message=db.Column(db.String(120),  nullable=False)
    date= db.Column(db.String(12), nullable=True)
   

class Posts(db.Model):
    # sl_no,name,email,phone_no,message,date

    slno= db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String,  nullable=False)
    # slug = db.Column(db.String(20))
    slug=db.Column(db.String(12), nullable=False)
    content=db.Column(db.String(120),  nullable=False)
    tagline=db.Column(db.String(120),  nullable=False)
    date= db.Column(db.String(12), nullable=True)
    img_file=db.Column(db.String(12), nullable=True)
@app.route("/")
def home():
    # pagination logic
    # #first page
    # then prev=_#
    # and next=page+1
    # mid page
     # then prev=page-1
    # and next=page+1
    # last page
        # then prev=page-1
    # and next=#
    posts=Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_of_posts']))
    page=request.args.get('page')
    if(not str(page).isdigit()):
        page=1
    page=int(page)
    posts=posts[(page-1)*params['no_of_posts']:page*params['no_of_posts']]
    if(page==1):
        prev="#"
        next="/?page="+str(page+1)
    elif(page==last):
        prev="/?page="+str(page-1)
        next="#"
    else:
        prev="/?page="+str(page-1)
        next="/?page="+str(page+1)
    



    
    return render_template("index.html",params=params,posts=posts,prev=prev,next=next)
@app.route("/about")
def about():
    return render_template("about.html",params=params)
@app.route("/post")
def post():
   
    return render_template("post.html",params=params)
@app.route("/dashboard",methods=["POST","GET"])
def dashboard():
    
    if('user' in session and session['user']==params["admin_user"]):
        posts=Posts.query.all()
        return render_template("dashboard.html",params=params,posts=posts)
    if(request.method=="POST"):
        username=request.form.get("uname")
        userpass=request.form.get("pass")
        if(username==params['admin_user'] and userpass==params["admin_password"]):
                # set the session variable
            posts=Posts.query.all()
            session['user']=username
            return render_template("dashboard.html",params=params,posts=posts)
    return render_template("login.html",params=params)


@app.route("/uploader",methods=["POST","GET"])
def uploader():
    if('user' in session and session['user']==params["admin_user"]):
        if(request.method=="POST"):

            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "Uploaded Successfully"
    return render_template("login.html",params=params)
@app.route("/edit/<string:sno>",methods=['POST','GET'])
def edit(sno):
    if('user' in session and session['user']==params["admin_user"]):
        if(request.method=="POST"):
            box_title=request.form.get('title')
            tline=request.form.get('tline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img_file=request.form.get('img_file')
            date=datetime.now()
            # >0-edit
            # 0 -add post
            if(sno=='0'):
                post=Posts(title=box_title,slug=slug,content=content,tagline=tline,img_file=img_file,date=date)
                # print(post)
                db.session.add(post)
                db.session.commit()
            else:
                post =Posts.query.filter_by(slno=sno).first()
                post.title=box_title
                post.slug=slug
                post.content=content
                post.tagline=tline
                post.img_file=img_file
                post.date=date
                db.session.commit()
                return redirect('/edit')
        post=Posts.query.filter_by(slno=sno).first()
        
        return render_template('edit.html',params=params,post=post,sno=sno)
    return render_template('login.html',params=params)
    

@app.route("/logout",methods=['POST','GET'])
def logout():
    if('user' in session and session['user']==params["admin_user"]):

        session.pop('user')
    return redirect('/dashboard')
    
@app.route("/delete/<string:sno>",methods=['POST','GET'])
def delete(sno):
    if('user' in session and session['user']==params["admin_user"]):
        post=Posts.query.filter_by(slno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

@app.route("/contact",methods=['POST','GET'])
def contact():
    if(request.method=='POST'):

        """add entry to the database"""
        name=request.form.get("name")
        email=request.form.get("email")
        phone=request.form.get("phone")
        message=request.form.get("message")
          # sl_no,name,email,phone_no,message,date
        entry=Contacts(name=name,email=email,phone_no=phone,message=message,date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        # mail.send_message('new message from '+name,
        #                   sender=email,
        #                   recipients=[params["gmail_user" ]],
        #                   body=message+"\n"+phone)
        


    return render_template("contact.html",params=params)
@app.route("/post/<string:post_slug>",methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",params=params,post=post)


app.run(debug=True)