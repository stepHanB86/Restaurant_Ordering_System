from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine, text

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "dein_geheimer_schluessel"

# Database configuration
username = 'root'
password = ''
host = 'localhost'
database = 'restaurant'

# Create  SQLAlchemy engine and database
engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/')
with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {database}"))

# Configure Flask app to use SQLAlchemy with MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define SQLAlchemy models
class Bestellung(db.Model):
    __tablename__ = 'bestellungen'
    bestellnummer = db.Column(db.Integer, primary_key=True)
    tisch_nr = db.Column(db.Integer, nullable=False)
    bestellzeit = db.Column(db.DateTime, default=datetime.utcnow)
    gesamtpreis = db.Column(db.Numeric(10, 2), default=0.00)
    bezahlt = db.Column(db.Boolean, default=False)
    positionen = db.relationship('Bestellposition', backref='bestellung', lazy=True)

class SortimentView(db.Model):
    __tablename__ = 'sortiment'
    __table_args__ = {'extend_existing': True}
    artikel_nr = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    beschreibung = db.Column(db.Text)
    preis = db.Column(db.Numeric(10, 2))
    kategorie = db.Column(db.String(50))
    verkauft = db.Column(db.Integer)

class Bestellposition(db.Model):
    __tablename__ = 'bestellpositionen'
    bestellposition_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bestellnummer = db.Column(db.Integer, db.ForeignKey('bestellungen.bestellnummer'), nullable=False)
    artikel_nr = db.Column(db.Integer, db.ForeignKey('sortiment.artikel_nr'), nullable=False)
    menge = db.Column(db.Integer, default=0)
    einzelpreis = db.Column(db.Numeric(10, 2), nullable=False)
    sortiment = db.relationship("SortimentView",
                                 primaryjoin="Bestellposition.artikel_nr==SortimentView.artikel_nr",
                                 viewonly=True)

class Getraenke(db.Model):
    __tablename__ = 'getraenke'
    artikel_nr = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    preis = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    unterkategorie = db.Column(db.String(50))
    posten = db.Column(db.String(30))
    verkauft = db.Column(db.Integer, default=0)
    groesse = db.Column(db.Numeric(3, 2), nullable=False, default=0.00)

class Speisen(db.Model):
    __tablename__ = 'speisen'
    artikel_nr = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    preis = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    unterkategorie = db.Column(db.String(50))
    posten = db.Column(db.String(30))
    verkauft = db.Column(db.Integer, default=0)
    beschreibung = db.Column(db.Text)

class Pizza(db.Model):
    __tablename__ = 'pizza'
    artikel_nr = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    preis = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    unterkategorie = db.Column(db.String(50))
    posten = db.Column(db.String(30))
    verkauft = db.Column(db.Integer, default=0)
    groesse = db.Column(db.String(10))
    beschreibung = db.Column(db.Text)

class Tisch(db.Model):
    __tablename__ = 'tische'
    tisch_nr = db.Column(db.Integer, primary_key=True)
    kapazitaet = db.Column(db.Integer, nullable=False)

# Functions for cart and order management
def add_item_to_cart(item, menge):
    cart = session.get("cart", {})
    key = str(item["artikel_nr"])
    cart[key] = {
        "artikel_nr": item["artikel_nr"],
        "name": item["name"],
        "preis": item["preis"],
        "quantity": menge,
        "category": item.get("category", ""),
        "remarks": cart.get(key, {}).get("remarks", "")
    }
    session["cart"] = cart

def ensure_tisch_exists(tisch_nr):
    if not Tisch.query.get(tisch_nr):
        neuer_tisch = Tisch(tisch_nr=tisch_nr, kapazitaet=4)
        db.session.add(neuer_tisch)
        db.session.commit()

def create_new_order(tisch_nr):
    ensure_tisch_exists(tisch_nr)
    new_order = Bestellung(tisch_nr=tisch_nr)
    db.session.add(new_order)
    db.session.commit()
    return new_order

def get_open_orders(tisch_nr):
    ensure_tisch_exists(tisch_nr)
    orders = Bestellung.query.filter_by(tisch_nr=tisch_nr, bezahlt=False).order_by(Bestellung.bestellzeit.desc()).all()
    return orders

