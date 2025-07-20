from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import os
import logging

# Make sure these imports work
try:
    from Audit_local import process_audit_file
    from update_descriptions import update_descriptions
    from pass_fail import determine_pass_fail
    from report import run_report
except ImportError as e:
    print(f"Import error: {e}")

from openpyxl import load_workbook

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'xlsx'}

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flashing messages
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder: str) -> str:
    filename = secure_filename(file.filename)
    filepath = os.path.join(folder, filename)
    file.save(filepath)
    return filepath

def process_excel_file(filepath: str, sheet_index: int = 1) -> pd.DataFrame:
    xl = pd.ExcelFile(filepath)
    sheet_names = xl.sheet_names
    print(sheet_names)
    logging.info(f"Sheet names in the uploaded file: {sheet_names}")
    if len(sheet_names) <= sheet_index:
        raise ValueError(f"File does not contain a sheet at index {sheet_index}.")
    data = pd.read_excel(filepath, sheet_name=sheet_names[sheet_index])
    return data, sheet_names[sheet_index]

def add_comments_column(df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty and 'Comments' not in df.columns:
        df['Comments'] = ''
    return df

def hide_columns(sheet):
    columns_to_hide = ['Year', 'Month', 'Day', 'COUNTRY', 'ROWNO', 'Start Date']
    for col_name in columns_to_hide:
        for cell in sheet[1]:  # First row for column names
            if cell.value == col_name:
                col_letter = cell.column_letter
                sheet.column_dimensions[col_letter].hidden = True
                break

def validate_and_save_files(file, rates_file, sob_file):
    """Validate main file and save all uploaded files"""
    if not file or file.filename == '':
        return None, 'No selected file'
    if not allowed_file(file.filename):
        return None, 'Invalid file type. Only .xlsx files are allowed.'
    
    file_filepath = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
    rates_filepath = save_uploaded_file(rates_file, app.config['UPLOAD_FOLDER']) if rates_file and rates_file.filename else None
    sob_filepath = save_uploaded_file(sob_file, app.config['UPLOAD_FOLDER']) if sob_file and sob_file.filename else None
    
    return (file_filepath, rates_filepath, sob_filepath), None

def parse_form_integers(form):
    """Parse and validate form integer inputs"""
    try:
        local = int(form['local'])
        core = form.get('core', '').strip()
        noncore = form.get('noncore', '').strip()
        return local, int(core) if core else None, int(noncore) if noncore else None
    except ValueError:
        return None, 'Error: Please ensure local, core, and noncore values are integers or empty.'

def process_optional_file(filepath, sheet_index, file_type):
    """Process optional Excel files (rates/SOB)"""
    if not filepath:
        return None, None
    
    try:
        xl = pd.ExcelFile(filepath)
        sheet_name = xl.sheet_names[sheet_index]
        data = pd.read_excel(filepath, sheet_name=sheet_name)
        logging.info(f"Columns in {file_type} file: {data.columns.tolist()}")
        return data, sheet_name
    except Exception as e:
        raise Exception(f'Error processing {file_type} file: {e}')

def filter_and_prepare_data(data, local, core, noncore, filter_column):
    """Filter data by subscript numbers and add comments column"""
    datasets = {
        'Local': data[data[filter_column] == local],
        'Core': data[data[filter_column] == core] if core is not None else pd.DataFrame(),
        'NonCore': data[data[filter_column] == noncore] if noncore is not None else pd.DataFrame()
    }
    
    return {name: add_comments_column(df) for name, df in datasets.items()}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    # Validate and save files
    file_paths, error = validate_and_save_files(
        request.files['file'], 
        request.files.get('rates'), 
        request.files.get('SOB')
    )
    if error:
        flash(error)
        return redirect(url_for('index'))
    
    file_filepath, rates_filepath, sob_filepath = file_paths

    # Parse form data
    form_result = parse_form_integers(request.form)
    if len(form_result) == 2:  # Error case
        flash(form_result[1])
        return redirect(url_for('index'))
    local, core, noncore = form_result

    # Process files
    try:
        data, sheet_name = process_excel_file(file_filepath)
        rates_data, rates_sheet_name = process_optional_file(rates_filepath, -1, 'rates')
        sob_data, _ = process_optional_file(sob_filepath, 0, 'SOB')
    except Exception as e:
        flash(str(e))
        return redirect(url_for('index'))

    # Validate filter column
    filter_column = 'Subscript Number'
    if filter_column not in data.columns:
        flash(f'Error: Column "{filter_column}" not found in sheet "{sheet_name}". Columns present: {data.columns.tolist()}')
        return redirect(url_for('index'))

    # Filter and prepare data
    datasets = filter_and_prepare_data(data, local, core, noncore, filter_column)

    # Write Excel file
    processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_data.xlsx')
    with pd.ExcelWriter(processed_filepath) as writer:
        for name, df in datasets.items():
            if not df.empty:
                df.to_excel(writer, sheet_name=name, index=False)
        if rates_data is not None:
            rates_data.to_excel(writer, sheet_name=rates_sheet_name, index=False)
        if sob_data is not None:
            sob_data.to_excel(writer, sheet_name='SOB', index=False)

    # Hide columns
    wb = load_workbook(processed_filepath)
    for sheet in wb.worksheets:
        hide_columns(sheet)
    wb.save(processed_filepath)

    return render_template('upload_success.html',
                           local=local, core=core, noncore=noncore,
                           sob_uploaded=sob_data is not None)

@app.route('/download')
def download_file():
    filepath = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_data.xlsx')
    return send_file(filepath, as_attachment=True)

@app.route('/audit_local', methods=['GET', 'POST'])
def audit_local():
    if request.method == 'POST':
        user_input = request.form.get('employee_type', 'yes')
        file_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_data.xlsx')
        
        try:
            # Import and call the function from Audit_local.py
            from Audit_local import compare_local_with_sob
            
            # Load data
            xl = pd.ExcelFile(file_path)
            local_data = pd.read_excel(xl, sheet_name='Local')
            sob_data = pd.read_excel(xl, sheet_name='SOB')
            
            # Process data
            updated_local_data = compare_local_with_sob(local_data, sob_data, user_input)
            
            # Save results
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                updated_local_data.to_excel(writer, sheet_name='Local', index=False)
            
            # Redirect to a page that prompts for manual review
            return redirect(url_for('manual_review'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('index'))
    
    return render_template('audit_local.html')

@app.route('/manual_review')
def manual_review():
    # This page will instruct the user to download, review, and re-upload the file
    return render_template('manual_review.html')

@app.route('/upload_reviewed', methods=['GET', 'POST'])
def upload_reviewed():
    if request.method == 'POST':
        if 'reviewed_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['reviewed_file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            # Save the manually reviewed file
            filename = 'processed_data.xlsx'
            file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
            file.save(file_path)
            
            # Redirect to the next step
            return redirect(url_for('core_noncore'))
    
    return render_template('upload_reviewed.html')

@app.route('/core_noncore', methods=['GET', 'POST'])
def core_noncore():
    if request.method == 'POST':
        user_input = request.form.get('employee_type', 'yes')
        file_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_data.xlsx')
        
        try:
            # Import the process_data function from Core_noncore.py
            from Core_noncore import process_data
            
            # Call the process_data function with the file path and user input
            process_data(file_path, user_input)
            
            # Redirect to update descriptions step
            return redirect(url_for('update_descriptions'))
        except Exception as e:
            flash(str(e))
            return redirect(url_for('audit_local'))
    
    return render_template('core_noncore.html')

@app.route('/update_descriptions')
def update_descriptions():
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_data.xlsx')
    
    try:
        # Import and run update_descriptions.py logic
        from update_descriptions import run_update_descriptions
        run_update_descriptions(file_path)
        
        return redirect(url_for('pass_fail'))
    except Exception as e:
        flash(str(e))
        return redirect(url_for('core_noncore'))

@app.route('/pass_fail')
def pass_fail():
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_data.xlsx')
    
    try:
        # Import and run pass_fail.py logic
        from pass_fail import run_pass_fail
        run_pass_fail(file_path)
        
        return redirect(url_for('generate_report'))
    except Exception as e:
        flash(str(e))
        return redirect(url_for('update_descriptions'))

@app.route('/generate_report')
def generate_report():
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_data.xlsx')
    
    try:
        # Import and run report.py logic
        from report import run_report
        run_report(file_path)
        
        return redirect(url_for('final_result'))
    except Exception as e:
        flash(str(e))
        return redirect(url_for('pass_fail'))

@app.route('/final_result')
def final_result():
    # This is the final page showing completion of all steps
    return render_template('final_result.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
