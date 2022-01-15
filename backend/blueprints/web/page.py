from flask import Blueprint, render_template
import os

root_path = os.path.abspath('..')
bp = Blueprint('page', __name__,
               template_folder=root_path + '/frontends/dist',
               # set js/css static filepath
               static_folder=root_path+'/frontends/dist',
               # set the right url to access js
               static_url_path='')


@bp.route('/<code>', methods=['GET'])
def activity_page(code):
    # id = Url.query.filter_by(hash_code=code).first().activity_id
    return render_template('index.html')
