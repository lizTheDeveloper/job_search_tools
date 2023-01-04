from cover_letter import get_cover_letter

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets' , 'https://www.googleapis.com/auth/documents']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'YOUR_ID_HERE'
RANGE_NAME = 'Review Queue!A3:Z' ## this is the range of the spreadsheet you want to read from, make sure to include the sheet name


def main():
    pending_applications = 0
    
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        ## now get the resume from resume.txt 
        with open('resume.txt', 'r') as resume_file:
            resume = resume_file.read()
    
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        titles = values[0]
        n = 0

        
        for row in values[1:]:
            n += 1
            job = {}
            for i in range(len(row)):
                job[titles[i]] = row[i]
            
            if job.get('Cover Letter') != '' and job.get('Liz wants to Apply?') == 'Yes':
                pending_applications += 1
                continue
                
            ## make sure we have all the data we need
            if job.get('Company', False) and job.get('Job Title', False) and job.get('Job Description', False) and job.get('Qualifications', False):
                ## make sure the above fields aren't empty either
                if job['Company'] == '' or job['Job Title'] == '' or job['Job Description'] == '' or job['Qualifications'] == '':
                    continue
                ## also make sure we don't already have a cover letter for this job
                if job.get('Cover Letter') != '':
                    continue
                print(job)
                cover_letter = get_cover_letter(resume, job['Company'], job['Job Title'], job['Job Description'], job['Qualifications'])
                print(cover_letter)
            
        

        
                title = job.get('Company', False) + ' Cover Letter'
                body = {
                    'title': title,
                }
                docservice = build('docs', 'v1', credentials=creds)
                doc = docservice.documents().create(body=body).execute()
            
                print('Created document with title: {0}'.format(doc.get('title')))

                ## now create a request to update the document with the cover letter
                requests = [
                    {
                        'insertText': {
                            'location': {
                                'index': 1,
                            },
                            'text': cover_letter,
                        }
                    },
                ]
                docservice.documents().batchUpdate(documentId=doc.get('documentId'), body={'requests': requests}).execute()

                url = f"https://docs.google.com/document/d/{doc.get('documentId')}/edit"
                print(url)
                range_ = f"Review Queue!K{n}:K{n}"
                ## now update the spreadsheet with the link to the cover letter
                request = service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range_, valueInputOption='RAW', body={"values": [[url]]})
                response = request.execute()

    except HttpError as err:
        print(err)

    print(f"Pending Applications: {pending_applications}")


if __name__ == '__main__':
    main()