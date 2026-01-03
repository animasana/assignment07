import json
from openai import api_key
from regex import D
import streamlit as st
from langchain.chat_models.base import init_chat_model
from langchain_core.prompts.prompt import PromptTemplate


st.title("Assignment07")


function = {
    "name": "create_quiz",
    "description": "function that takes a list of questions and answers and returns a quiz",
    "parameters": {
        "type": "object",
        "properties": {
            "questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                        },
                        "answers": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "answer": {
                                        "type": "string",
                                    },
                                    "correct": {
                                        "type": "boolean",
                                    },
                                },
                                "required": ["answer", "correct"],
                            },
                        },
                    },
                    "required": ["question", "answers"],
                },
            }
        },
        "required": ["questions"],
    },
}

with st.sidebar:
    OPENAI_API_KEY = st.text_input(label="OPENAI API KEY")
    difficulty = st.radio("Degree of Difficulty", ["Easy", "Hard"], index=0)    
    topic = st.text_input("Input a topic about quiz you want to create")
    st.write("https://github.com/animasana/assignment07/blob/main/app.py")


llm = init_chat_model(
    model=("openai:gpt-5-nano"),
    api_key=OPENAI_API_KEY,
).bind(
    function_call={
        "name": "create_quiz"
    }, 
    functions=[
        function
    ],
)

@st.cache_data(show_spinner="Making quiz...")
def run_quiz_chain(topic: str, difficulty: str):
    prompt = PromptTemplate.from_template(
        """
        Make five {difficulty} level quizz questions about {topic}.
        Ensure the answer choices are in a random order.
        """
    )
    
    chain = prompt | llm
    return chain.invoke(
        {
            "topic": topic,
            "difficulty": difficulty.upper()
        }
    )


if not (topic and OPENAI_API_KEY and difficulty):
    st.markdown(
        """
        Welcome to Assignment07!!!        
        I will make a quiz from Wikipedia articles or files you upload         
        to test your knowledge and help you study.
        
        Get started by uploading a file or searching on Wikipedia in the sidbar.
        """
    )
else:
    response = run_quiz_chain(topic=topic, difficulty=difficulty)
    response = json.loads(response.additional_kwargs["function_call"]["arguments"])

    with st.form("questions_form", clear_on_submit=True, enter_to_submit=False):
        correct_answers = 0
        for i, question in enumerate(response["questions"]):
            st.write(question["question"])            
            value = st.radio(
                "Select an option.", 
                [answer["answer"] for answer in question["answers"]], 
                index=None,                
            )

            if value is not None:
                if {"answer": value, "correct": True} in question["answers"]:
                    st.success("Correct!")
                    correct_answers += 1
                elif value is not None:
                    st.error("Wrong")        
        
        is_perfect = len(response["questions"]) == correct_answers

        submitted = st.form_submit_button("Submit", disabled=is_perfect)        
        
        if submitted:
            if is_perfect:            
                st.balloons()            
                st.success("Perfect score!")                
            else:            
                st.error("Not perfect, Try again?")                
                if st.form_submit_button("Retry"):                    
                    st.rerun()
                    
        
    
    

    
    

    
        


    
    
    
    

    
    
        