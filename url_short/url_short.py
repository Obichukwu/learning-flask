from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session, jsonify
import json
import os.path
from werkzeug.utils import secure_filename

bp = Blueprint('url_short',__name__,template_folder='templates')

@bp.route('/')
def home():
    codes = session.keys()
    return render_template('home.jinja', prev_codes=codes)

@bp.route('/your-url', methods=['GET','POST'])
def your_url():
    if request.method == 'POST':
        urls = {}

        url_filename = 'urls.json'
        if os.path.exists(url_filename):
            with open(url_filename,'r') as urls_file:
                urls = json.load(urls_file)

        if request.form['code'] in urls.keys():
            flash("That short name has already been taken, select a new one")
            return redirect(url_for('url_short.home'))

        if 'url' in request.form.keys():
            urls[request.form['code']] = {'url':request.form['url']}
        else:
            f = request.files['file']
            full_name = request.form['code'] + secure_filename(f.filename)
            f.save('./static/user_files/' + full_name)
            urls[request.form['code']] = {'file':full_name}        

        with open(url_filename,'w') as urls_file:
            session[request.form['code']] = True
            json.dump(urls, urls_file)

        return render_template('your_url.jinja', code=request.form['code'])
    else:
        return redirect(url_for('url_short.home'))

@bp.route('/<string:code>')
def redirect_to_url(code):
    urls = {}
    url_filename = 'urls.json'
    if os.path.exists(url_filename):
        with open(url_filename,'r') as urls_file:
            urls = json.load(urls_file)

    if code in urls.keys():
        shorted_item = urls[code]
        if 'url' in shorted_item.keys():
            return redirect(shorted_item['url'])
        else:
            return redirect(url_for('static',filename='user_files/' + shorted_item['file']))
    
    return abort(404)


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.jinja'), 404

@bp.route('/api')
def session_api():
    return jsonify(list(session.keys()))

