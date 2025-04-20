"""
PostgreSQL database controller for NEXDB.
Provides endpoints for managing PostgreSQL databases and users.
"""
from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from app.utils.postgres_manager import PostgresManager

blueprint = Blueprint('postgres', __name__)

@blueprint.route('/')
def index():
    """Display PostgreSQL database management dashboard"""
    postgres_manager = PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )
    
    try:
        databases = postgres_manager.list_databases()
        users = postgres_manager.list_users()
        status = postgres_manager.get_status()
    except Exception as e:
        flash(f"Error connecting to PostgreSQL: {str(e)}", "danger")
        databases = []
        users = []
        status = False
    
    return render_template(
        'database/postgres/index.html',
        databases=databases,
        users=users,
        status=status
    )

@blueprint.route('/database/create', methods=['POST'])
def create_database():
    """Create a new PostgreSQL database"""
    name = request.form.get('name')
    owner = request.form.get('owner', current_app.config['POSTGRES_USER'])
    
    if not name:
        flash("Database name is required", "danger")
        return redirect(url_for('database.postgres.index'))
    
    postgres_manager = PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )
    
    try:
        postgres_manager.create_database(name, owner)
        flash(f"Database {name} created successfully", "success")
    except Exception as e:
        flash(f"Error creating database: {str(e)}", "danger")
    
    return redirect(url_for('database.postgres.index'))

@blueprint.route('/database/delete', methods=['POST'])
def delete_database():
    """Delete a PostgreSQL database"""
    name = request.form.get('name')
    
    if not name:
        flash("Database name is required", "danger")
        return redirect(url_for('database.postgres.index'))
    
    postgres_manager = PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )
    
    try:
        postgres_manager.delete_database(name)
        flash(f"Database {name} deleted successfully", "success")
    except Exception as e:
        flash(f"Error deleting database: {str(e)}", "danger")
    
    return redirect(url_for('database.postgres.index'))

@blueprint.route('/user/create', methods=['POST'])
def create_user():
    """Create a new PostgreSQL user"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash("Username and password are required", "danger")
        return redirect(url_for('database.postgres.index'))
    
    postgres_manager = PostgresManager(
        host=current_app.config['POSTGRES_HOST'],
        port=current_app.config['POSTGRES_PORT'],
        user=current_app.config['POSTGRES_USER'],
        password=current_app.config['POSTGRES_PASSWORD']
    )
    
    try:
        postgres_manager.create_user(username, password)
        flash(f"User {username} created successfully", "success")
    except Exception as e:
        flash(f"Error creating user: {str(e)}", "danger")
    
    return redirect(url_for('database.postgres.index')) 