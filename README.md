## Job Search Toolchain

This is a collection of tools to help you with your job search. It is a work in progress, and I will be adding more tools as I make them. If you don't want to bother with this, they're in use at hackingcapitalism.dev, and you can just use that. If not, read on.

### How to Use
They're just scripts. You'll need to modify them to work for you.
I followed this [Python Quickstart](https://developers.google.com/sheets/api/quickstart/python) to get the requisite permissions working for the Google Sheets API. You'll need to do that too. It's looking for a file called `creds.json`. You'll need to make that file and put it in the same directory as the scripts.

I use the `gsheets_toolchain.py` script to generate cover letters, then modify them to make sure they're true. They do a great job talking about the job itself, but sometimes phrase your experience weirdly (eg, it might say "with my 8+ years of experience" when my resume states I have 20, because the job description wants 8+ years of experience). 
I also use it to generate a list of qualities they'll want me to demonstrate from the job description, this helps me rehearse for interviews.


### Tools

#### Resume
Job Duties Suggestor - suggests job duties based on job titles, for resume rewording 


#### Cover Letter
Cover Letter Generator - generates a cover letter based on job title and company name given your resume
Google Sheets Toolchain - given a google sheets link, generates cover letters based on a csv dump of job descriptions, qualifications, job titles, and your resume, then adds a google docs link to the sheet

#### Interview
Interview Prep - generates a list of questions to ask based on job title and company name given your resume
Qualities to Practice - generates a list of qualities to practice based on the job description 
Evaluate Answer - evaluates your answer to a question based on given criteria (provided by qualities to practice, usually)