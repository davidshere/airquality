import functools
import json
import logging

from flask import (
    Blueprint, jsonify, flash, g, redirect, render_template, request, session, url_for
)

from airquality.db import get_db

logger = logging.getLogger(__name__)

bp = Blueprint('readings', __name__)

@bp.route('/', methods=('GET',))
def readings():
    db = get_db()
    pmi25, pmi10 = db.execute(
        "SELECT pmi25, pmi10 from readings where recorded_at = (SELECT max(recorded_at) from readings);"
    ).fetchone()
    pmi = {
        '2.5': pmi25,
        '10': pmi10,
    }
    return render_template('index.html', pmi=pmi)

@bp.route('/readings', methods=('GET',))
def timing():
    db = get_db()
    query = """
        SELECT recorded_at, pmi25, pmi10
        from readings 
        where recorded_at > (SELECT datetime(max(recorded_at), '-1 days') from readings)
        order by recorded_at asc;
    """
    results = db.execute(query).fetchall()
    return jsonify([(a[0],a[1],a[2]) for a in results])


