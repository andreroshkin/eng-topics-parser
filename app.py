# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from dataclasses import dataclass
import requests
import re
import json
from dataclasses_serialization.json import JSONSerializer

@dataclass
class Question:
    text: str

@dataclass
class Topic:
    title: str
    url: str
    questions: list[Question]

def get_page(url: str):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    page = None
    try:
        page = requests.get(url, headers=headers)
    except:
        print("Connection error")
    return page

def parse_topics(html: str):
    topics = []
    soup = BeautifulSoup(html, "html.parser")
    links = soup.findAll('a', href=True)
    if links is not None:
        for link in links:
            topic_title = link.string 
            topic_url = "https://esldiscussions.com/" + link['href']
            topic_questions = []
            topic = Topic(topic_title, topic_url, topic_questions)
            topics.append(topic)
    return topics

def get_topics_questions(topics: list[Topic]):
    for topic in topics:
        questions = []
        topic_page = get_page(topic.url)
        if (topic_page): 
            print(topic.url)
            topic_page_html = topic_page.text
            soup = BeautifulSoup(topic_page_html, "html.parser")
            raw_questions = soup.findAll('td', width="93%")
            if raw_questions is not None:
                for raw_question in raw_questions:
                    question_text = raw_question.string
                    if question_text is not None:
                        filtered_question_text = get_filtered_text(question_text)
                        question = Question(filtered_question_text)
                        questions.append(question)
                topic.questions = questions
    
    return topics

def get_filtered_text(raw_text): 
    return re.sub(' +', ' ', raw_text)

def save_topics(topics: list[Topic]):
    serialized_topics = JSONSerializer.serialize(topics)
    with open(f'topics.json', 'w', encoding='utf8') as outfile:
        outfile.write(json.dumps(serialized_topics, indent=4, ensure_ascii=False))

def get_not_empty_topic(topics):
    non_empty_topics = []
    for topic in topics:
        if topic.questions:
            non_empty_topics.append(topic)
    return non_empty_topics
        
def main():
    main_page_url = 'https://esldiscussions.com'
    main_page = get_page(main_page_url)

    topics = parse_topics(main_page.text)
    topics = get_topics_questions(topics)
    non_empty_topics = get_not_empty_topic(topics)    
    save_topics(non_empty_topics)

main()