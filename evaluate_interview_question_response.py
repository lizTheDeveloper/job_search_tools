import json
from ai_util import discerning_natural_language_prompt, clean_list, classifying_natural_language_prompt
import json
import os 
import time 

def get_question_rubrics():
    ## load the rubrics for each question
    with open("./question_rubrics.json") as f:
        question_rubrics = json.load(f)
        return question_rubrics

def save_question_rubrics(question_rubrics):
    print("saving question rubrics")
    
    ## save the rubrics for each question
    with open("./question_rubrics.json", "w") as f:
        json.dump(question_rubrics, f)

def get_rubric_for_question(question):
    ## given a question text, return the rubric
    question_rubrics = get_question_rubrics()
    for rubric in question_rubrics:
        if rubric["question"] == question:
            return rubric
    print("did not find a rubric for question ",question)
    return

def evaluate_candidate_response(question,response,criteria):
    print("evaluate_response got question",question)
    print("evaluate_response got response",response)
    print("evaluate_response got criteria",criteria)
    ## given a question, response, and criteria, return a score by asking GPT to rate it on a scale of 1-5 against the criteria
    ## make sure we have a response and criteria
    if not response:
        return
    if not criteria:
        return
    question_rubric = get_rubric_for_question(question)
    if not question_rubric:
        ## if we don't have a rubric for this question, create one
        question_rubric = {"question": question, "criteria": {}}
    ## loop over all the criteria in in the question_rubric['criteria'] and find any that are in the criteria list
    ## add them to a rubric_string
    scoring_rubric_str = ""
    for criterion in criteria:
        ## if the criteria is represented in the question_rubric, add it to the scoring rubric
        if criterion not in question_rubric['criteria']:
            print("creating criteria question")
            ## if the criteria isn't in the question_rubric, we need to create it
            question_rubric = create_criteria_question(criterion,question_rubric)
        scoring_rubric_str += f"{criterion}: {question_rubric['criteria'][criterion]['question']}\n"
        if len(question_rubric['criteria'][criterion]['examples'].keys()) == 0:
            ## if the criteria doesn't have examples, we need to create them
            print("creating criteria examples and rubric")
            question_rubric = create_criteria_rubric(criterion,question_rubric)
        for i in question_rubric['criteria'][criterion]['examples'].keys():
            print("adding example to scoring rubric ",i)
            example = question_rubric['criteria'][criterion]['examples'][i]
            scoring_rubric_str += f"Example of a score of {i}: {example}\n"
   
    ## save the question_rubric in question_rubrics.json by adding it to the list of question_rubrics, or replacing the existing one
    
    question_rubrics = get_question_rubrics()
    found = False
    for i in range(len(question_rubrics)):
        if question_rubrics[i]['question'] == question:
            question_rubrics[i] = question_rubric
            found = True
            break
    if not found:
        question_rubrics.append(question_rubric)
    save_question_rubrics(question_rubrics)


    ## get all the criteria for this question
    criteria_str = ", ".join(criteria)
    prompt = f"Question: {question}\n\nScoring Rubric: {scoring_rubric_str} Candidate Response: {response}\n\ Please score the candidate's response according to the following Criteria: {criteria_str}\n\nScore (1-5): {criteria[0]}: "
    response = f"{criteria[0]}:" + classifying_natural_language_prompt(prompt)
    print("evaluate_response got response",response)
    clean_list_response = clean_list(response)
    return clean_list_response

def suggest_improvements(question,response,criteria):
    ## make sure we have a response and criteria
    if not response:
        return
    if not criteria:
        return
    criteria_str = ", ".join(criteria)
    ## given a question, response, and criteria, ask GPT to revise the answer to improve it according to the criteria
    prompt = f"Question: {question}\n\nCandidate Response: {response}\n\nPlease revise the candidate's response to improve how the same story is communicated, by using the STAR (Situation, Task, Action, Result) technique, and writing it to maximize signaling to the following qualities the candidate will be judged on in the interview: {criteria_str}\n\nRevised Response: "
    response = discerning_natural_language_prompt(prompt)
    print("suggest_improvements got response",response)
    return response


