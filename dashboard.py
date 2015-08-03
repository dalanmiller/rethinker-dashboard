from __future__ import print_function, unicode_literals
from flask import Flask, make_response
import rethinkdb as r
import json
app = Flask(__name__, static_url_path="/static")

@app.route("/")
@app.route("/users")
def root():
    return app.send_static_file('index.html')

@app.route("/api/users")
def users():

    conn = r.connect(host='localhost', port=28015, db="users_dashboard")

    users = r.table("users")\
        .has_fields("geo_point")\
        .merge(lambda d: {'coords': d['geo_point'].to_geojson()['coordinates']})\
        .pluck("coords", "id", "login", "location")\
        .coerce_to("array")\
        .run(conn)

    json_string = json.dumps(dict(
        users = users
    ))

    response = make_response(json_string)
    response.headers['Content-Type'] = "application/json"
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'X-AUTH-TOKEN, X-API-VERSION, X-Requested-With, Content-Type, Accept, Origin'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Max-Age'] = "1728000"
    return response

@app.route('/api/users/<user_id>')
def user(user_id):
    conn = r.connect(host='localhost', port=28015, db="users_dashboard")

    user = r.table("users")\
        .get(user_id)\
        .merge(lambda d: {'coords': d['geo_point'].to_geojson()['coordinates']})\
        .pluck("coords", "id", "login", "location")\
        .run(conn)

    json_string = json.dumps(dict(
        user = user
    ))

    response = make_response(json_string)
    response.headers['Content-Type'] = "application/json"
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'X-AUTH-TOKEN, X-API-VERSION, X-Requested-With, Content-Type, Accept, Origin'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Max-Age'] = "1728000"
    return response

if __name__ == '__main__':
    app.run(debug=True)
