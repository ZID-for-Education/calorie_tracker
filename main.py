import sys
from flask import Flask, request, redirect, render_template, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import datetime
import json

from sqlalchemy import and_, or_


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' 
db=SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'User'
    id =db.Column(db.Integer, primary_key=True, unique = True, nullable = False)
    username = db.Column(db.String(200),unique=True,nullable=False)
    passward = db.Column(db.String(200),nullable=False)
    age = db.Column(db.Integer,nullable=False)
    height = db.Column(db.Integer,nullable=False)
    weight = db.Column(db.Integer,nullable=False)
    goal_weight = db.Column(db.Integer,nullable=False)
    gender = db.Column(db.String(200),nullable=False)
    daily_caloire_goal = db.Column(db.Integer,nullable=False)
    date_of_creation = db.Column(db.String(200), default = datetime.utcnow().strftime('%Y-%m-%d'), nullable = False)

    def __init__(self,username,passward,age,height,weight,goal_weight,gender,daily_caloire_goal):
        self.username=username
        self.passward=passward
        self.age=age
        self.height=height
        self.weight=weight
        self.goal_weight=goal_weight
        self.gender=gender
        self.daily_caloire_goal=daily_caloire_goal

    def __repr__(self): #for debugging
        return '<Name %r>' % self.username
    
class diary(db.Model): 
    __tablename__ = 'Diary'
    id =db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200),nullable=False)
    calorie = db.Column(db.String(200),nullable=False)
    date = db.Column(db.String(200),nullable=False)

    def serialize(self):
       return {
           'id' : self.id,
           'username' : self.user,
           'calorie'  : self.calorie,
           'date': self.date
       }
    
    def __repr__(self):
        return '<Name %r>' % self.user

class Food(db.Model):
    __tablename__ = 'Food'
    id = db.Column(db.Integer, primary_key = True, unique = True, nullable = False)
    name = db.Column(db.String(200), nullable = False)
    calories = db.Column(db.Integer, nullable = False)
    userID = db.Column(db.Integer, db.ForeignKey('User.id'), nullable = False)

    def __repr__(self):
        return '<Name %r>' % self.name

class Exercise(db.Model):
    __tablename__ = 'Exercise'
    id = db.Column(db.Integer, primary_key = True, unique = True, nullable = False)
    name = db.Column(db.String(200), nullable = False)
    calories = db.Column(db.Integer, nullable = False)
    userID = db.Column(db.Integer, db.ForeignKey('User.id'), nullable = False)

    def __repr__(self):
        return '<Name %r>' % self.name

def date_string_to_float(date_string):
    date = datetime.strptime(date_string, '%Y-%m-%d')
    return date.timestamp()
class FoodDiary:
    def __init__(self, diary_list):
        self.diary_list = diary_list
    
    def average(self):
        total = 0
        for diary in self.diary_list:
            total += diary[0]
        return total / len(self.diary_list)
    
    def average_over_time(self, timeBegin, timeEnd):
        total = 0
        count = 0
        for diary in self.diary_list:
            if diary[1] >= timeBegin and diary[1] <= timeEnd:
                total += diary[0]
                count += 1
        return total / count
    
    def total(self):
        total = 0
        for diary in self.diary_list:
            total += diary[0]
        return total
    
    def total_over_time(self, timeBegin, timeEnd):
        total = 0
        for diary in self.diary_list:
            if diary[1] >= timeBegin and diary[1] <= timeEnd:
                total += diary[0]
        return total
    
    def max(self):
        max = 0
        for diary in self.diary_list:
            if diary[0] > max:
                max = diary[0]
        return max
    
    def max_over_time(self, timeBegin, timeEnd):
        max = 0
        for diary in self.diary_list:
            if diary[1] >= timeBegin and diary[1] <= timeEnd:
                if diary[0] > max:
                    max = diary[0]
        return max
    
    def min(self):
        min = sys.maxint
        for diary in self.diary_list:
            if diary[0] < min:
                min = diary[0]
        return min
    
    def min_over_time(self, timeBegin, timeEnd):
        min = sys.maxint
        for diary in self.diary_list:
            if diary[1] >= timeBegin and diary[1] <= timeEnd:
                if diary[0] < min:
                    min = diary[0]
        return min
    
    def count(self):
        return len(self.diary_list)
    
    def count_over_time(self, timeBegin, timeEnd):
        count = 0
        for diary in self.diary_list:
            if diary[1] >= timeBegin and diary[1] <= timeEnd:
                count += 1
        return count
    
    def get_diary_list(self):
        return self.diary_list
    
    def get_diary_list_over_time(self, timeBegin, timeEnd):
        diary_list = []
        for diary in self.diary_list:
            if diary[1] >= timeBegin and diary[1] <= timeEnd:
                diary_list.append(diary)
        return diary_list
    
    def get_diary_data_over_time(self, timeBegin, timeEnd):
        max = self.max_over_time(timeBegin, timeEnd)
        min = self.min_over_time(timeBegin, timeEnd)
        average = self.average_over_time(timeBegin, timeEnd)
        total = self.total_over_time(timeBegin, timeEnd)
        count = self.count_over_time(timeBegin, timeEnd)
        return [max, min, average, total, count]
    
    def get_diary_data(self):
        max = self.max()
        min = self.min()
        average = self.average()
        total = self.total()
        count = self.count()
        return [max, min, average, total, count]
    
    
