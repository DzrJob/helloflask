from flask import render_template
from . import main


@main.app_errorhandler(404)
def page_net_found(e):
    return render_template('404.html'), 404


def internal_server_error(e):
    return render_template('500.html'), 500
