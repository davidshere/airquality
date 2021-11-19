import functools
from datetime import datetime
import json
import logging
from typing import List

from flask import (
    Blueprint, jsonify, flash, g, redirect, render_template, request, session, url_for
)

from airquality.db import get_db
from airquality.utils import get_aqi, Particle


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

@bp.route('/series', methods=('GET',))
def timing():
    db = get_db()
    query = """
        SELECT recorded_at, pmi25, pmi10
        from readings 
        where recorded_at > (SELECT datetime(max(recorded_at), '-1 days') from readings)
        order by recorded_at asc;
    """
    results: List[datetime, float, float]
    results = [
        (a[0].isoformat(),get_aqi(a[1], Particle.TWO_POINT_FIVE) ,get_aqi(a[2], Particle.TEN))
        for a in db.execute(query).fetchall()
    ]
    return jsonify(results)


