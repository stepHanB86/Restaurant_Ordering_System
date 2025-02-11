from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine, text

# Initialize Flask app

app = Flask(__name__)


# Define MySQL database

username = 'root'
password = ''
host = 'localhost'
database = 'restaurant'


# Create SQLAlchemy engine to connect to MySQL

engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/')
with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {database}"))


# Configure Flask app to use database

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# Define 'Bestellung' (represents an order)

class Bestellung(db.Model):
    __tablename__ = 'bestellungen'
    bestellnummer = db.Column(db.Integer, primary_key=True)
    tisch_nr = db.Column(db.Integer, nullable=False)
    bestellzeit = db.Column(db.DateTime, default=datetime.utcnow)
    gesamtpreis = db.Column(db.Numeric(10,2), default=0.00)
    positionen = db.relationship('Bestellposition', backref='bestellung', lazy=True)


# Define 'Bestellposition' (for order items)

class Bestellposition(db.Model):
    __tablename__ = 'bestellpositionen'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bestellnummer = db.Column(db.Integer, db.ForeignKey('bestellungen.bestellnummer'), nullable=False)
    artikel_nr = db.Column(db.Integer, db.ForeignKey('sortiment.artikel_nr'), nullable=False)
    menge = db.Column(db.Integer, default=0)
    einzelpreis = db.Column(db.Numeric(10,2), nullable=False)
    sortiment = db.relationship("Sortiment", backref="bestellpositionen", lazy=True)


# Define 'Sortiment' (for items on the menu)

class Sortiment(db.Model):
    __tablename__ = 'sortiment'
    artikel_nr = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    beschreibung = db.Column(db.Text)
    preis = db.Column(db.Numeric(10,2), nullable=False, default=0.00)
    kategorie = db.Column(db.String(50))
    rezept_id = db.Column(db.Integer)
    verkauft = db.Column(db.Integer, default=0)



# Define 'Tisch' (for table in Restaurant)

class Tisch(db.Model):
    __tablename__ = 'tische'
    tisch_nr = db.Column(db.Integer, primary_key=True)
    kapazitaet = db.Column(db.Integer, nullable=False)



# Define root route (redirecting to order view)

@app.route("/")
def index():
    return redirect(url_for('bestellung_view'))



# Define route for creating new order - accepts GET and POST

@app.route("/bestellung", methods=['GET', 'POST'], endpoint="bestellung_view")
def bestellung():
    sortiment_items = Sortiment.query.order_by(Sortiment.verkauft.desc()).all()                            # Get all menu items from Sortiment table (ordered by number sold descending
    menu_items = [{                                                                                        # Create list of menu items as dictionaries
        "artikel_nr": item.artikel_nr,
        "name": item.name,
        "preis": float(item.preis)
    } for item in sortiment_items]
    
    if request.method == 'POST':
        try:
            tisch_nr = int(request.form.get('tableNumber'))
        except (ValueError, TypeError):
            return "Ungültige Tischnummer", 400
        if not Tisch.query.get(tisch_nr):                                                                   # Create new table entry with default capacity, if table not exists
            neuer_tisch = Tisch(tisch_nr=tisch_nr, kapazitaet=4)
            db.session.add(neuer_tisch)
            db.session.flush()
        neue_bestellung = Bestellung(tisch_nr=tisch_nr)                                                     # Create new order 
        db.session.add(neue_bestellung)
        db.session.flush()
        for art in sortiment_items:                                                                         # Loop through menu items to get ordered quantities                                        
            menge_str = request.form.get(str(art.artikel_nr))
            try:
                menge = int(menge_str)
            except (ValueError, TypeError):
                menge = 0
            if menge > 0:                                                                                   # If quantity > 0, create order position
                bp = Bestellposition(
                    bestellnummer=neue_bestellung.bestellnummer,
                    artikel_nr=art.artikel_nr,
                    menge=menge,
                    einzelpreis=art.preis
                )
                db.session.add(bp)
                art.verkauft += menge
        db.session.commit()
        return redirect(url_for('bestellungen'))
    return render_template("bestellung.html", sortiment_items=sortiment_items, menu_items=menu_items)        # If request method is GET, render order page



# Define route for displaying all orders

@app.route("/bestellungen")
def bestellungen():
    orders = Bestellung.query.order_by(Bestellung.bestellzeit.desc()).all()
    return render_template("bestellungen.html", orders=orders)


# Run app

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False)

