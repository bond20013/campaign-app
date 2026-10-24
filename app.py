from flask import Flask, render_template, request, jsonify, session, redirect
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

app = Flask(__name__)
app.secret_key = "campaign-secret-2026"

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'service-account.json'
SPREADSHEET_ID = '1BVz1a2svo0WSzPqtdWzRPN55Z89xDZHtDUsqyiV8L2E'

def get_service():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def require_login():
    if 'user' not in session:
        return redirect('/')
    return None

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    userid = data.get('userid', '').strip()
    password = data.get('password', '').strip()
    service = get_service()
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='Users!A2:G').execute()
    for row in result.get('values', []):
        if len(row) >= 2 and row[0] == userid and row[1] == password:
            session['user'] = {'id': row[0], 'name': row[2] if len(row)>2 else userid, 'role': row[3] if len(row)>3 else 'Manager', 'head': row[4] if len(row)>4 else ''}
            return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid ID or Password'})

@app.route('/home')
def home():
    if require_login(): return require_login()
    return render_template('home.html', user=session['user'])

@app.route('/vehicle')
def vehicle():
    if require_login(): return require_login()
    return render_template('vehicle.html', user=session['user'])

@app.route('/food')
def food():
    if require_login(): return require_login()
    return render_template('food.html', user=session['user'])

@app.route('/publicity')
def publicity():
    if require_login(): return require_login()
    return render_template('publicity.html', user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/api/vehicles')
def api_vehicles():
    service = get_service()
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='Vehicles!A2:H').execute()
    return jsonify(result.get('values', []))

@app.route('/api/save-attendance', methods=['POST'])
def save_attendance():
    data = request.json
    service = get_service()
    row = [data.get('date'), data.get('vehicle'), data.get('attendance'), data.get('fuel', 0), data.get('other', 0), data.get('total', 0), session['user']['id']]
    service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range='Vehicle_Attendance!A2', valueInputOption='RAW', body={'values': [row]}).execute()
    return jsonify({'success': True})

@app.route('/api/save-food', methods=['POST'])
def save_food():
    data = request.json
    service = get_service()
    row = [data.get('date'), data.get('chef'), data.get('attendance'), data.get('chefRate', 0), data.get('team', 0), data.get('teamRate', 0), data.get('cylinders', 0), data.get('cylRate', 0), data.get('raw', 0), data.get('packaging', 0), data.get('total', 0), session['user']['id']]
    service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range='Food!A2', valueInputOption='RAW', body={'values': [row]}).execute()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/office')
def office():
    if require_login(): return require_login()
    return render_template('office.html', user=session['user'])

@app.route('/volunteers')
def volunteers():
    if require_login(): return require_login()
    return render_template('volunteers.html', user=session['user'])

@app.route('/social')
def social():
    if require_login(): return require_login()
    return render_template('social.html', user=session['user'])

@app.route('/misc')
def misc():
    if require_login(): return require_login()
    return render_template('misc.html', user=session['user'])

@app.route('/advance')
def advance():
    if require_login(): return require_login()
    if session['user']['role'] not in ['Administrator', 'Senior Manager']:
        return "Access denied", 403
    return render_template('advance.html', user=session['user'])

@app.route('/api/save-office', methods=['POST'])
def save_office():
    data = request.json
    service = get_service()
    row = [data.get('date'), data.get('item'), data.get('qty',1), data.get('amount',0), data.get('vendor',''), data.get('remarks',''), session['user']['id']]
    service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range='Office!A2', valueInputOption='RAW', body={'values':[row]}).execute()
    return jsonify({'success': True})

@app.route('/api/save-volunteer', methods=['POST'])
def save_volunteer():
    data = request.json
    service = get_service()
    row = [data.get('date'), data.get('name'), data.get('purpose'), data.get('amount',0), session['user']['id']]
    service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range='Volunteers!A2', valueInputOption='RAW', body={'values':[row]}).execute()
    return jsonify({'success': True})

