from email.mime import multipart
from http.client import HTTPException
from lib2to3.pgen2 import token
from logging import raiseExceptions
from fastapi import Body,requests
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI
from fastapi import Form
import json
from fastapi import *



app=FastAPI()
oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/Hello")
def home():
    return "Welcome to the international Bank"

@app.post("/token")
async def Login(form_data:OAuth2PasswordRequestForm=Depends()):
    print(form_data)
    with open ("userdb.json","r") as json_file:
        json_data=json.load(json_file)
        if json_data:
            password=json_data.get(form_data.username)
            if not password:
                print("you are not registered,pls registered your self/wrong username or password")
                raise HTTPException(status_code=403,detail="incorrect creditials")
            
    return {"access_token":form_data.username,"token_type":"bearer"}
    

@app.get("/spend/History")
def spend_history(token:str=Depends(oauth_scheme)):
    print(token)
    print("SPEND HISTORY")
    with open ("spendhist.json","r") as spendhist:
        spendhist_data=json.load(spendhist)
        if not spendhist_data.get(token):
            print("you are not registered,pls registered your self")
            raise HTTPException(status_code=400,detail="incorrect creditials")
        return {
            "username":token,
            "spendhist":spendhist_data[token]
            }


@app.get("/credit/History")
def credit_history(token:str=Depends(oauth_scheme)):
    print(token)
    print("Credit HISTORY")
    with open ("credithist.json","r") as credithist:
        credithist_data=json.load(credithist)
        if not credithist_data.get(token):
            print("you are not registered,pls registered your self")
            raise HTTPException(status_code=400,detail="incorrect creditials")
    return {
        "username":token,
        "spendhist":credithist_data[token]
        }


@app.post("/transfer/money")
def transfer_money(token:str=Depends(oauth_scheme),destination_user:str=Body(...),
                                    amount_to_transfer:float=Body(...)):
    print(token)
    print(amount_to_transfer)
    print(destination_user)
    userbalance_data=None
    with open ("userbalance.json","r") as userbalance_file:
        userbalance_data=json.load(userbalance_file)
        curr_user_bal=userbalance_data.get(token)['curr_balance']
        print(f" current user balance is {curr_user_bal}")
        dest_user=userbalance_data.get(destination_user)
        if not dest_user:
            raise HTTPException(status_code=400,detail="user not available")
        dest_user_bal=dest_user['curr_balance']
        print(f"destination user balance:{dest_user_bal}")
        if curr_user_bal-amount_to_transfer<0:
            raise HTTPException(status_code=400,detail="not able to tranfer")
    userbalance_data[token]['curr_balance']-=amount_to_transfer
    print(userbalance_data)
    userbalance_data[destination_user]['curr_balance']+=amount_to_transfer
    with open("userbalance.json","w") as userbal_write:
        json.dump(userbalance_data,userbal_write)
        return {
            "username":token,
            "message":f"money success{amount_to_transfer}"
            }

@app.get("/userbalance")
def get_userbalance(token:str=Depends(oauth_scheme)):
    with open ("userbalance.json","r") as userfile:
        userbalance=json.load(userfile)
    if not userbalance.get(token):
        raise HTTPException(status_code=400,detail="user not avialable")
    return {
            "username":token,
            "current_balance":userbalance.get(token)['curr_balance']
        }

           

