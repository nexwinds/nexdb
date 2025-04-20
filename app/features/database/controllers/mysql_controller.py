"""
MySQL database controller for NEXDB.
Provides endpoints for managing MySQL databases and users.
"""
from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from app.utils.mysql_manager import MySQLManager

blueprint = Blueprint('mysql', __name__)

@blueprint.route('/')
def index():
    """Display MySQL database management dashboard"""
    mysql_manager = MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    
    try:
        databases = mysql_manager.list_databases()
        users = mysql_manager.list_users()
        status = mysql_manager.get_status()
    except Exception as e:
        flash(f"Error connecting to MySQL: {str(e)}", "danger")
        databases = []
        users = []
        status = False
    
    return render_template(
        'database/mysql/index.html',
        databases=databases,
        users=users,
        status=status
    )

@blueprint.route('/database/create', methods=['POST'])
def create_database():
    """Create a new MySQL database"""
    name = request.form.get('name')
    charset = request.form.get('charset', 'utf8mb4')
    collation = request.form.get('collation', 'utf8mb4_unicode_ci')
    
    if not name:
        flash("Database name is required", "danger")
        return redirect(url_for('database.mysql.index'))
    
    mysql_manager = MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    
    try:
        mysql_manager.create_database(name, charset, collation)
        flash(f"Database {name} created successfully", "success")
    except Exception as e:
        flash(f"Error creating database: {str(e)}", "danger")
    
    return redirect(url_for('database.mysql.index'))

@blueprint.route('/database/delete', methods=['POST'])
def delete_database():
    """Delete a MySQL database"""
    name = request.form.get('name')
    
    if not name:
        flash("Database name is required", "danger")
        return redirect(url_for('database.mysql.index'))
    
    mysql_manager = MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    
    try:
        mysql_manager.delete_database(name)
        flash(f"Database {name} deleted successfully", "success")
    except Exception as e:
        flash(f"Error deleting database: {str(e)}", "danger")
    
    return redirect(url_for('database.mysql.index'))

@blueprint.route('/user/create', methods=['POST'])
def create_user():
    """Create a new MySQL user"""
    username = request.form.get('username')
    password = request.form.get('password')
    host = request.form.get('host', '%')
    
    if not username or not password:
        flash("Username and password are required", "danger")
        return redirect(url_for('database.mysql.index'))
    
    mysql_manager = MySQLManager(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD']
    )
    
    try:
        mysql_manager.create_user(username, password, host)
        flash(f"User {username} created successfully", "success")
    except Exception as e:
        flash(f"Error creating user: {str(e)}", "danger")
    
    return redirect(url_for('database.mysql.index')) 