with app.app_context():
    db.create_all()
  
@app.route("/") 
def default(): 
    return redirect(url_for("login_controller"))
    
@app.route("/login/", methods=["GET", "POST"]) 
def login_controller(): 
    if(request.method=="GET"):
        return render_template("loginPage.html")
    else:
        user = User.query.filter_by(username=request.form['user_name']).first()

        if user and user.passward == request.form['user_password']:
            return redirect(url_for('profile',username=request.form['user_name']))
        else:
            return render_template("loginPage.html")

@app.route("/register/", methods=["GET", "POST"]) 
def register_controller(): 
    if(request.method=="GET"):
        return render_template("registerPage.html")
    else:
        user1 = User.query.filter_by(username=request.form['user']).first()

        if user1:
            return render_template("registerPage.html")
        elif request.form['Password']==request.form['RePassword']:
            Useranme =request.form['user']
            age=request.form['age']
            gender=request.form['gender']
            height=request.form['height']
            weight=request.form['weight']
            goal_weight=request.form['goal_weight']
            daily_caloire_goal=request.form['daily_caloire_goal']
            Passward =request.form['Password']
            newUser= User(username=Useranme,
                          age=age,height=height,
                          weight=weight,
                          goal_weight=goal_weight,
                          gender=gender,
                          daily_caloire_goal=daily_caloire_goal,
                          passward=Passward)
            try:
               db.session.add(newUser)
               db.session.commit()
               return redirect(url_for('profile', username=Useranme))
            except:
               return 'There was an issue adding your task'
        else:
            return render_template("registerPage.html")
            
@app.route("/<username>/profile") 
def profile(username=None): 
    if request.method == "POST":
        return redirect(url_for('diary', username=username))
    else:
        return render_template("caloriePage.html", username=username)
 
@app.route('/<username>/getdiarydata')
def get_diary_data(username=None, methods=["GET"]):
    user = User.query.filter_by(username=username).first() #get user from the database
    diary_list = db.session.execute(db.select([diary.date]).where(diary.user == username)).scalars().all() #get all the dates when the user has made an entry, username are unique
    diary_list = [datetime.strptime(date_str, '%Y-%m-%d') for date_str in diary_list]
    diary_list = list(set(diary_list))
    diary_list.sort()
    diary_list = [datetime.strftime(date_obj, '%Y-%m-%d') for date_obj in diary_list]
    calorie_list = [] #list of tuples (calories, date)
    for i in range(len(diary_list)): #for each date
        calorie_entry = db.session.execute(db.select([diary.calorie]).where(diary.date == diary_list[i], diary.user == user.username)).scalars().all() #get all the calories for that date
        calorie_sum = 0 #sum of calories for that date
        for j in range(len(calorie_entry)): #for each calorie entry
            calorie_sum += float(calorie_entry[j]) #add it to the sum
        calorie_sum=round(calorie_sum,2) 
        newdate = datetime.strptime(diary_list[i], "%Y-%m-%d").strftime("%m-%d-%Y")
        calorie_list.append((newdate, calorie_sum)) #add the sum and the date to the list
    
    return json.dumps(calorie_list)

@app.route("/logout/") 
def unlogger(): 
     return render_template("logoutPage.html")

