CREATE DATABASE restaurant
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;
USE restaurant;

CREATE TABLE mitarbeiter (
    mitarbeiter_id INT AUTO_INCREMENT PRIMARY KEY,
    nachname VARCHAR(50) NOT NULL,
    vorname VARCHAR(50) NOT NULL,
    adresse VARCHAR(100) NOT NULL,
    plz VARCHAR(10) NOT NULL,
    ort VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    telefon VARCHAR(20),
    abteilung VARCHAR(50) NOT NULL,
    eintrittsdatum DATE NOT NULL,
    gehalt DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tische (
    tisch_nr INT PRIMARY KEY,
    kapazitaet INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE kunden (
    kunde_id INT AUTO_INCREMENT PRIMARY KEY,
    vorname VARCHAR(50),
    nachname VARCHAR(50),
    telefon VARCHAR(20),
    email VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE reservierungen (
    reservierung_id INT AUTO_INCREMENT PRIMARY KEY,
    kunde_id INT NOT NULL,
    tisch_nr INT NOT NULL,
    reservierungszeit DATETIME NOT NULL,
    anzahl_personen INT NOT NULL,
    FOREIGN KEY (kunde_id) REFERENCES kunden(kunde_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (tisch_nr) REFERENCES tische(tisch_nr)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE bestellungen (
    bestellnummer INT AUTO_INCREMENT PRIMARY KEY,
    tisch_nr INT NOT NULL,
    mitarbeiter_id INT,
    kunde_id INT,
    bestellzeit DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gesamtpreis DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (tisch_nr) REFERENCES tische(tisch_nr)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (mitarbeiter_id) REFERENCES mitarbeiter(mitarbeiter_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (kunde_id) REFERENCES kunden(kunde_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE bestellpositionen (
    bestellposition_id INT AUTO_INCREMENT PRIMARY KEY,
    bestellnummer INT NOT NULL,
    artikel_nr INT NOT NULL,
    menge INT NOT NULL,
    einzelpreis DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (bestellnummer) REFERENCES bestellungen(bestellnummer)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE rechnungen (
    rechnung_id INT AUTO_INCREMENT PRIMARY KEY,
    bestellung_id INT NOT NULL,
    rechnungsdatum DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    betrag DECIMAL(10,2) NOT NULL,
    bezahlt BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (bestellung_id) REFERENCES bestellungen(bestellnummer)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE getraenke (
    artikel_nr INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    preis DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    unterkategorie VARCHAR(50),
    posten VARCHAR(30),
    verkauft INT DEFAULT 0,
    groesse DECIMAL(3,2) NOT NULL DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE speisen (
    artikel_nr INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    preis DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    unterkategorie VARCHAR(50),
    posten VARCHAR(30),
    verkauft INT DEFAULT 0,
    beschreibung TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE pizza (
    artikel_nr INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    preis DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    unterkategorie VARCHAR(50),
    posten VARCHAR(30),
    verkauft INT DEFAULT 0,
    groesse VARCHAR(10),
    beschreibung TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE OR REPLACE VIEW sortiment AS
SELECT artikel_nr, name, preis, 'Getränke' AS kategorie, NULL AS beschreibung, verkauft
FROM getraenke
UNION ALL
SELECT artikel_nr, name, preis, 'Speisen' AS kategorie, beschreibung, verkauft
FROM speisen
UNION ALL
SELECT artikel_nr, name, preis, 'Pizza' AS kategorie, beschreibung, verkauft
FROM pizza;
