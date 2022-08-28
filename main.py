from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice
import pandas as pd

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=['GET'])
def random():
    cafes = db.session.query(Cafe).all()

    random_cafe = choice(cafes)
    """
    data = jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
    })
    """

    data = jsonify(cafe=random_cafe.to_dict())

    return data


# HTTP GET - Read Record


@app.route("/all", methods=['GET'])
def all_cafes():
    cafes = db.session.query(Cafe).all()
    """
    csv = ",".join(cafes[0].to_dict().keys()) + "\n"
    for cafe in cafes:
        line = ",".join(map(str, cafe.to_dict().values())) + "\n"
        csv = csv + line
    print(csv)
    return csv
    """
    data = [cafe.to_dict() for cafe in cafes]
    return jsonify(all_cafes=data)


# @app.route("/search/<location>", methods=['GET'])
# def search(location):
@app.route("/search", methods=['GET'])
def search():
    location = request.args.get("location")
    cafes = db.session.query(Cafe).filter_by(location=location)
    # cafes = Cafe.query.filter_by(location=location) == this returns empty list if not available
    # cafes = Cafe.query.filter_by(location=location).first() == this returns a None object if not available

    if cafes:
        data = [cafe.to_dict() for cafe in cafes]
        return jsonify(cafes=data)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


# HTTP POST - Create Record

@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )

    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record

@app.route("/update_price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = int(request.args.get("new_price"))
    cafe_to_be_updated = db.session.query(Cafe).filter_by(id=cafe_id).first()
    # cafe_to_be_updated = db.session.query(Cafe).get(cafe_id)

    if cafe_to_be_updated:
        if isinstance(new_price, int):
            cafe_to_be_updated.coffee_price = new_price
            db.session.commit()

            return jsonify(success="successfully updated the price"), 200
        else:
            return jsonify(error={"input error": "sorry, please input a correct value."}), 404
    else:
        return jsonify(error={"not found": "sorry, we do not have a cafe with this id"}), 404


# HTTP DELETE - Delete Record

@app.route("/report_closed/<int:cafe_id>", methods=["DELETE"])
def report_closed(cafe_id):
    key = request.args.get("key")
    cafe_to_be_closed = db.session.query(Cafe).filter_by(id=cafe_id).first()
    # cafe_to_be_updated = db.session.query(Cafe).get(cafe_id)

    if key == "TOPSECRET":

        if cafe_to_be_closed:
            db.session.delete(cafe_to_be_closed)
            db.session.commit()

            return jsonify(success="successfully closed this cafe"), 200
        else:
            return jsonify(error={"not found": "sorry, we do not have a cafe with this id"}), 404

    else:
        return jsonify(error={"invalid key": "sorry, you do not have the key to perform this action"}), 404


if __name__ == '__main__':
    app.run(debug=True)

# https://documenter.getpostman.com/view/3110543/VUjTmPjS
