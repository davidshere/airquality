import dataclasses
from xml.etree import ElementTree

from flask import (
    Blueprint, jsonify,render_template, request
)
import requests

from app.utils.aqi import get_aqi, Particle
from app.utils.response import get_last_day, TimingResponse, timing_results_to_buckets, average_aqi_from_buckets

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
    results = [ 
        TimingResponse(
            a[0],
            get_aqi(a[1],Particle.TWO_POINT_FIVE),
            get_aqi(a[2], Particle.TEN)
        )
        for a in get_last_day()
    ]

    buckets = timing_results_to_buckets(results)
    average_aqi = average_aqi_from_buckets(buckets)
    return jsonify(average_aqi)

@bp.route('/', methods=('GET',))
def index():
    return render_template('index.html')