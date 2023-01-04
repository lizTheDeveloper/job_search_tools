from ai_util import discerning_natural_language_prompt
def get_cover_letter(resume, company, job_title, job_description, job_qualifications):

    prompt = f"Resume: {resume}\n \n Job Title: {job_title} \n\n {job_qualifications} \n\n Job Description: {job_description} \n\n Write a professional, engaging cover letter for this person to apply for the job title of {job_title} at {company}.\n\n"
        
    response_text = discerning_natural_language_prompt(prompt)
    return response_text