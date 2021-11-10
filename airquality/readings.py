import functools
import json
import logging

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
logger = logging.getLogger(__name__)

bp = Blueprint('readings', __name__)

@bp.route('/', methods=('GET'))
def readings():
    pmi = {
        '2.5': 99,
        '10': 99 
    }
    return render_template('index.html', pmi=pmi)


