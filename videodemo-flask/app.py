from functools import wraps

from flask import Flask, request, jsonify, abort, url_for, Response
from flask import render_template

import appHelper

from config import config

app = Flask(__name__)
config["development"].init_app(app)

def pasrse(param):
    # todo
    return param

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    # username and password just for test
    return username == 'admin' and password == 'admin'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route('/')
def hello_world():
    return render_template("video-app.html")


@app.route("/login")
def get_login():
    return render_template("index.html")


@app.route("/video")
def get_video():
    return render_template("video-app.html")


@app.route("/get_video", methods=["GET"])
def get_video_info():
    video_uri = request.args.get("name", None)
    if not video_uri:
        abort(404)
    try:
        video_info, m3u8_list = appHelper.get_video_info(video_uri)
        return render_template("search.html", video_info=video_info, m3u8_list=m3u8_list,
                               count=[x + 1 for x in range(len(m3u8_list))])
    except Exception as err:
        app.logger().exception(err)
        abort(500)


@app.route("/search", methods=["POST"])
@requires_auth
def get_search():
    data_post = request.get_json()
    search_video_name = data_post.get("video_name")
    video_infos = appHelper.search_video(search_video_name)
    return jsonify(video_infos)


if __name__ == '__main__':
    app.run()
