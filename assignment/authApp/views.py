from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import json


import google.oauth2.credentials
import google_auth_oauthlib.flow
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import datetime
import os

# Use the client_secret.json file to identify the application requesting
# authorization. The client ID (from that file) and access scopes are required.

SCOPES = ['https://www.googleapis.com/auth/calendar.events.readonly']


def index(request):
    return HttpResponseRedirect('http://localhost:8000/rest/v1/calendar/init/')


def GoogleCalendarInitView(request):
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES)

    flow.redirect_uri = 'http://localhost:8000/rest/v1/calendar/redirect/'

    authorization_url, state = flow.authorization_url(
        access_type='offline',
    )

    return HttpResponseRedirect(authorization_url)


def GoogleCalendarRedirectView(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES)

    flow.redirect_uri = 'http://localhost:8000/rest/v1/calendar/redirect/'

    authorization_response = request.build_absolute_uri().replace("http", "https")
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)

    # make an html page with the events

    string  = "<html><body><h1>Events</h1><ul>"
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        string += "<li>" + start + " " + event['summary'] + "</li>"
    string += "</ul></body></html>"
    return HttpResponse(string)
