from flask import  Blueprint,Response, render_template, request, flash, redirect, url_for, abort,send_file
from flask_login import login_required, current_user,login_user, logout_user    # for login_manager
from .extensions import db, login_manager
from .models import Url, User
from .models import Demo
from .utils.views import get_greeting,generate_demo_url
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
import validators
import secrets
import qrcode
import io 


url = Blueprint('url', __name__)
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
limiter = Limiter(key_func=get_remote_address)
# #short url
# @url.route('/<shorten_url>', methods=['GET'])
# def redirect_short_original_url(shorten_url):
#     demo_urls = Demo.query.filter_by(demo_short_url=shorten_url).first()
#     if demo_urls:
#         return redirect(demo_urls.original_url)
#     else:
#         flash('Invalid short URL', 'danger')
#         return redirect(url_for('url.trial_demo'))

# @url.route('/trials', methods=['GET', 'POST'])
# def trial_demo():
    
#     demo_original_url = request.form.get('demo_original_url')
#     demo_short_url = generate_demo_url()

#     # if not validators.url(original_url):
#     #     flash('Invalid URL', 'danger')
#     #     return redirect(url_for('url.demo_trial'))

#     urls = Demo(demo_original_url=demo_original_url, demo_short_url=demo_short_url)
#     urls.save()

#     flash('Shortened URL created successfully', 'success')
#     return render_template('trial_demo.html', new_url=demo_short_url, demo_original_url=demo_original_url)
#URL Home Routes
# @url.route('/')
# def home():
#     return render_template('index.html')
#URL DEMO ROUTES returning just original url and shortened url


#redirect to short to  original url

# @url.route('/<short_url>')
# def redirect_to_original_url(short_url):
#     # Find the corresponding original URL based on the short URL
#     url = Url.query.filter_by(short_url=short_url).first_or_404()
    
#         # Redirect to the original URL
#     # url.visits = url.visits + 1
#     # db.session.commit()
#     return redirect(url.original_url)
    
    # else:
    #     # Handle the case when the short URL is not found
    #     flash('Invalid short URL', 'danger')
    #     return redirect(url_for('url.profile'))

#URL User Authentication and Authorisation (login,logout,signup)Routes
# signup route
@url.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username1 = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        username_exists = User.query.filter_by(username=username1).first()
        if username_exists:
            flash('Username already exists.', 'danger')
            return redirect(url_for('url.signup'))
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            flash('Email address already exists.', 'danger')
            return redirect(url_for('url.signup'))

        user = User(username=username1, email=email, password=generate_password_hash(password, method='sha256'))
        try:
            user.save()
        except:
            db.session.rollback()
            response = {'Message': 'Unexpected error occurred while saving'}
            return response, 500

        flash('Account created successfully!', 'success')
        return redirect(url_for('url.home'))

    return render_template('signup.html')
