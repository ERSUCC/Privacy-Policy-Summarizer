#!/usr/bin/env python

# Privacy Policy Condenser: A Browser Extension
# Authors: Charles Cheng, Jadon Lau, Isaac Brown, Tergel Myanganbayar

from ai21 import AI21Client
from json import dumps
from re import sub
from struct import pack, unpack
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sys import stdin, stdout

##### Questions and focus points #####

questions = [
    "What type of information does the company collect about the user?",
    "How does the company use the users' information?",
    "Who does the company share the users' information with?",
    "What information is collected by or shared with third-parties?",
    "How long does the company store the users' information and what security measures are taken to safeguard data?",
    "How is the users' information being used for advertisement?",
    "Does the company use cookies and, if so, why?",
    "How can the user opt out of certain data collection or usage?",
    "How can the user access the information collected about them or modify that information?",
    "How does the user contact the company if they have questions or concerns?"
]

GDPR_checklist = {
    "Lawful basis and transparency": [
        "Does the company list the information they collect and how has access to it?",
        "Does the company have a justification for their data processing and usage?"
    ],
    "Data security": [
        "Does the company take data protection into account?",
        "Does the company encrypt, pseudonymize, or anonymize personal data?"
    ],
    "Accountability and goverance": [
        "Does the company list third-parties with whom users' information is shared, if applicable?",
        "Does the company provide a justification for sharing users' information with third-parties, if applicable?"
    ],
    "Privacy rights": [
        "Can the user request and receive all the information collected about them?",
        "Can the user update or correct their personal information?",
        "Can the user request to have their personal information deleted?",
        "Can the user opt out of the company's data collection and processing?",
        "Does the company aim to protect the users' privacy rights?"
    ]
}

##### AI helper functions #####

client = AI21Client(api_key = "9fxQ7qXHEGh6RZxadsskKD8l5wBefKnB")

def ask(context, question):
    answer = client.answer.create(context, question).answer

    if answer is None:
        return "Sorry, we could not find any information about this topic in the privacy policy."

    return answer

def score(context, question):
    answer = client.answer.create(context, question).answer

    if answer is None:
        return 0
    
    words = sub(r"[^\w\s.-]", "", answer).lower().split()

    return "yes" in words or "no" not in words

def condense(source):
    return client.summarize.create(source).summary

def tag(text, tag):
    return "<" + tag + ">" + text + "</" + tag + ">"

##### Summary #####

def summarize_policy(text):
    summarizer = LsaSummarizer()

    summary = tag("Warning: The following summary and evaluation was created with a large language model (LLM), using the contents of the current website. It may present incomplete or false information due to the inaccuracies of LLMs. The final score tests if the policy is compliant with the General Data Protection Regulation (GDPR), which does not necessarily reflect how good the company is at protecting users' privacy.", "p")

    i = 0
    its = float(len(questions) + sum(map(lambda x: len(x), GDPR_checklist.values())))

    for question in questions: 
        answer = ask(text, question)

        if len(answer) > 300:
            parser = PlaintextParser.from_string(answer, Tokenizer("english"))
            output = summarizer(parser.document, sentences_count = 4) # can change length of summary

            answer = " ".join([sentence._text for sentence in output])

        summary += tag(tag(question, "b"), "p") + tag(answer, "p")

        i += 1

        send(str(i / its))
        
    summary += tag("Privacy Score", "b")
    
    checklist_len = 0
    total_score = 0

    for bullet in GDPR_checklist:
        section_score = 0
        num_questions = len(GDPR_checklist[bullet])

        for question in GDPR_checklist[bullet]:
            section_score += score(text, question)

            i += 1

            send(str(i / its))

        checklist_len += num_questions
        total_score += section_score

        summary += tag(bullet + ": " + str(section_score) + "/" + str(num_questions), "p")

    summary += tag(tag("Total score: ", "b") + str(total_score) + "/" + str(checklist_len), "p")

    return summary

##### Extension communication #####

def receive():
    length = stdin.buffer.read(4)

    return stdin.buffer.read(unpack("i", length)[0]).decode("utf-8")

def send(message):
    message_bytes = dumps(message).encode("utf-8")

    stdout.buffer.write(pack("i", len(message_bytes)))
    stdout.buffer.write(message_bytes)

    stdout.buffer.flush()

send(summarize_policy(receive()))

while True:
    continue
