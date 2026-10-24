from flask import Flask, render_template, request, jsonify, session, redirect
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

app = Flask(__name__)
app.secret_key = "campaign-secret-2026"

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1BVz1a2svo0WSzPqtdWzRPN55Z89xDZHtDUsqyiV8L2E'

def get_service():
    creds = service_account.Credentials.from_service_account_file('service-account.json', scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    try:
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
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/')
    return render_template('home.html', user=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