# login route   
@url.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('url.home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('url.login'))
        login_user(user)
        return redirect(url_for('url.home'))
     # Return a response when the request method is not 'POST'
    return render_template('login.html')
#logout route
@url.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful', 'success')
    return redirect(url_for('url.login'))
#user profile route with update, greeting  and delete options
#Route for user profile
@url.route('/profile')
@login_required
def profile():
    user = User.query.filter_by(id=current_user.id).first_or_404()
    urls = Url.query.filter_by(user=user).all()
    greeting = get_greeting()

    return render_template('profile.html', urls=urls, user=user, greeting=greeting)






# @url.route('/profile/short_url')
# @login_required
# def profile_short_url():
    
#     user=User.query.filter_by(username=current_user.username)
#     if user:
#        new_urls = Url.query.filter_by(user=user).all()
#     greeting=get_greeting()

#     return render_template('short_url.html', new_urls=new_urls, user=user, greeting=greeting)



@url.route('/edit_username', methods=['GET', 'POST'])
@login_required
def edit_account():
    user = User.query.filter_by(email=current_user.email).first()
    if not user:
        # User not found, handle the error accordingly
        return render_template('error.html', error_message="User not found")

    if request.method == 'POST':
        new_username = request.form.get('username')
        user.username = new_username
        db.session.commit()

        return redirect(url_for('url.profile'))

    return render_template('edit_account.html', user=user)
#delete account route 
@url.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        user = User.query.filter_by(email=current_user.email).first()
        if user:
            # Delete the associated URLs
            urls = Url.query.filter_by(user=user).all()
            for url in urls:
                db.session.delete(url)

            # Delete the user account
            db.session.delete(user)
            db.session.commit()

            # Log out the user
            logout_user()

            flash('Your account has been deleted.', 'success')
            return redirect(url_for('url.home_page'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('url.delete_account'))

    # GET request
    return render_template('delete_user_account.html')

#user password update route
@url.route('/password', methods=['POST'])
@login_required
def password_post():
    user = User.query.filter_by(email=current_user).first()
    if user:
        if request.method =='POST':
            check_password_hash(user.password, request.form.get('old_password'))
            flash('Old password is incorrect.', 'danger')
            user.password = generate_password_hash(request.form.get('new_password'), method='sha256')
            db.session.commit()
        flash('Password updated successfully', 'success')
        return redirect(url_for('url.profile'))
    return render_template('password.html',user=user)
   
    return redirect(url_for('url.profile')),200
@url.route('/', methods=['GET'])
def home_page():
    return render_template('home.html')
#URL DEMO ROUTES returning just original url and shortened url

@url.route('/index', methods=['GET'])
@login_required
def home():
    return render_template('index.html')
# #route for non customizable url 
@url.route('/shortened', methods=['POST'])
@limiter.limit("10 per minute")
@login_required
def short_url():
    email = current_user.email
    authenticated_user = User.query.filter_by(email=email).first_or_404()
    if not authenticated_user:
        return {
            'message': 'No record found.'
        }, 404
        
    original_url = request.form['original_url']
    #short_url = request.form.get('short_url')

    if not original_url.startswith('http://') and not original_url.startswith('https://'):
        original_url = 'http://' + original_url

    if not validators.url(original_url):
        flash('Please enter a valid URL', 'danger')
        return redirect(url_for('url.index'))
   
    url = Url(original_url=original_url)
    greeting=get_greeting()
    try:
        url.save()
    except:
        db.session.rollback()
        response = {'Message': 'Unexpected error occurred while saving'}
        return response, 500

    flash('Shortened URL created successfully!', 'success')
    
    return render_template('shortened.html', short_url=url.short_url,user=current_user, greeting=greeting,original_url=url.original_url)

      

@url.route('/<short_url>')
def redirect_to_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first_or_404()
    # Redirect to the original URL
    url.visits = url.visits + 1
    db.session.commit()
    if url:
        return redirect(url.original_url)
    else:
        flash('Invalid short URL', 'danger')
        return redirect(url_for('url.home'))

@url.route('/customise', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
@login_required
def customize_url():
    email = current_user.email
    authenticated_user = User.query.filter_by(email=email).first()
    if not authenticated_user:
        return {
            'message': 'No record found.'
        }, 404

    custom_domain = request.form.get('custom_domain')
    original_url = request.form.get('original_url')

    # Perform any validation or sanitization on the input
    if not validators.url(original_url):
        return "Please enter a valid URL"
    if not validators.domain(custom_domain):
        return "Please enter a valid domain"

    custom_url = Url.query.filter_by(custom_domain=custom_domain).first()
    if custom_url:
        return "This domain is already taken. Please choose another one."

    # Generate a random short URL
    short_url = secrets.token_urlsafe(4)

    custom_url = Url(original_url=original_url, custom_short_url=short_url, custom_domain=custom_domain, user=current_user)
    db.session.add(custom_url)
    db.session.commit()

    full_short_url = f"{request.host_url}/{custom_domain}/{short_url}"  # Replace 'http://' with 'https://' if using HTTPS
    return render_template('customize_url.html', custom_url=custom_url, full_short_url=full_short_url)


# Flask route for redirecting to custom URLs
@url.route('/<custom_domain>/<custom_short_url>', methods=['GET'])
def redirect_to_custom_url(custom_domain, custom_short_url):
    # Find the corresponding original URL based on the custom short URL
    custom_url = Url.query.filter_by(custom_domain=custom_domain, custom_short_url=custom_short_url).first()
    custom_url.visits = custom_url.visits + 1
    db.session.commit()
    if custom_url:
        # Redirect to the original URL
        return redirect(custom_url.original_url)
    if custom_url is None:
        flash('You do not have a Custom  URL', 'danger')
        return redirect(url_for('url.index'))
    else:
        # Handle the case when the custom URL is not found
        flash('Invalid custom URL', 'danger')
        return redirect(url_for('url.customize_url'))

  
@url.route('/stat')
@cache.cached(timeout=30)   # cache the page for 50 seconds
@login_required
def stats():
    short_urls=Url.query.filter_by(user_id=current_user.id).all()
    return render_template('stats.html', urls=short_urls)
@url.route('/stats')
@cache.cached(timeout=30)   # cache the page for 50 seconds
@login_required
def custom_url_stats():
    
    urls=Url.query.filter_by(user_id=current_user.id).all()
    return render_template('custom_urlstats.html', urls=urls)
@url.route('/delete_url/<short_url>')
@login_required
def delete_url(short_url):
    url = Url.query.filter_by(short_url=short_url).first_or_404()
    # if current_user != url.user:
    #     abort(403)
    url.delete()
    flash('Your URL has been deleted', 'success')
    return redirect(url_for('url.home'))

# #QR code Generator
def generate_qr_code(url):
    img = qrcode.make(url)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

# Route for QR code
@url.route('/qr_code/<short_url>')
def generate_qr_code_image(short_url):
    
    url = Url.query.filter_by(short_url=short_url).first_or_404()
    if url:
        img_io = generate_qr_code(request.host_url  + url.short_url)
        return img_io.getvalue(), 200, {'Content-Type': 'image/png'}
    return "No URL found"






 
@url.app_errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


