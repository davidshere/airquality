import functools
import logging

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from airquality.db import get_db
from airquality import node
logger = logging.getLogger(__name__)

bp = Blueprint('readings', __name__)

@bp.route('/', methods=('GET', 'POST'))
def readings():
    if request.method == 'POST':
        if 'pmi25' not in request.form and 'pmi10' not in request.form:
            logger.error(f"Failed post, args: {request.form}")
            return 'Missing required elements pmi25 or pmi10', 400
        db = get_db()
        db.execute(
            'INSERT INTO readings(pmi25, pmi10) '
            'VALUES (?, ?);',
            (request.form['pmi25'], request.form['pmi10'])
        )
        db.commit()
        return 'success'
    else:
        two_point_five, ten = sensor.get_pmi_result()
        pmi = {
            '2.5': two_point_five,
            '10': ten,
        }
        return render_template('index.html', pmi=pmi)


