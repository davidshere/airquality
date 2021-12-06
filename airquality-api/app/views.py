from xml.etree import ElementTree

from flask import (
    Blueprint, jsonify, render_template, request
)
import requests

from app.response import get_last_day_bucketed_aqi
from app.reading import write_reading

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


@bp.route('/data', methods=('GET', 'POST'))
def data():
    if request.method == "GET":
        average_aqi = get_last_day_bucketed_aqi()
        return jsonify(average_aqi)
    else:
        results = request.json
        write_reading(
            device=results['device_id'],
            pmi25=results['pmi2.5'],
            pmi10=results['pmi10']
        )
        return f"wrote {results}", 200

@bp.route('/', methods=('GET',))
def index():
    return render_template('index.html')