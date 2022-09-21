from flask import render_template, url_for, redirect, request, jsonify
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from app.models import User, LoginForm, RegisterForm, db, Author, Task
from datetime import datetime
from app import app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# models where here

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    tasks = db.session.query(Task, Author).filter(Task.author_id == Author.author_id).all()
    return render_template("dashboard.html", tasks=tasks)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# logic to CRUD tasks in dashboard after login
@app.route("/submit", methods=["POST"])
def submit():
    global_task_object = Task()

    title = request.form["title"]
    author_name = request.form["author"]
    state = request.form["state"]
    deadline = request.form["deadline"]
    priority = request.form["priority"]
    deadline = datetime.strptime(deadline,'%Y-%m-%d').date()  # select zeros no 00:00:00

    author_exists = db.session.query(Author).filter(Author.name == author_name).first()
    print("author_exists: ", author_exists)  # activate later
    #deadline = db.session.query(Task).filter(Task.deadline == author_name).first()
    # check if author already exists in db
    if author_exists:
        author_id = author_exists.author_id
        print(f'author_id: {author_id}')
        task = Task(author_id=author_id, title=title, state=state, deadline=deadline, priority=priority)
        db.session.add(task)
        db.session.commit()
        global_task_object = task
    else:
        author = Author(name=author_name)
        db.session.add(author)
        db.session.commit()

        task = Task(author_id=author.author_id, title=title, state=state, deadline=deadline, priority=priority)
        db.session.add(task)
        db.session.commit()
        global_task_object = task

    response = f"""
    <tr>
        <td>{title}</td>
        <td>{author_name}</td>
        <td>{state}</td>
        <td>{priority}</td>
        <td>{deadline}<td>
        <td>
            <button class="btn btn-primary"
                hx-get="/get-edit-form/{global_task_object.task_id}">
                Editar Deber
            </button>
        </td>
        <td>
            <button hx-delete="/delete/{global_task_object.task_id}"
                class="btn btn-primary">
                Borrar
            </button>
        </td>
    </tr>
    """
    return response

@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_task(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()

    return ""

@app.route("/get-edit-form/<int:id>", methods=["GET"])
def get_edit_form(id):
    task = Task.query.get(id)
    author = Author.query.get(task.author_id)

    response = f"""
    <tr hx-trigger='cancel' class='editing' hx-get="/get-task-row/{id}">
        <td><input name="title" value="{task.title}"/></td>
        <td>{author.name}</td>
        <td><input name="state" value="{task.state}"/></td>
        <td><input name="priority" value="{task.priority}"/></td>
        <td><input name="deadline" value="{task.deadline.date()}"/></td>
        
        <td>
            <button class="btn btn-primary" hx-get="/get-task-row/{id}">
            Cancel
            </button>
            <button class="btn btn-primary" hx-put="/update/{id}" hx-include="closest tr">
            Save
            </button>
        </td>
    </tr>
    """
    return response

@app.route("/get-task-row/<int:id>", methods=["GET"])
def get_task_row(id):
    task = Task.query.get(id)
    author = Author.query.get(task.author_id)

    response = f"""
    <tr>
        <td>{task.title}</td>
        <td>{author.name}</td>
        <td>{task.state}</td>
        <td>{task.priority}</td>
        <td>{task.deadline.date()}</td>
        <td>
            <button class="btn btn-primary"
                hx-get="/get-edit-form/{id}">
                Editar Deber
            </button>
        </td>
        <td>
            <button hx-delete="/delete/{id}"
                class="btn btn-primary">
                Borrar
            </button>
        </td>
    </tr>
    """
    return response

@app.route("/update/<int:id>", methods=["PUT"])
def update_task(id):
    task_query = db.session.query(Task).filter(Task.task_id == id)
    
    deadline_get = request.form.get("deadline", False)
    #print("deadline_get: ", deadline_get)
    deadline_formatted = datetime.strptime(deadline_get,'%Y-%m-%d')
    #print("deadline_formatted: ", deadline_formatted)
    deadline_date = deadline_formatted.date()
    #print("deadline_date: ", deadline_date)
    data_to_update = dict(title = request.form.get("title", False), 
                          state = request.form.get("state", False),
                          priority = request.form.get("priority", False),
                          deadline = deadline_date)
    print(data_to_update)
    task_query.update(data_to_update)
    db.session.commit()

    title = request.form["title"]
    state = request.form.get("state", False)
    task = Task.query.get(id)
    author = Author.query.get(task.author_id)
    priority = request.form.get("priority", False)
    deadline = request.form.get("deadline", False)

    response = f"""
    <tr>
        <td>{title}</td>
        <td>{author.name}</td>
        <td>{state}</td>
        <td>{priority}</td>
        <td>{deadline}</td>
        <td>
            <button class="btn btn-primary"
                hx-get="/get-edit-form/{id}">
                Editar Deber
            </button>
        </td>
        <td>
            <button hx-delete="/delete/{id}"
                class="btn btn-primary">
                Borrar
            </button>
        </td>
    </tr>
    """
    return response