@app.route("/<username>/add_record/", methods=["GET", "POST"])
def add_record(username=None):
    user = User.query.filter_by(username=username).first() # get user
    food_list = db.session.execute(db.select([Food.name]).where(or_(Food.userID == user.id, Food.userID == 0))).scalars().all() # get food list
    calorie_list = db.session.execute(db.select([Food.calories]).where(or_(Food.userID == user.id, Food.userID == 0))).scalars().all() # get calorie list
    for i in range(len(food_list)):
        food_list[i] = food_list[i] + " (" + str(calorie_list[i]) + " calories)" # combine food and calorie
    if request.method == "GET":
        return render_template("add_record.html", username=username, food_list=food_list)
    else:
        flag = 0 # flag to check if food is in the list
        date = request.form['date']
        food_l_ent = request.form['food_list'] # food list entry
        food = request.form['food'] # food entry
        calorie0 = request.form['calories']
        amount = request.form['amount']

        if food_l_ent != "0": # if dropdown is selected
            flag = 1 # set flag to 1
            food = " ".join(food_l_ent.split(" ")[:-1]) # get food name
            calorie0 = db.session.execute(db.select([Food.calories]).where(Food.name == food)).scalars().first() # get calorie

        calorie1 = str(float(calorie0) * float(amount) / 100) # calculate calorie

        if flag == 0:
            diary_entry = diary(user=username, calorie=calorie1, date=date)
            food_entry = Food(name=food, calories=calorie0, userID=user.id) # add food to the database
        else:
            diary_entry = diary(user=username, calorie=calorie1, date=date)
        try:
            if flag == 0:
                db.session.add(food_entry)
            db.session.add(diary_entry)
            db.session.commit()
            return redirect(url_for('profile', username=username))
        except:
            return 'There was an issue adding your task'
    
@app.route("/<username>/sub_record/", methods=["GET", "POST"])
def sub_record(username=None):
    user = User.query.filter_by(username=username).first() #get user from the database
    exercise_list = db.session.execute(db.select([Exercise.name]).where(or_(Exercise.userID == user.id, Exercise.userID == 0))).scalars().all() #look for exercises by the user and by default
    calorie_list = db.session.execute(db.select([Exercise.calories]).where(or_(Exercise.userID == user.id, Exercise.userID == 0))).scalars().all() #look for calories associated with these exercises
    for i in range(len(exercise_list)):
        exercise_list[i] = exercise_list[i] + " (" + str(calorie_list[i]) + " calories)" #join them
    if request.method == "GET":
        return render_template("sub_record.html", username=username, exercise_list = exercise_list)
    else:
        flag = 0 #flag to check if the dropdown menu was used
        date = request.form['date']
        exercise_l_ent = request.form['exercise_list']
        exercise = request.form['exercise']
        calorie0 = request.form['calories']
        amount = request.form['amount']

        if exercise_l_ent != "0": #if the dropdown menu was used
            flag = 1
            exercise = " ".join(exercise_l_ent.split(" ")[:-1]) #get the exercise name
            calorie0 = db.session.execute(db.select([Exercise.calories]).where(Exercise.name == exercise)).scalars().first()

        calorie1 = str(-(float(calorie0) * float(amount)))
        print(calorie1)
        if flag == 0: #if the dropdown menu was not used
            diary_entry = diary(user=username, calorie=calorie1, date=date)
            exercise_entry = Exercise(name=exercise, calories=calorie0, userID=user.id) #add the exercise to the database
        else: #if the dropdown menu was used
            diary_entry = diary(user=username, calorie=calorie1, date=date)
        try:
            if flag == 0:
                db.session.add(exercise_entry)
            db.session.add(diary_entry)
            db.session.commit()
            return redirect(url_for('profile', username=username))
        except:
            return 'There was an issue adding your task'
        
@app.route("/<username>/diary/", methods=["GET"])
def diary_entry(username=None):
    user = User.query.filter_by(username=username).first() #get user from the database
    diary_list = db.session.execute(db.select([diary.date]).where(diary.user == username)).scalars().all() #get all the dates when the user has made an entry, username are unique
    diary_list = [datetime.strptime(date_str, '%Y-%m-%d') for date_str in diary_list]
    diary_list = list(set(diary_list))
    diary_list.sort(reverse=True)
    diary_list = [datetime.strftime(date_obj, '%Y-%m-%d') for date_obj in diary_list]
    calorie_list = [] #list of tuples (calories, date)
    for i in range(len(diary_list)): #for each date
        calorie_entry = db.session.execute(db.select([diary.calorie]).where(diary.date == diary_list[i], diary.user == user.username)).scalars().all() #get all the calories for that date
        calorie_sum = 0 #sum of calories for that date
        for j in range(len(calorie_entry)): #for each calorie entry
            calorie_sum += float(calorie_entry[j]) #add it to the sum
        calorie_sum=round(calorie_sum,2)
        calorie_list.append((calorie_sum, diary_list[i])) #add the sum and the date to the list
    
    return render_template("diary.html", username=username, records=calorie_list)
        
        
if __name__=="__main__":
  app.run(threaded=True)
