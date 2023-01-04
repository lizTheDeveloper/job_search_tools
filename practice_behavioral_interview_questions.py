from ai_util import discerning_natural_language_prompt, clean_list
import json

## given a job descriptioin, return the top 5 qualities that are most likely to be evaluated for in the behavioral questions phase of the job interview for this job

def get_practice_qualities_from_job_description(job_description):
    ## first, get the top 5 qualities that are most likely to be evaluated for in the behavioral questions phase of the job interview for this job
    prompt = f"""We are searching job descriptions for what qualities they might be evaluating for in a job interview.
Here are the qualities: 
Professionalism, Honesty, Initiative, Communication, Respect, Patience, Understanding, Conflict Resolution, Tact, Proactivity, Problem Solving, Listening Skills, Self-Awareness, Adaptability, Calmness, Negotiation, Creative Thinking, Perspective, Interpersonal Skills, Follow-Through, Resourcefulness, Creativity, Planning, Leadership, Problem-Solving Capability, Focus, Cooperation, Decision-Making Skills, Research and Analysis, Problem Recognition, Attention to detail, Time Management, Stress Management, Results-Oriented, Flexible Thinking, Problem Solving Skills, Empathy, Speed, Teamwork, Multitasking, Knowledge/Expertise, Accuracy, Analytical Thinking, Attention to Detail, Resource Management, Post-Sale Evaluation, Effective Communication, Goal-setting, Delegation, Encouragement, Flexibility, Problem-solving, Critical Thinking, Collaboration, Relationship Building, Innovative Thinking, Decision Making, Prioritization, Goal Orientation, Team Building, Openness, Body Language, Listening, Storytelling, Intuition, Use of Language, Persuading, Positivity, Motivation, Emotional Intelligence, Presentation Skills, Clarity, Results, Innovation, Feedback, Decision-Making, Organization, Perseverance, Problem-Solving, Risk Assessment, Fact-Finding, Thoroughness, Goal-Oriented, Collaborative, Stakeholder Engagement, Goal Setting, Risk Management, Follow Up, Accountability, Trustworthiness, Project Leadership, Strategic Thinking, Resource Allocation, Decision-making, Goal Achievement, Team Management, Process Improvement, Proactive/Reactive, Planning/Organization, Result Orientation

Here is the job description:

{job_description}

Which are the top 5 qualities that are most likely to be evaluated for in the behavioral questions phase of the job interview for this job?

1.
"""
    response_text = discerning_natural_language_prompt(prompt)
    qualities = clean_list(response_text)
    if "Professionalism" in qualities:
        qualities.remove("Professionalism") ## will suggest all questions, so remove this
    return qualities

## read question_rubrics.json 
def get_question_rubrics():
    with open("question_rubrics.json") as f:
        question_rubrics = json.load(f)
    return question_rubrics

## read practice_questions.json
def get_practice_questions():
    with open("practice_questions.json") as f:
        practice_questions = json.load(f)
    return practice_questions

## given a list of practice qualities, return a list of questions that are likely to be asked in a behavioral interview for this job
def get_practice_questions_from_qualities(qualities):
    practice_questions = get_practice_questions()
    questions = []
    for quality in qualities:
        ## loop through all questions and find the ones that match the quality from the criteria field
        for question in practice_questions:
            if quality in question["criteria"]:
                questions.append(question)
    return questions

## wrapper function for the above
def get_practice_questions_from_job_description(job_description):
    qualities = get_practice_qualities_from_job_description(job_description)
    questions = get_practice_questions_from_qualities(qualities)
    return qualities, questions

if __name__ == "__main__":
    jd = """
    What You'll Do
    Own Company's payment system and platform APIs - helping our customers process payments
    Work with your team, Product, and Design to build new customer-facing product features and improve upon existing ones
    Empower the Engineering Team to achieve a high level of technical productivity and quality
    Grow, develop, and guide the engineers on the team to help them advance in their careers and achieve their professional goals
    Jump in and contribute to the codebase as needed
    Hire and retain top engineering talentDevelop engineers on the team, helping them advance in their careers
    What We're Looking For
    A product focused mindset - a passion to deliver great products to the businesses and their end-consumers
    Ability to work cross-functionally and collaborate with other departments to achieve a common goal
    You thrive in a fast-paced and sometimes ambiguous environmentYou are comfortable with high levels of autonomy and responsibility
    Managed engineering teams with a proven track record of success
    Solutions oriented - you are energized by finding solutions to problems
    2+ years of engineering management experience
    """
    qualities = get_practice_qualities_from_job_description(jd)
    print(qualities)

    questions = get_practice_questions_from_qualities(qualities)
    for question in questions:
        ## print the question from the question field, then show qualities (key and value) from the criteria field that are in the qualities list
        print(question["question"])
        print("Key Criteria: ")
        for key, value in question["criteria"].items():
            if key in qualities:
                print("\t\t",key, value)
        print("\n\n\n")