@app.route('/api/save-social', methods=['POST'])
def save_social():
    data = request.json
    service = get_service()
    row = [data.get('date'), data.get('platform'), data.get('desc'), data.get('vendor',''), data.get('amount',0), session['user']['id']]
    service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range='Social_Media!A2', valueInputOption='RAW', body={'values':[row]}).execute()
    return jsonify({'success': True})

@app.route('/api/save-misc', methods=['POST'])
def save_misc():
    data = request.json
    service = get_service()
    row = [data.get('date'), data.get('head','Miscellaneous'), data.get('desc'), data.get('amount',0), session['user']['id']]
    service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range='Miscellaneous!A2', valueInputOption='RAW', body={'values':[row]}).execute()
    return jsonify({'success': True})

@app.route('/api/save-advance', methods=['POST'])
def save_advance():
    data = request.json
    service = get_service()
    row = [data.get('date'), data.get('manager'), data.get('amount',0), data.get('remarks',''), session['user']['id']]
    service.spreadsheets().values().append(spreadsheetId=SPREADSHEET_ID, range='Advances!A2', valueInputOption='RAW', body={'values':[row]}).execute()
    return jsonify({'success': True})

@app.route('/my-entries')
def my_entries():
    if require_login(): return require_login()
    return render_template('my_entries.html', user=session['user'])

@app.route('/voters')
def voters():
    if require_login(): return require_login()
    if session['user']['role'] not in ['Administrator', 'Senior Manager']:
        return "Access denied", 403
    return render_template('voters.html', user=session['user'])

@app.route('/reports')
def reports():
    if require_login(): return require_login()
    return render_template('reports.html', user=session['user'])

@app.route('/api/balance')
def api_balance():
    if 'user' not in session:
        return jsonify({'balance': 0})
    uid = session['user']['id']
    service = get_service()
    
    # Advances received
    adv = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='Advances!A2:E').execute().get('values', [])
    advance_total = sum(float(r[2]) for r in adv if len(r) > 2 and r[1] == uid)
    
    # Expenses by this user (sum across sheets)
    expense_sheets = ['Vehicle_Attendance', 'Food', 'Publicity', 'Office', 'Volunteers', 'Social_Media', 'Miscellaneous']
    spent = 0
    for sh in expense_sheets:
        try:
            rows = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=f'{sh}!A2:Z').execute().get('values', [])
            for r in rows:
                if r and r[-1] == uid:  # last column is EnteredBy
                    # try to find a numeric total/amount
                    for cell in reversed(r[:-1]):
                        try:
                            spent += float(cell)
                            break
                        except:
                            continue
        except:
            pass
    return jsonify({'balance': advance_total - spent, 'advance': advance_total, 'spent': spent})

@app.route('/api/my-entries')
def api_my_entries():
    uid = session['user']['id']
    service = get_service()
    entries = []
    sheets = {
        'Vehicle_Attendance': 'Vehicle',
        'Food': 'Food',
        'Publicity': 'Publicity',
        'Office': 'Office',
        'Volunteers': 'Volunteers',
        'Social_Media': 'Social Media',
        'Miscellaneous': 'Miscellaneous'
    }
    for sh, label in sheets.items():
        try:
            rows = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=f'{sh}!A2:Z').execute().get('values', [])
            for r in rows:
                if r and r[-1] == uid:
                    entries.append({'sheet': label, 'data': r})
        except:
            pass
    return jsonify(entries)

@app.route('/api/voters')
def api_voters():
    service = get_service()
    rows = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range='Voter_List!A2:G').execute().get('values', [])
    return jsonify(rows)

@app.route('/api/edit-entry', methods=['POST'])
def edit_entry():
    if session['user']['role'] not in ['Administrator', 'Senior Manager']:
        return jsonify({'success': False, 'message': 'No permission'}), 403
    # For simplicity, editing is done directly in Google Sheet for now
    # Full in-app edit can be added later
    return jsonify({'success': True, 'message': 'Edit via Google Sheet for now'})
