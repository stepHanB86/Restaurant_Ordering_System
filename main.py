from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine, text

app = Flask(__name__)


# Application Initialization

def init_app():
    print("Initialization before the first request")


# Before Request Handler (Run Once)

@app.before_request
def run_once():
    if not getattr(app, '_got_first_request', False):
        init_app()
        create_sortiment_if_needed()
        app._got_first_request = True


# Database Configuration

username = 'root'
password =
host = 'localhost'
database = 'restaurant'

# Create the database if it does not exist.
engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}/')
with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {database}"))

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Model Definitions

class Bestellung(db.Model):
    __tablename__ = 'bestellungen'
    id = db.Column(db.Integer, primary_key=True)
    tisch_nr = db.Column(db.Integer, nullable=False)
    datum = db.Column(db.DateTime, default=datetime.utcnow)
    positionen = db.relationship('Bestellposition', backref='bestellung', lazy=True)

class Bestellposition(db.Model):
    __tablename__ = 'bestellpositionen'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bestellung_id = db.Column(db.Integer, db.ForeignKey('bestellungen.id'), nullable=False)
    sortiment_artikel_nr = db.Column(db.Integer, db.ForeignKey('sortiment.artikel_nr'), nullable=False)
    menge = db.Column(db.Integer, default=0)
    einzelpreis = db.Column(db.Numeric(10,2), nullable=False)

class Sortiment(db.Model):
    __tablename__ = 'sortiment'
    artikel_nr = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    beschreibung = db.Column(db.Text)
    preis = db.Column(db.Numeric(10,2), nullable=False, default=0.00)
    kategorie = db.Column(db.String(50))
    rezept_id = db.Column(db.Integer)
    verkauft = db.Column(db.Integer, default=0)


# Route Definitions

@app.route("/")
def index():
    return redirect(url_for('bestellung_view'))

@app.route("/bestellung", methods=['GET', 'POST'], endpoint="bestellung_view")
def bestellung():
    sortiment_items = Sortiment.query.order_by(Sortiment.verkauft.desc()).all()
    menu_items = [{"id": item.artikel_nr, "name": item.name} for item in sortiment_items]
    
    if request.method == 'POST':
        tisch_nr = request.form.get('tableNumber')
        neue_bestellung = Bestellung(tisch_nr=tisch_nr)
        db.session.add(neue_bestellung)
        db.session.flush()

        for art in sortiment_items:
            menge_str = request.form.get(str(art.artikel_nr))
            try:
                menge = int(menge_str)
            except (ValueError, TypeError):
                menge = 0
            if menge > 0:
                bp = Bestellposition(
                    bestellung_id=neue_bestellung.id,
                    sortiment_artikel_nr=art.artikel_nr,
                    menge=menge,
                    einzelpreis=art.preis
                )
                db.session.add(bp)
                art.verkauft += menge
        db.session.commit()
        return redirect(url_for('bestellungen'))
    
    return render_template("bestellung.html", sortiment_items=sortiment_items, menu_items=menu_items)

@app.route("/bestellungen")
def bestellungen():
    orders = Bestellung.query.order_by(Bestellung.datum.desc()).all()
    return render_template("bestellungen.html", orders=orders)


# Run App

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False)
