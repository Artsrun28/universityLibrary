from flask import Flask, render_template, redirect, request, url_for, session
import glob
import os
from datetime import datetime, timedelta
from peewee import fn

from forms import CreateBookForm, LoginForm, RegisterForm, ChangePasswordForm

from models.books import Book
from models.user import User
from models.library_history import LibraryHistory
from login import login_required

# Flask app
app = Flask(__name__, static_url_path='/media')
app.config.from_object("config.AppConfig")


# Context processor to inject user data
@app.context_processor
def inject_data():
    user_id = session.get("user")
    user = None
    if user_id:
        user = User.get(user_id)
    return {"user": user}


# Handles user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.get(username=form.username.data)
        hashed_password = User.hash_password(form.username.data, form.password.data)
        if not user or user.password != hashed_password:
            form.username.errors.append('Invalid credentials')
            return render_template("login.html", form=form)  # Return the template if credentials are invalid

        session['user'] = user.id
        return_url = request.args.get("next")
        return redirect(return_url if return_url else "/")  # Redirect to home or the previous page

    return render_template(template_name_or_list="login.html", form=form)


# Logout
@app.route('/logout')
def logout():
    session['user'] = None
    return redirect('/login')


# Handles user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.from_registration_form(form)
        user.save()
        return redirect("/our-students")
    return render_template(template_name_or_list="register.html", form=form)


# Changing password
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        current_password = form.current_password.data
        new_password = form.new_password.data

        user = User.get(username=username)
        if user and user.password == User.hash_password(username, current_password):
            User.change_password(user.id, new_password)
            return redirect('/')
        else:
            form.username.errors.append('Invalid credentials')

    return render_template('change_password.html', change_password_form=form)


# Home route
@app.route('/')
def home():
    return render_template(template_name_or_list='home.html')


# About route
@app.route('/about')
def about():
    return render_template(template_name_or_list='about.html')


# Displays available books
@app.route('/books')
def books():
    query = request.args.get('query', '').lower()

    # Filter books based on the search query
    if query:
        books = Book.select().where(
            (fn.lower(Book.book_name).contains(query)) |
            (fn.lower(Book.author_name).contains(query))
        )
    else:
        books = Book.select()
    return render_template(template_name_or_list='books.html', books=books, query=query)


# Dynamic routing for book details
@app.route('/books/<int:book_id>')
def books_details(book_id):
    try:
        book = Book.get(id=book_id)
        return render_template('books_details.html', book=book)
    except Book.DoesNotExist:
        return render_template(template_name_or_list='404.html'), 404


# app.route decorators methods by default are GET, if you need POST, you need to define methode
@app.route('/books/new', methods=['GET', 'POST'])
@login_required  # Requires login
def new_book():
    create_book_form = CreateBookForm()
    if create_book_form.validate_on_submit():
        # Create a new book and save it
        book = Book(
            book_name=create_book_form.book_name.data,
            author_name=create_book_form.author_name.data,
            release_year=create_book_form.release_year.data,
            book_copy=create_book_form.book_copy.data,
        )
        book.save()
        return redirect('/books')  # Redirect to books page after adding a new book
    return render_template(template_name_or_list="new_book.html", form=create_book_form)


# Update book details
@app.route('/book_update', methods=['POST'])
def book_update():
    book_id = request.form.get('book_update_id')
    new_book_name = request.form.get('new_book_name')
    author_name = request.form.get('author_name')
    new_release_year = request.form.get('new_release_year')

    if book_id and new_book_name and author_name and new_release_year:
        try:
            book = Book.get(Book.id == book_id)
            book.book_name = new_book_name
            book.author_name = author_name
            book.release_year = new_release_year
            book.save()
        except User.DoesNotExist:
            render_template(template_name_or_list='404.html'), 404
    return redirect("/books")


# Add this route to your Flask app
@app.route('/add-book-copies/<int:book_id>', methods=['POST'])
@login_required  # Requires login
def add_book_copies(book_id):
    new_book_copies = int(request.form.get('new_book_copies'))
    try:
        book = Book.get(id=book_id)
        book.book_copy += new_book_copies
        book.save()
    except (ValueError, Book.DoesNotExist):
        return render_template('404.html'), 404

    return redirect(url_for('books_details', book_id=book.id))


