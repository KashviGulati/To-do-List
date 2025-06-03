from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from config import Config
from extensions import db, login_manager
from models import User, Task
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'




# ---------------------- Auth Routes ----------------------

@app.route('/')
def index():
    print("=== INDEX ROUTE CALLED ===")
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Current user: {current_user}")
    try:
        result = render_template('index.html')
        print("Index template rendered successfully")
        return result
    except Exception as e:
        print(f"Error rendering index: {e}")
        return f"Error: {e}"

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("=== REGISTER ROUTE CALLED ===")
    print(f"Request method: {request.method}")
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Current user: {current_user}")
    print(f"Current user type: {type(current_user)}")
    
    # TEMPORARILY COMMENT OUT THE REDIRECT CHECK TO DEBUG
    # if current_user.is_authenticated:
    #     print("User already authenticated, redirecting to index")
    #     return redirect(url_for('index'))

    if request.method == 'POST':
        print("Processing POST request for registration")
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password or not confirm_password:
            flash('Please fill out all fields.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    print("Rendering register template")
    try:
        result = render_template('register.html')
        print("Register template rendered successfully")
        return result
    except Exception as e:
        print(f"Error rendering register: {e}")
        return f"Error rendering register template: {e}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("=== LOGIN ROUTE CALLED ===")
    print(f"Request method: {request.method}")
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Current user: {current_user}")
    print(f"Current user type: {type(current_user)}")
    
    # TEMPORARILY COMMENT OUT THE REDIRECT CHECK TO DEBUG
    # if current_user.is_authenticated:
    #     print("User already authenticated, redirecting to index")
    #     return redirect(url_for('index'))

    if request.method == 'POST':
        print("Processing POST request for login")
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')

        if not username_or_email or not password:
            flash('Please enter username/email and password.', 'danger')
            return render_template('login.html')

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
            return render_template('login.html')

    print("Rendering login template")
    try:
        result = render_template('login.html')
        print("Login template rendered successfully")
        return result
    except Exception as e:
        print(f"Error rendering login: {e}")
        return f"Error rendering login template: {e}"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ---------------------- Task Routes ----------------------

@app.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date).all()
    return render_template('dashboard.html', tasks=tasks)

@app.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    if request.is_json:  # Handle AJAX JSON request
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        if not title:
            return jsonify({'success': False, 'message': 'Title is required'}), 400

        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d')
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid due date format'}), 400

        task = Task(
            title=title,
            description=data.get('description', '').strip(),
            status=data.get('status', 'Pending'),
            due_date=due_date,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Task created successfully'})

    # Handle regular form submission
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'Pending')
        due_date_str = request.form.get('due_date', '').strip()

        if not title:
            flash('Title is required.', 'danger')
            return render_template('task_form.html', task=None)

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format. Use YYYY-MM-DD.', 'danger')
                return render_template('task_form.html', task=None)

        task = Task(title=title, description=description, status=status,
                    due_date=due_date, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('task_form.html', task=None)

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'Pending')
        due_date_str = request.form.get('due_date', '').strip()

        if not title:
            flash('Title is required.', 'danger')
            return render_template('task_form.html', task=task)

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format. Use YYYY-MM-DD.', 'danger')
                return render_template('task_form.html', task=task)

        task.title = title
        task.description = description
        task.status = status
        task.due_date = due_date

        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('task_form.html', task=task)

@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    print("=== CREATING DATABASE TABLES ===")
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    
    print("=== STARTING FLASK APP ===")
    print("Available routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule}")
    
    app.run(debug=True)