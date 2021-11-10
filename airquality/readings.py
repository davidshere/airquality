import functools
import json
import logging

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from airquality.db import get_db
logger = logging.getLogger(__name__)

bp = Blueprint('readings', __name__)

@bp.route('/', methods=('GET', 'POST'))
def readings():
    if request.method == 'POST':
        if not request.form:
            return "No results found\n", 404
        db = get_db()
        db.execute(
            'INSERT INTO readings(pmi25, pmi10) '
            'VALUES (?, ?);',
            (request.form['pmi25'], request.form['pmi10'])
        )
        db.commit()
        return 'success'
    else:
        #two_point_five, ten = sensor.get_pmi_result()
        pmi = {
            '2.5': 99,
            '10': 99 
        }
        return render_template('index.html', pmi=pmi)


