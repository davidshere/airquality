import functools
from datetime import tzinfo
import json
import logging

from flask import (
    Blueprint, jsonify, flash, g, redirect, render_template, request, session, url_for
)

from airquality.db import get_db


logger = logging.getLogger(__name__)

bp = Blueprint('readings', __name__)

@bp.route('/current', methods=('GET',))
def readings():
    db = get_db()
    pmi25, pmi10 = db.execute(
        "SELECT pmi25, pmi10 from readings where recorded_at = (SELECT max(recorded_at) from readings);"
    ).fetchone()
    pmi = {
        '2.5': pmi25,
        '10': pmi10,
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
    results = [(a[0].astimezone(),a[1],a[2]) for a in db.execute(query).fetchall()]
    return jsonify(results)


