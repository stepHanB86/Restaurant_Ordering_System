# Restaurant Ordering System

A Flask-based web application for managing restaurant orders - with a dynamic product catalog, a shopping cart system, and a payment workflow. The system uses SQLAlchemy with a MySQL database.

## Overview

This project is a restaurant ordering system that allows staff to:
- Browse a product catalog divided into categories
- Add items from different categories to a persistent shopping cart.
- Finalize orders per table, where each new order is created separately.
- View all open and past orders and process payments by aggregating open orders for a table.

The app automatically creates the required SQL tables (including tables for employees, customers, reservations, orders, order items, invoices, and product catalogs) and includes a view that integrates products from multiple categories.

## Current Features

- **Product Catalog:** Displays beverages, food, and pizza items; each category has its own page.
- **Shopping Cart:** Persistent cart that retains  table number and selected items across navigation.
- **Order Management:** New orders are created per table; if a table has unpaid orders, they are kept separate and later aggregated on the payment page.
- **Payment Workflow:** The payment page aggregates all open orders for a table and allows payment via cash or card.
- **Database Integration:** Uses SQLAlchemy to interact with a MySQL/MariaDB database, with automatic creation and population of necessary tables.
- **AJAX Integration:** Utilizes AJAX for adding items to cart, ensuring dynamic and responsive user experience.

## Future Enhancements

- **Frontend Modernization:** Redevelop frontend with Flutter for a cross-platform user experience.
- **Kitchen Display System:** Integrate features to improve kitchen workflow and order tracking.
- **Integrated Cash Register:** Incorporate a fully functional cash register system.
- **Advanced Analytics:** Enhance data collection and analytics to support business insights.

## Setup

- Python 3.x
- MySQL or MariaDB
- Required Python packages (Flask, Flask-SQLAlchemy, PyMySQL)