def create_criteria_rubric(criteria,question):
    """ 
    Criteria: a dictionary with the following keys: {'criteria': 'criteria_text', 'question': 'criteria_question_text', 'examples': {}, 'rubric': ''}
    Question: a dictionary with the following keys: {'question': 'question_text', 'criteria': {}}
    """
    print("creating criteria rubric for ",criteria)
    criteria_question_text = question['criteria'].get(criteria,{}).get("question")
    question_text = question["question"]
    criteria_text = criteria
    criteria = question['criteria'].get(criteria,{})

    prompt_context=f"""Given the following behavioral interview question:
{question_text}
and the following criteria:
{criteria_text}
Asking yourself the following question:
{criteria_question_text}
"""
    example_text = ""
    for n in range(1,6):
        example_prompt = f"{prompt_context}\nGive an example of an answer that would demonstrate a rating of {n}:\n"
        example_response = discerning_natural_language_prompt(example_prompt)
        ## save to the object of examples, with n as the key and the example as the value
        criteria['examples'][n] = example_response
        example_text += f"{n}: {example_response}\n"
    
    ## create a rubric for the criteria
    rubric_prompt = f"{prompt_context}\nGiven these examples:\n {example_text}\n\n Provide a brief description for what evidence an interviewer is looking for as answers become more sophisticated in terms of {criteria['criteria']}?\n"
    rubric_response = discerning_natural_language_prompt(rubric_prompt)
    criteria['rubric'] = rubric_response

    ## log to rubric_data.jsonl
    with open('rubric_data.jsonl', 'a') as f:
        f.write(json.dumps(question) + "\n")

    return question

def create_criteria_question(criteria,question):
    print("creating criteria question for criteria ",criteria," and question ",question["question"])
    ## create a criteria question for a question
    prompt_context = f"""Given the following behavioral interview question:
{question['question']}
"""
    criteria_question_prompt = f"{prompt_context}\nWhat criteria would you use to evaluate the candidate's response to this question?\n"
    ## now loop over 5 other criteria and add them to the criteria_question_prompt with their question 
    added_prompt_count = 0
    for _c in question['criteria']:
        c = question['criteria'][_c]
        if added_prompt_count < 5:
            added_prompt_count += 1
            criteria_question_prompt += f"{c['criteria']}: {c['question']}\n"
        else:
            break
    
    criteria_question_prompt += f"{criteria}: "
    criteria_question_response = f"{criteria}: " + discerning_natural_language_prompt(criteria_question_prompt)
    ## we might get multiple criteria and questions back, so we need to split on the newlines
    criteria_list = criteria_question_response.split("\n")
    
    
    ## loop over the cleaned response and add it to the criteria for the question (provided it doesn't already exist)
    ## if it's the first one in this loop, we need to just add the question to the criteria that was passed in, then add that to the question_rubric
    for i in range(len(criteria_list)):
        print("criteria_list[i]",criteria_list[i])
        ## make sure there is a : in the line 
        if ":" not in criteria_list[i]:
            continue
        criteria = criteria_list[i].split(":")[0]
        criteria_question = criteria_list[i].split(":")[1]
        print("trying to add criteria:",criteria)
        print("with criteria question:",criteria_question)
        new_criteria = {}
        new_criteria['examples'] = {}
        new_criteria['rubric'] = ""
        if i==0:
            new_criteria['criteria'] = criteria
            new_criteria['question'] = criteria_question
            question['criteria'][criteria] = new_criteria
        else:
            if criteria_question not in question['criteria']:
                new_criteria['question'] = criteria_question
                new_criteria['criteria'] = criteria
                question['criteria'][new_criteria['criteria']] = new_criteria
            else:
                print("criteria question already exists")
            
            
    ## log to rubric_data.jsonl
    with open('rubric_data.jsonl', 'a') as f:
        f.write(json.dumps(question) + "\n")

    return question


## given a new question, query gpt to give the criteria by which the question can be evaluated
def get_criteria(question_text):

    prompt = f"""
    Given the following behavioral interview question:
    {question_text}
    What are 20 criteria an interviewer could give a 1-5 point score to that will evaluate the range of responses from candidates?

    1. Professionalism (1-5): How did the candidate handle the situation with respect and professionalism?\n"""
    response = "1. Professionalism (1-5): How did the candidate handle the situation with respect and professionalism?\n" + discerning_natural_language_prompt(prompt)
    return clean_list(response)



if __name__ == "__main__":
    """
    Test the functions
    question:  Describe a situation where you had to think quickly to solve a problem and the result of your solution.
    criteria:  ['Leadership', 'Communication', 'Problem Solving', 'Decision Making Skills', 'Interpersonal Skills']
    answer:   Once when I was running a project I encountered a problem and I had to think quickly to find a solution.
    """
    question = "Describe a situation where you had to think quickly to solve a problem and the result of your solution."
    criteria = ['Leadership', 'Communication', 'Problem Solving', 'Decision Making Skills', 'Interpersonal Skills']
    answer = "Once when I was running a project I encountered a problem and I had to think quickly to find a solution."

    ## test the evaluate_candidate_response function
    print("evaluate_candidate_response:",evaluate_candidate_response(question,answer,criteria))