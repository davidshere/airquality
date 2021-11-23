import dataclasses
import functools
import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List

from flask import (
    Blueprint, jsonify, flash, g, redirect, render_template, request, session, url_for
)

from airquality.db import get_db
from airquality.utils import get_aqi, Particle

TIME_INTERVAL_MINUTES = 20

logger = logging.getLogger(__name__)

bp = Blueprint('readings', __name__)

@bp.route('/current', methods=('GET',))
def readings():
    db = get_db()
    pmi25, pmi10 = db.execute(
        "SELECT pmi25, pmi10 from readings where recorded_at = (SELECT max(recorded_at) from readings);"
    ).fetchone()
    pmi = {
        '2.5': get_aqi(pmi25, Particle.TWO_POINT_FIVE),
        '10': get_aqi(pmi10, Particle.TEN),
    }
    return jsonify(pmi) 

def get_last_day():
    db = get_db()
    query = """
        SELECT recorded_at, pmi25, pmi10
        from readings 
        where recorded_at > (SELECT datetime(max(recorded_at), '-1 days') from readings)
        order by recorded_at asc;
    """
    return db.execute(query).fetchall()

@dataclasses.dataclass
class TimingResponse:
    recorded_at: datetime
    aqi_two_point_five: int
    aqi_ten: int

def timing_results_to_buckets(results):
    bucket_marker = results[0].recorded_at 
    buckets = defaultdict(list)
    for result in results:
        if result.recorded_at > bucket_marker + timedelta(
            minutes=TIME_INTERVAL_MINUTES
        ):
            bucket_marker = result.recorded_at
        buckets[bucket_marker].append(result)
    return buckets

def average_aqi_from_buckets(buckets):
    response = []
    for marker, bucket in buckets.items():
        two_point_five = [a.aqi_two_point_five for a in bucket]
        ten = [a.aqi_ten for a in bucket]
        response.append([
            marker.isoformat(),
            sum(two_point_five)/len(two_point_five),
            sum(ten)/len(ten)
        ])
    return response

@bp.route('/series', methods=('GET',))
def timing():
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
