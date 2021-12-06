from xml.etree import ElementTree

from flask import (
    Blueprint, jsonify, render_template
)
import requests

from app.response import get_last_day_bucketed_aqi

bp = Blueprint('readings', __name__)

@bp.route('/outside', methods=('GET',))
def outside():
    url = 'http://feeds.airnowapi.org/rss/realtime/98.xml'
    print(url)
    response = requests.get(url)
    tree = ElementTree.fromstring(response.content)
    print(tree)
    breakpoint()
    return ''
 

@bp.route('/series', methods=('GET',))
def series():
    average_aqi = get_last_day_bucketed_aqi()
    return jsonify(average_aqi)

@bp.route('/', methods=('GET',))
def index():
    return render_template('index.html')