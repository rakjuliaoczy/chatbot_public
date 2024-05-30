import random
import chainlit as cl
import asyncio
import pandas as pd
from gensim.models import Word2Vec
import gensim
from nltk.tokenize import sent_tokenize, word_tokenize
import warnings
warnings.filterwarnings(action='ignore')
import numpy as np
from chainlit.context import init_http_context
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import Request
from fastapi.responses import HTMLResponse
from chainlit.server import app
from chainlit.context import init_ws_context
from chainlit.session import WebsocketSession
from fastapi import FastAPI
import requests
from pydantic import BaseModel
import vector_similarities

app = FastAPI()

# Allow your domain
# origins = [
#     "http://your-frontend-domain.com",
#     # Add other domains if necessary
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

class RuleBasedChatBot:
    def __init__(self):
        self.conversation_state = "occasion"
        self.collected_data = {}

        reactions_occ = ["Sounds fun!", "Sounds nice.", "Cool.", "Exciting.", "Exciting!", "Great!", "Nice!", "Cool!", "Sounds fun."]
        reactions_loc = ["Okay!", "Cool.", "Exciting.", "Exciting!", "Great!", "Nice!", "Nice.", "Cool!", "Okay.", "Noted!"]
        occasions = ["Could you share the location?", "Could you provide the location?", "Can you share the location with me?", "I'm interested in knowing the location. Could you share it?", "I'd appreciate it if you could tell me the location."]
        locations = ["Are you looking for a DJ, band, ensemble, or solo artist?","Are you in search of a DJ, band, ensemble, or solo aritst?","Are you seeking a DJ, band, ensemble, or solo artist?"]
        reactions_form_gen = ["Interesting choice!", "Interesting choice.", "Sounds fun!", "Sounds nice.", "Cool.", "Exciting.", "Exciting!", "Great!", "Nice!", "Nice.", "Cool!", "Sounds fun."]
        formations = ["Which music genre are you interested in?"]
        finales_gen = ["And my last question is", "And my final question is", "And finally,"]
        genres = ["how much would you like to pay?", "what is your budget?","what is the budget you have in mind?"]
        reactions_budget = ["Noted.", "Sure thing!", "Sure thing.", "Okay.", "Noted!"]
        budgets = ["I'll show you some artists that fit your criteria.", "I'll show you some artists that meet your criteria.", "I'll show you some artists that match your preferences.", "I'll show you some artists that might interest you." "I'll show you some artists that might catch your interest."]

        self.reaction_occ = random.choice(reactions_occ)
        self.reaction_loc = random.choice(reactions_loc)
        self.reaction_form = random.choice(reactions_form_gen)
        self.reaction_gen = random.choice(reactions_form_gen)
        self.reaction_budget = random.choice(reactions_budget)

        self.occasion = random.choice(occasions)
        self.location = random.choice(locations)
        self.formation = random.choice(formations)
        self.genre = random.choice(genres)
        self.finale_gen = random.choice(finales_gen)
        self.budget = random.choice(budgets)

    def get_response(self, user_input):
        responses = {
            "occasion": f"{self.reaction_occ} {self.occasion}",
            "location": f"{self.reaction_loc} {self.location}",
            "formation": f"{self.reaction_form} {self.formation}",
            "genre": f"{self.reaction_gen} {self.finale_gen} {self.genre}",
            "budget": f"{self.reaction_budget} {self.budget}"
        }

        response = responses[self.conversation_state]
        self.collected_data[self.conversation_state] = user_input
        self.conversation_state = self.next_conversation_state()
        return response

    def next_conversation_state(self):
        states = ["occasion", "location", "formation", "genre", "budget", "last"]
        current_index = states.index(self.conversation_state)
        return states[min(current_index + 1, len(states) - 1)]

bot = RuleBasedChatBot()

@cl.author_rename
def rename(orig_author: str):
    rename_dict = {"Chatbot": "Snuppy"}
    return rename_dict.get(orig_author)


@cl.on_chat_start
async def on_chat_start():
    # print("Session id:", cl.user_session.get("id"))
    # print("Session id:", session_id)
    #ws_session = WebsocketSession.get_by_id(session_id=session_id)
    await cl.Avatar(
        name="Snuppy",
        url="https://e7.pngegg.com/pngimages/96/827/png-clipart-club-penguin-clothing-avatar-penguin-blue-animals-thumbnail.png",
    ).send()
    await cl.Avatar(
        name="Human",
        url="https://duoplanet.com/wp-content/uploads/2023/05/duolingo-avatar-4.png",
    ).send()

    msg = cl.Message(content="Starting the bot...")
    await msg.send()

    greetings = ["Hi", "Hello", "Hey", "Hi there", "Hey there", "Hello there"]
    intros = ["I'm Snuppy, your personal assistant", "I'm Snuppy, here to assist you", "I'm Snuppy, at your service", "I'm Snuppy, excited to meet you"]
    help_statements = ["I hope I can help you find the best artist", "I'm here to assist you in finding the perfect artist", "I'm here to help you in finding the best artist", "Please let me know what you are looking for and I hope I can help you"]
    occasion_question = "What is the occasion you're searching for an artist for?"
    emojis = ["🎷", "🥁", "🎸"]

    greeting = random.choice(greetings)
    intro = random.choice(intros)
    help_statement = random.choice(help_statements)
    emoji = random.choice(emojis)

    msg_content = f"{greeting}! {emoji} {intro}. {help_statement}. {occasion_question}"
    msg.content = msg_content
    #print("Session id:", cl.user_session.get("id"))
    await msg.update()
    
# class Message(BaseModel):
#     content: str

@app.get("/")
async def start(request: Request):
    init_http_context()
    # This will trigger the on_chat_start decorator
    return HTMLResponse("Chat started. Check the WebSocket for messages.")


user_inputs = []

# @app.post("/chatbot")
# async def chatbot_endpoint(user_input: dict):
#     # Your chatbot processing logic here
#     return {"message": "Response from chatbot"}

@app.post("/chatbot")#main/{session_id}")
@cl.on_message
async def main(message):#, session_id: str):
    #ws_session = WebsocketSession.get_by_id(session_id=session_id)
    #init_ws_context(ws_session)
    global user_input
    user_input = message.content
    user_inputs.append(user_input)
    # print('user input:', user_input)

    # Check if the user's response is to the last state
    if bot.conversation_state == "last":
        if user_input.lower() in ["ok", "okay"]:
            responses_last = ["Just give me a few seconds.", "Bear with me for just a moment.", "Stay with me for just a few seconds."]
            response = random.choice(responses_last)
        elif any(word in user_input.lower() for word in ["thank", "thanks", "thx"]):
            responses_last = ["No problem. Just give me a few seconds.", "No worries. Just give me a few seconds.", "No problem. Bear with me for just a moment.", "No worries. Bear with me for just a moment."]
            response = random.choice(responses_last)
        else:
            responses_last = ["Just give me a few seconds.", "Bear with me for just a moment.", "Stay with me for just a few seconds."]
            response = random.choice(responses_last)
    else:
        # Check if the user input is "funeral"
        if user_input.lower() == "funeral" or user_input.lower() == "cremation":
            # If so, update the conversation state and respond accordingly
            bot.conversation_state = "location"
            response = "I'm sorry to hear that. Could you share the location with me?"
        else:
            # If not, proceed with the regular response
            response = bot.get_response(user_input)

    if len(user_inputs) == 5:
        print(user_inputs)
        user_options = vector_similarities.all_options(user_inputs)
        print(user_options)

    await asyncio.sleep(1.3)
    await cl.Message(content=response).send()



