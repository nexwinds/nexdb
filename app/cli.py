"""
Command-line interface for NEXDB.
Provides commands for managing users and database.
"""
import click
import random
import string
from flask import Flask
from flask.cli import with_appcontext
from app.db.models import db, User
from app.auth.auth_manager import create_user, change_password

def register_cli_commands(app):
    """Register CLI commands with the Flask application."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_user_command)
    app.cli.add_command(reset_password_command)
    app.cli.add_command(list_users_command)

@click.command('init-db')
@click.option('--force', is_flag=True, help='Force recreate all tables')
@with_appcontext
def init_db_command(force):
    """Initialize the database."""
    from app.db.init_db import init_db
    click.echo('Initializing the database...')
    init_db(flask.current_app, force=force)
    click.echo('Database initialized successfully.')

@click.command('create-user')
@click.option('--username', prompt=True, help='Username for the new user')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password for the new user')
@click.option('--email', help='Email for the new user (optional)')
@click.option('--admin', is_flag=True, help='Create user as admin')
@with_appcontext
def create_user_command(username, password, email, admin):
    """Create a new user."""
    if len(password) < 8:
        click.echo('Error: Password must be at least 8 characters long')
        return
    
    user = create_user(username, password, email, admin)
    
    if user:
        click.echo(f"User '{username}' created successfully")
        if admin:
            click.echo("User has admin privileges")
    else:
        click.echo("Error: Username or email already exists")

@click.command('reset-password')
@click.option('--username', prompt=True, help='Username of the user')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='New password')
@click.option('--generate', is_flag=True, help='Generate a random password')
@with_appcontext
def reset_password_command(username, password, generate):
    """Reset a user's password."""
    user = User.query.filter_by(username=username).first()
    
    if not user:
        click.echo(f"Error: User '{username}' not found")
        return
    
    if generate:
        # Generate a secure random password
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choices(chars, k=16))
        click.echo(f"Generated password: {password}")
    
    if len(password) < 8:
        click.echo('Error: Password must be at least 8 characters long')
        return
    
    user.set_password(password)
    db.session.commit()
    
    click.echo(f"Password for '{username}' reset successfully")

@click.command('list-users')
@with_appcontext
def list_users_command():
    """List all users."""
    users = User.query.all()
    
    if not users:
        click.echo("No users found")
        return
    
    click.echo("ID | Username | Email | Admin | Last Login")
    click.echo("-" * 50)
    
    for user in users:
        admin_status = "Yes" if user.is_admin else "No"
        last_login = user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else "Never"
        click.echo(f"{user.id} | {user.username} | {user.email or 'N/A'} | {admin_status} | {last_login}") 