# Define route for AJAX endpoint to add item to the cart
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart_route():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    item = data.get("item")
    quantity = data.get("quantity", 0)
    tableNumber = data.get("tableNumber")
    if not tableNumber:
        return jsonify({"error": "Tischnummer fehlt"}), 400
    session["tableNumber"] = tableNumber
    add_item_to_cart(item, quantity)
    return jsonify({"message": "Item added", "cart": session.get("cart")})

# Define index route to redirect to order page
@app.route("/")
def index():
    return redirect(url_for('getraenke_view'))

# Define the route for drinks order page
@app.route("/bestellung", methods=['GET'], endpoint="getraenke_view")
def getraenke_bestellung():
    getraenke_items = Getraenke.query.order_by(Getraenke.verkauft.desc()).all()
    menu_items = [{
        "artikel_nr": item.artikel_nr,
        "name": item.name,
        "preis": float(item.preis),
        "groesse": float(item.groesse),
        "category": "Getränke"
    } for item in getraenke_items]
    return render_template("bestellung.html", menu_items=menu_items)

# Define route for food order page
@app.route("/speisen", methods=['GET'], endpoint="speisen_view")
def speisen_bestellung():
    speisen_items = Speisen.query.order_by(Speisen.verkauft.desc()).all()
    menu_items = [{
        "artikel_nr": item.artikel_nr,
        "name": item.name,
        "preis": float(item.preis),
        "beschreibung": item.beschreibung or "",
        "category": "Speisen"
    } for item in speisen_items]
    return render_template("speisen.html", menu_items=menu_items)

# Define route for pizza order page
@app.route("/pizza", methods=['GET'], endpoint="pizza_view")
def pizza_bestellung():
    pizza_items = Pizza.query.order_by(Pizza.verkauft.desc()).all()
    menu_items = [{
        "artikel_nr": item.artikel_nr,
        "name": item.name,
        "preis": float(item.preis),
        "beschreibung": item.beschreibung or "",
        "category": "Pizza"
    } for item in pizza_items]
    return render_template("pizza.html", menu_items=menu_items)

# Define route for cart view order submission
@app.route("/warenkorb", methods=["GET", "POST"], endpoint="warenkorb_view")
def warenkorb_view():
    cart = session.get("cart", {})
    total = sum(item["preis"] * item["quantity"] for item in cart.values())
    tableNumber = session.get("tableNumber", None)
    if request.method == "POST":
        if not tableNumber:
            return "Tischnummer fehlt", 400
        order = create_new_order(tableNumber)
        for item in cart.values():
            bp = Bestellposition(
                bestellnummer=order.bestellnummer,
                artikel_nr=item["artikel_nr"],
                menge=item["quantity"],
                einzelpreis=item["preis"]
            )
            db.session.add(bp)
        order.gesamtpreis = float(order.gesamtpreis) + total
        db.session.commit()
        session.pop("cart", None)
        session.pop("tableNumber", None)
        return redirect(url_for("bestellungen"))
    return render_template("warenkorb.html", cart=cart, total=total, tableNumber=tableNumber)

# Define route for payment view
@app.route("/bezahlen", methods=["GET", "POST"], endpoint="bezahlen_view")
def bezahlen():
    if request.method == "POST":
        if "tableNumber" in request.form:
            try:
                tisch_nr = int(request.form.get("tableNumber"))
            except (ValueError, TypeError):
                return "Ungültige Tischnummer", 400
            orders = get_open_orders(tisch_nr)
            if not orders:
                return render_template("bezahlen.html", error="Keine offene Bestellung für diesen Tisch gefunden.", orders=None)
            else:
                return render_template("bezahlen.html", orders=orders)
        elif "payment_method" in request.form:
            try:
                tisch_nr = int(request.form.get("tisch_nr"))
            except (ValueError, TypeError):
                return "Ungültige Tischnummer", 400
            orders = get_open_orders(tisch_nr)
            if not orders:
                return "Keine offene Bestellung gefunden", 404
            for order in orders:
                order.bezahlt = True
            db.session.commit()
            return redirect(url_for("bestellungen"))
    return render_template("bezahlen.html", orders=None)

# Define route to display all orders
@app.route("/bestellungen")
def bestellungen():
    orders = Bestellung.query.order_by(Bestellung.bestellzeit.desc()).all()
    return render_template("bestellungen.html", orders=orders)

# Run app - create database
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False)

