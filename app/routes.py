from datetime import datetime, timezone
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request, send_from_directory, current_app
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    EmptyForm, LostFoundItemForm, ResetPasswordRequestForm, ResetPasswordForm, SearchForm 
from app.models import User, LostFoundItem 
from app.email import send_password_reset_email, send_item_confirmation_email 
from werkzeug.utils import secure_filename
import os
import uuid 


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = LostFoundItemForm() 
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            if allowed_file(form.image.data.filename):
                filename = secure_filename(form.image.data.filename)
                unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                form.image.data.save(file_path)
                image_filename = unique_filename
            else:
                flash('Invalid image file type. Allowed types: png, jpg, jpeg, gif', 'danger')
                return redirect(url_for('index'))

        item = LostFoundItem(
            item_type=form.item_type.data,
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            contact_info=form.contact_info.data,
            image_filename=image_filename,
            author=current_user
        )
        db.session.add(item)
        db.session.commit()
        flash(f'Your {item.item_type} item "{item.title}" has been posted!', 'success')
        send_item_confirmation_email(current_user, item) 
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    query = sa.select(LostFoundItem).order_by(LostFoundItem.timestamp.desc())
    items = db.paginate(query, page=page,
                             per_page=app.config['POSTS_PER_PAGE'], error_out=False) 
    next_url = url_for('index', page=items.next_num) \
        if items.has_next else None
    prev_url = url_for('index', page=items.prev_num) \
        if items.has_prev else None

    return render_template('index.html', title='Post Lost/Found Item', form=form,
                           items=items.items, next_url=next_url, prev_url=prev_url)


@app.route('/browse', methods=['GET', 'POST']) 
@login_required
def browse():
    search_form = SearchForm()
    query_param = request.args.get('query', '') 

    if search_form.validate_on_submit():
        query_param = search_form.search_query.data
        return redirect(url_for('browse', query=query_param))

    page = request.args.get('page', 1, type=int)
    base_query = sa.select(LostFoundItem).order_by(LostFoundItem.timestamp.desc())

    if query_param:
        search_filter = LostFoundItem.title.ilike(f'%{query_param}%') | \
                        LostFoundItem.description.ilike(f'%{query_param}%') | \
                        LostFoundItem.location.ilike(f'%{query_param}%')
        base_query = base_query.where(search_filter)

    items = db.paginate(base_query, page=page,
                             per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('browse', page=items.next_num, query=query_param) \
        if items.has_next else None
    prev_url = url_for('browse', page=items.prev_num, query=query_param) \
        if items.has_prev else None

    return render_template('browse.html', title='Browse Lost & Found', items=items.items,
                           next_url=next_url, prev_url=prev_url, search_form=search_form,
                           current_search_query=query_param) 


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger') 
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        flash(f'Welcome back, {user.username}!', 'success') 
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info') 
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user! Please log in.', 'success') 
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid or expired password reset token.', 'danger')
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = user.get_user_items()
    items = db.paginate(query, page=page,
                             per_page=app.config['POSTS_PER_PAGE'],
                             error_out=False)
    next_url = url_for('user', username=user.username, page=items.next_num) \
        if items.has_next else None
    prev_url = url_for('user', username=user.username, page=items.prev_num) \
        if items.has_prev else None
    return render_template('user.html', user=user, items=items.items, 
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = db.session.get(LostFoundItem, item_id)
    if item is None:
        flash('Item not found.', 'danger')
        return redirect(url_for('index'))
    if item.author != current_user:
        flash('You do not have permission to edit this item.', 'danger')
        return redirect(url_for('index'))

    form = LostFoundItemForm(obj=item) 

    if form.validate_on_submit():
        image_filename = item.image_filename 
        if form.image.data and allowed_file(form.image.data.filename):
            if item.image_filename:
                old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.image_filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            filename = secure_filename(form.image.data.filename)
            unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            form.image.data.save(file_path)
            image_filename = unique_filename
        elif form.image.data is None: 
            if item.image_filename:
                old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.image_filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            image_filename = None


        item.item_type = form.item_type.data
        item.title = form.title.data
        item.description = form.description.data
        item.location = form.location.data
        item.contact_info = form.contact_info.data
        item.image_filename = image_filename 
        db.session.commit()
        flash('Your item has been updated!', 'success')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        pass 

    return render_template('edit_item.html', title='Edit Lost/Found Item', form=form, item=item)


@app.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = db.session.get(LostFoundItem, item_id)
    if item is None:
        flash('Item not found.', 'danger')
        return redirect(url_for('index'))
    if item.author != current_user:
        flash('You do not have permission to delete this item.', 'danger')
        return redirect(url_for('index'))

    if item.image_filename:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(item)
    db.session.commit()
    flash('Your item has been deleted.', 'info')
    return redirect(url_for('user', username=current_user.username))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