# Delete book
@app.route('/delete-book', methods=['POST'])
def delete_book():
    book_id = request.form.get('book_id')
    if book_id:
        try:
            book = Book.get(Book.id == book_id)
            book.delete_instance()
        except Book.DoesNotExist:
            render_template(template_name_or_list='404.html'), 404
    return redirect("/books")


# book borrow
@app.route('/take-book/<int:book_id>')
@login_required  # Requires login
def take_book(book_id):
    user = User.get(session['user'])

    try:
        book = Book.get(id=book_id)
        if book.book_copy > 0:
            # Decrease the book copies by 1
            book.book_copy -= 1
            book.save()

            days_to_add = 14

            LibraryHistory.create(
                student_id=user.id,
                student_name=user.full_name,
                book_name=book.book_name,
                author_name=book.author_name,
                date_taken=datetime.today().date(),
                return_date=datetime.today().date() + timedelta(days=days_to_add),
            )

            return redirect('/books')  # Redirect to the books page after taking the book
        else:
            return render_template('book_not_available.html', book=book)   # change
    except Book.DoesNotExist:
        return render_template(template_name_or_list='404.html'), 404


@app.route('/delete-returned-book', methods=['POST'])
@login_required
def delete_returned_book():
    history_id = request.form.get('history_id')
    if history_id:
        try:
            returned_book = LibraryHistory.get(LibraryHistory.id == history_id)
            book = Book.get(Book.book_name == returned_book.book_name)

            # Increment book_copy by one
            book.book_copy += 1
            book.save()

            returned_book.delete_instance()
        except LibraryHistory.DoesNotExist:
            return render_template("404.html"), 404
    return redirect("/library-history")


# Admin's library history page
@app.route('/library-history')
@login_required
def library_history():
    history = LibraryHistory.select().order_by(LibraryHistory.date_taken.desc()).limit(5)
    return render_template('library_history.html', history=history)


# Route to display students
@app.route('/our-students')
def students():
    students = User.select()
    return render_template(template_name_or_list='students.html', students=students)


# Dynamic routing for student details
@app.route('/students/<int:user_id>')
def student_details(user_id):
    try:
        student = User.get(id=user_id)
        return render_template("student_details.html", student=student)
    except User.DoesNotExist:
        return render_template(template_name_or_list="404.html"), 404


@app.route('/user_update', methods=['POST'])
def user_update():
    user_id = request.form.get('user_update_id')
    new_username = request.form.get('new_username')
    new_full_name = request.form.get('new_full_name')
    new_email = request.form.get('new_email')
    # Update user details
    if user_id and new_full_name and new_email and new_username:
        try:
            user = User.get(User.id == user_id)
            user.username = new_username
            user.full_name = new_full_name
            user.email = new_email
            user.save()
        except User.DoesNotExist:
            return render_template(template_name_or_list="404.html"), 404
    return redirect("/our-students")


@app.route('/delete-user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')
    if user_id:
        try:
            user = User.get(User.id == user_id)
            user.delete_instance()
        except User.DoesNotExist:
            return render_template(template_name_or_list="404.html"), 404
    return redirect("/our-students")


@app.route('/photos')
def photos():
    all_files = map(os.path.basename, glob.glob(f"{app.static_folder}/*.jpg"))
    photo_urls = []
    for file in all_files:
        photo_urls.append(url_for("static", filename=file))
    return render_template(template_name_or_list="photos.html", photo_urls=photo_urls)


@app.route('/photos/new', methods=['GET', 'POST'])
@login_required
def add_photo():
    if request.method == "POST":
        photo = request.files["photo"]
        photo.save(f"{app.static_folder}/{photo.filename}")
        return redirect("/photos")
    return render_template(template_name_or_list="photos_new.html")


if __name__ == '__main__':
    app.run(port=5000, debug=True)


'''TODO
1.UX/UI
'''
