from flask import Blueprint, redirect, request, session, url_for
import os
import pickle
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request

auth_bp = Blueprint('auth', __name__)

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = 'securevision-oauth-credentials.json'
TOKEN_FILE = 'user_token.pickle'

@auth_bp.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )
    flow.redirect_uri = url_for('auth.oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    session['state'] = state
    return redirect(authorization_url)

@auth_bp.route('/oauth2callback')
def oauth2callback():
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = url_for('auth.oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials

    with open(TOKEN_FILE, 'wb') as token:
        pickle.dump(creds, token)

    return '✅ Authorization complete. You can close this window.'
