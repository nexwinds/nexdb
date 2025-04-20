"""
Database explorer controller for NEXDB.
Provides a lightweight PHPMyAdmin-like interface for database management.
"""
from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from app.auth.auth_manager import login_required, admin_required
from app.features.database.utils import get_mysql_manager, get_postgres_manager, format_db_size
import time

blueprint = Blueprint('db_explorer', __name__)

@blueprint.route('/')
@login_required
def index():
    """Display database explorer dashboard"""
    db_type = request.args.get('db_type', 'mysql')
    db_name = request.args.get('db_name', '')
    
    if db_type not in ['mysql', 'postgres']:
        flash('Invalid database type', 'danger')
        return redirect(url_for('database.db_explorer.index', db_type='mysql'))
    
    try:
        if db_type == 'mysql':
            db_manager = get_mysql_manager()
            databases = db_manager.list_databases()
            if not db_name and databases:
                db_name = databases[0]['name']
        else:
            db_manager = get_postgres_manager()
            databases = db_manager.list_databases()
            if not db_name and databases:
                db_name = databases[0]['name']
        
        # Get tables for the selected database
        tables = []
        if db_name:
            tables = db_manager.list_tables(db_name)
    except Exception as e:
        flash(f"Error connecting to database: {str(e)}", "danger")
        databases = []
        tables = []
    
    return render_template(
        'database/explorer/index.html',
        db_type=db_type,
        db_name=db_name,
        databases=databases,
        tables=tables
    )

@blueprint.route('/table')
@login_required
def view_table():
    """View table contents"""
    db_type = request.args.get('db_type')
    db_name = request.args.get('db_name')
    table_name = request.args.get('table_name')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', '')
    sort_dir = request.args.get('sort_dir', 'asc')
    
    if not db_type or not db_name or not table_name:
        flash('Missing required parameters', 'danger')
        return redirect(url_for('database.db_explorer.index'))
    
    try:
        if db_type == 'mysql':
            db_manager = get_mysql_manager()
        else:
            db_manager = get_postgres_manager()
        
        # Get table structure
        structure = db_manager.get_table_structure(db_name, table_name)
        
        # Get total records count
        total_records = db_manager.count_records(db_name, table_name, search)
        
        # Get table data
        offset = (page - 1) * limit
        data = db_manager.get_table_data(
            db_name, 
            table_name, 
            offset=offset, 
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir
        )
        
        # Calculate pagination
        total_pages = (total_records + limit - 1) // limit
        
        return render_template(
            'database/explorer/table.html',
            db_type=db_type,
            db_name=db_name,
            table_name=table_name,
            structure=structure,
            data=data,
            total_records=total_records,
            page=page,
            limit=limit,
            total_pages=total_pages,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir
        )
    except Exception as e:
        flash(f"Error retrieving table data: {str(e)}", "danger")
        return redirect(url_for('database.db_explorer.index', db_type=db_type, db_name=db_name))

@blueprint.route('/query', methods=['GET', 'POST'])
@login_required
def run_query():
    """Run SQL query on database"""
    db_type = request.args.get('db_type') or request.form.get('db_type', 'mysql')
    db_name = request.args.get('db_name') or request.form.get('db_name', '')
    query = request.form.get('query', '')
    
    if not db_type or not db_name:
        flash('Database type and name are required', 'danger')
        return redirect(url_for('database.db_explorer.index'))
    
    results = None
    error = None
    affected_rows = 0
    execution_time = 0
    
    if request.method == 'POST' and query:
        try:
            if db_type == 'mysql':
                db_manager = get_mysql_manager()
            else:
                db_manager = get_postgres_manager()
            
            # Run query
            query_type = query.strip().split(' ')[0].upper()
            is_select = query_type == 'SELECT'
            
            start_time = time.time()
            if is_select:
                results = db_manager.run_query(db_name, query)
                affected_rows = len(results)
            else:
                affected_rows = db_manager.execute_query(db_name, query)
                results = []
            execution_time = round((time.time() - start_time) * 1000, 2)  # ms
            
            flash(f"Query executed successfully. {affected_rows} rows affected. Execution time: {execution_time}ms", "success")
        except Exception as e:
            error = str(e)
            flash(f"Error executing query: {error}", "danger")
    
    return render_template(
        'database/explorer/query.html',
        db_type=db_type,
        db_name=db_name,
        query=query,
        results=results,
        error=error,
        affected_rows=affected_rows,
        execution_time=execution_time
    )

@blueprint.route('/record', methods=['GET', 'POST'])
@login_required
def edit_record():
    """Edit or create record"""
    db_type = request.args.get('db_type')
    db_name = request.args.get('db_name')
    table_name = request.args.get('table_name')
    primary_key = request.args.get('primary_key')
    primary_value = request.args.get('primary_value')
    
    if not db_type or not db_name or not table_name:
        flash('Missing required parameters', 'danger')
        return redirect(url_for('database.db_explorer.index'))
    
    try:
        if db_type == 'mysql':
            db_manager = get_mysql_manager()
        else:
            db_manager = get_postgres_manager()
        
        # Get table structure
        structure = db_manager.get_table_structure(db_name, table_name)
        
        # Create or update record
        if request.method == 'POST':
            record_data = {}
            for field in structure:
                field_name = field['name']
                field_value = request.form.get(field_name, '')
                
                # Handle special cases like NULL values
                if field_value == 'NULL':
                    field_value = None
                
                record_data[field_name] = field_value
            
            if primary_key and primary_value:
                # Update existing record
                db_manager.update_record(db_name, table_name, primary_key, primary_value, record_data)
                flash('Record updated successfully', 'success')
            else:
                # Create new record
                db_manager.insert_record(db_name, table_name, record_data)
                flash('Record created successfully', 'success')
            
            return redirect(url_for('database.db_explorer.view_table', db_type=db_type, db_name=db_name, table_name=table_name))
        
        # Get record data if editing
        record = {}
        if primary_key and primary_value:
            record = db_manager.get_record(db_name, table_name, primary_key, primary_value)
        
        return render_template(
            'database/explorer/record.html',
            db_type=db_type,
            db_name=db_name,
            table_name=table_name,
            structure=structure,
            record=record,
            primary_key=primary_key,
            primary_value=primary_value
        )
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('database.db_explorer.view_table', db_type=db_type, db_name=db_name, table_name=table_name))

@blueprint.route('/delete-record', methods=['POST'])
@login_required
def delete_record():
    """Delete record"""
    db_type = request.form.get('db_type')
    db_name = request.form.get('db_name')
    table_name = request.form.get('table_name')
    primary_key = request.form.get('primary_key')
    primary_value = request.form.get('primary_value')
    
    if not db_type or not db_name or not table_name or not primary_key or not primary_value:
        flash('Missing required parameters', 'danger')
        return redirect(url_for('database.db_explorer.index'))
    
    try:
        if db_type == 'mysql':
            db_manager = get_mysql_manager()
        else:
            db_manager = get_postgres_manager()
        
        # Delete record
        db_manager.delete_record(db_name, table_name, primary_key, primary_value)
        flash('Record deleted successfully', 'success')
    except Exception as e:
        flash(f"Error deleting record: {str(e)}", "danger")
    
    return redirect(url_for('database.db_explorer.view_table', db_type=db_type, db_name=db_name, table_name=table_name)) 