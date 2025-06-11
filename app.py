from flask import Flask, request, render_template, send_file # type: ignore
import pandas as pd # type: ignore
import os
from openpyxl import load_workbook # type: ignore

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    rates_file = request.files.get('rates')  # Get rates file if it exists

    if file.filename == '':
        return 'No selected file'
    if file:
        file_filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_filepath)
        rates_filepath = None
        if rates_file and rates_file.filename != '':
            rates_filepath = os.path.join(app.config['UPLOAD_FOLDER'], rates_file.filename)
            rates_file.save(rates_filepath)

        try:
            local = int(request.form['local'])
            core = request.form.get('core', '').strip()
            noncore = request.form.get('noncore', '').strip()
            core = int(core) if core else None
            noncore = int(noncore) if noncore else None
        except ValueError:
            return 'Error: Please ensure local, core, and noncore values are integers or empty.'

        try:
            xl = pd.ExcelFile(file_filepath)
            sheet_names = xl.sheet_names
            print(f"Sheet names in the uploaded file: {sheet_names}")
            sheet_name = sheet_names[1]  # Automatically select the second sheet
            data = pd.read_excel(file_filepath, sheet_name=sheet_name)
        except Exception as e:
            return f'Error processing file: {e}'

        rates_data = None
        if rates_filepath:
            try:
                rates_xl = pd.ExcelFile(rates_filepath)
                rates_last_sheet_name = rates_xl.sheet_names[-1]  # Get the last sheet
                rates_data = pd.read_excel(rates_filepath, sheet_name=rates_last_sheet_name)
                print(f"Columns in rates file: {rates_data.columns.tolist()}")
            except Exception as e:
                return f'Error processing rates file: {e}'

        # Print out the column names for debugging
        print(f"Columns in sheet '{sheet_name}': {data.columns.tolist()}")

        filter_column = 'Subscript Number'  # Use the correct column name

        if filter_column not in data.columns:
            return f'Error: Column "{filter_column}" not found in sheet "{sheet_name}". Columns present: {data.columns.tolist()}'

        local_data = data[data[filter_column] == local]
        core_data = data[data[filter_column] == core] if core is not None else pd.DataFrame()
        noncore_data = data[data[filter_column] == noncore] if noncore is not None else pd.DataFrame()

        # Add 'Comments' column to each DataFrame
        for df in [local_data, core_data, noncore_data]:
            if not df.empty:
                df['Comments'] = ''  # Initialize with empty strings or any default value

        processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_data.xlsx')
        with pd.ExcelWriter(processed_filepath) as writer:
            if not local_data.empty:
                local_data.to_excel(writer, sheet_name='Local', index=False)
            if not core_data.empty:
                core_data.to_excel(writer, sheet_name='Core', index=False)
            if not noncore_data.empty:
                noncore_data.to_excel(writer, sheet_name='NonCore', index=False)
            if rates_data is not None:
                rates_data.to_excel(writer, sheet_name=rates_last_sheet_name, index=False)

        wb = load_workbook(processed_filepath)

        def hide_columns(sheet):
            columns_to_hide = ['Year', 'Month', 'Day', 'COUNTRY', 'ROWNO', 'Start Date']
            for col_name in columns_to_hide:
                for cell in sheet[1]:  # Check the first row for column names
                    if cell.value == col_name:
                        col_letter = cell.column_letter
                        sheet.column_dimensions[col_letter].hidden = True
                        break

        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            hide_columns(sheet)

        wb.save(processed_filepath)

        return f'''
        <h3>Files Uploaded and Processed Successfully!</h3>
        <p>Local: {local}</p>
        <p>Core: {core if core is not None else 'N/A'}</p>
        <p>Non-Core: {noncore if noncore is not None else 'N/A'}</p>
        <p>Processed data saved in <a href="/download">processed_data.xlsx</a></p>
        '''

@app.route('/download')
def download_file():
    filepath = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_data.xlsx')
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
