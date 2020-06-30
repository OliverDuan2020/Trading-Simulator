import tkinter as tk
from tkinter import messagebox
import threading
from yahoo_fin import stock_info as si
from termcolor import cprint
from stringcolor import *
import datetime
import tweepy, json
import time
import re
from nltk.tokenize import TweetTokenizer
import Sentimentanalysis



## Here is the function for the trading section

def getBuyprice(symbol):

    symbol_list.append(symbol)
    PnL_symbol_list.append(symbol)
    buy_price=si.get_live_price(symbol)
    buy_price_list.append(buy_price)
    PnL_buy_price_list.append(buy_price)
    buy_price="{:.2f}".format(buy_price)
    buy_string="Buy Price: "+ str(buy_price) + " dollar a share"
    label_confirmation['text']=buy_string

def getQuantity(quantity):
    quantity=int(quantity)
    quantity_list.append(quantity)
    PnL_quantity_list.append(quantity)
    inventory()
    printInventory(portfolio)

def getSellprice(symbol):
    sell_symbol_list.append(symbol)
    sell_price=si.get_live_price(symbol)
    global sell_now_ticker
    sell_now_ticker=symbol
    sell_price_list.append(sell_price)
    sell_price = "{:.2f}".format(sell_price)
    sell_string = "Sell Price: " + str(sell_price) + " dollar a share"
    label_sell_confirmation['text'] = sell_string

def getSellquantity(quantity):
    quantity=int(quantity)
    global sell_now_quantity
    sell_now_quantity=quantity
    sell_quantity_list.append(quantity)
    inventory()
    printInventory(portfolio)
    PnL()

def getCurrentprice():
    All_price_up=''
    All_price_down=''
    show_list=[]
    global PnL_symbol_list
    for i in PnL_symbol_list:
        if i not in show_list:
            show_list.append(i)
            try:
                now_price=si.get_live_price(i)
                if PnL_buy_price_list[PnL_symbol_list.index(i)] < now_price:
                    current_price_string_up = " current price " + i+ " : " + str(now_price) +'\n'
                    All_price_up +=current_price_string_up
                if PnL_buy_price_list[PnL_symbol_list.index(i)] > now_price:
                    current_price_string_down= " current price " + i+ " : " + str(now_price) +'\n'
                    All_price_down += current_price_string_down
            except:
                All_price_up="receive an error in connecting with the server!"
                All_price_down="receive an error in connecting with the server!"

    label_current_price_up['text'] = All_price_up
    label_current_price_down['text']= All_price_down

    threading.Timer(1.0, getCurrentprice).start()

def inventory():
    global portfolio
    transaction_number = 1
    global sell_now_ticker
    global sell_now_quantity
    global symbol_list
    global buy_price_list
    global quantity_list
    for i in range(len(symbol_list)):
        try:
            portfolio[transaction_number] = {"ticker": symbol_list[i], "buy": buy_price_list[i],
                                             "quantity": quantity_list[i]}
            if sell_now_ticker in portfolio[transaction_number]["ticker"]:
                if portfolio[transaction_number]["quantity"] == sell_now_quantity:
                    del portfolio[transaction_number]
                    symbol_list.remove(symbol_list[i])
                    buy_price_list.remove(buy_price_list[i])
                    quantity_list.remove(quantity_list[i])

                else:
                    portfolio[transaction_number]["quantity"] -= sell_now_quantity
                    quantity_list[i] -= sell_now_quantity

                sell_now_ticker = 'FAKE TICKER'
                sell_now_quantity = 0

            transaction_number += 1
        except:
                print("Out of range")

def printInventory(portfolio):
    All_quantity=''
    for transaction in portfolio:
        inventory_string = "Stock Ticker: " + str(portfolio[transaction]["ticker"])+'\n'
        inventory_string += "Buy price: $ "+ str("{:.2f}".format(portfolio[transaction]["buy"])) +" Quantity: "+ str(portfolio[transaction]["quantity"])+'\n'
        print("\nStock Ticker:",portfolio[transaction]["ticker"])

        print(portfolio[transaction]["buy"],portfolio[transaction]["quantity"])
        All_quantity += inventory_string

    label_inventory['text'] = All_quantity

def PnL():
    profit_loss=0
    global sell_quantity_list
    global sell_price_list
    global sell_symbol_list
    global PnL_symbol_list
    global PnL_buy_price_list
    total_PnL =0
    for i in range(len(sell_symbol_list)):
        if sell_symbol_list[i] in PnL_symbol_list:
            profit_loss=(sell_price_list[i]-PnL_buy_price_list[PnL_symbol_list.index(sell_symbol_list[i])])*sell_quantity_list[i]
            total_PnL += profit_loss

    label_PnL['text'] = " Profit and Loss: " + str(total_PnL)

## Here are the functions for the tweets section

consumer_key ='h7wfN4WcNhXitrP6jW549ux9R'
consumer_secret='a6Q3ccJOEtbVpqyKDQ56theJ1QXzNSdoxCDMSlfpp3gIksUBSQ'
access_token ='1268968436719386624-8dC1pk0BC9sahJVjRXRACgkokzVTl0'
access_token_secret ='GHudtsDAQVOKSFj4KHI3BSJqgDFacvEjO8FxVF1Hjp9Nn'

class MyStreamListener(tweepy.StreamListener):

    def __init__(self, time_limit=60):
        self.start_time = time.time()
        self.limit = time_limit
        super(MyStreamListener, self).__init__()

    def on_status(self, status):
        if (time.time() - self.start_time) < self.limit:
            if status.text.startswith("RT @") == True:  ## Here I make sure I only record tweets that are not retweets
                result = ''


            else:
                result = 'This tweet said: ' + status.text

            tknzr = TweetTokenizer()  ##This special method breaks up a complete sentence into a list of words

            tweet_tokens = tknzr.tokenize(result)
            text = ''
            cleaned_tokens_list = []

            for token in tweet_tokens:
                token = re.sub(r'^https?:\/\/.*[\r\n]*', 'url', token,
                               flags=re.MULTILINE)  ##This code detects whether a token has a URL
                                                    ##If found, it will replace the token with a new token that shows "url"
                cleaned_tokens_list.append(token)

                text = ' '.join(str(tokens) for tokens in cleaned_tokens_list)

            with open('tweets_clear.txt','a') as outfile:  ## This program will write the output live tweet into a file called tweets.txt

                outfile.write('\n')

                json.dump(text, outfile)

            return True
        else:

            return False


    def on_error(selfself,status_code):
        if status_code == 420:
            print('Rate limited by Twitter!')

        else:
            print(status_code)


def getTweets(name):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)





    myStream = tweepy.Stream(auth,listener=MyStreamListener(time_limit=20))
    myStream.filter(track=[name])

# Here is the section for install a countdown

class Countdown(tk.Frame):
    '''A Frame with label to show the time left, an entry
       to input the seconds to count down from, and a
       start button to start counting down.'''
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()
        self.show_widgets()
        self.seconds_left = 0
        self._timer_on = False

    def show_widgets(self):

        self.label.pack()
        self.start.pack()

    def create_widgets(self):

        self.label = tk.Label(self, text="00:00:00")
        self.start = tk.Button(self, text="Start",
                               command=self.start_button)

    def countdown(self):
        '''Update label based on the time left.'''
        self.label['text'] = self.convert_seconds_left_to_time()

        if self.seconds_left:
            self.seconds_left -= 1
            self._timer_on = self.after(1000, self.countdown)
        else:
            self._timer_on = False

    def start_button(self):
        '''Start counting down.'''
        # 1. to fetch the seconds
        self.seconds_left = 5
        # 2. to prevent having multiple
        self.stop_timer()
        #    timers at once
        self.countdown()

    def stop_timer(self):
        '''Stops after schedule from executing.'''
        if self._timer_on:
            self.after_cancel(self._timer_on)
            self._timer_on = False

    def convert_seconds_left_to_time(self):

        return datetime.timedelta(seconds=self.seconds_left)


## Here is the code for the sentiment analysis score code

def startSentiment():
    result= Sentimentanalysis.main()
    label_sentiment_score['text'] = result



portfolio = {}

##This is for buy stock, I create three lists with equal length to store the buy price, quantity and ticker
symbol_list = []
quantity_list=[]
buy_price_list=[]

##This is for sell stock, I create three lists with equal length to store the sell price, quantity and ticker
sell_price_list=[]
sell_symbol_list=[]
sell_quantity_list=[]


## This is for updating the inventory
sell_now_ticker='FAKE TICKER'
sell_now_quantity=0

##I need to create another 3 lists to hold value from symbol, quantity, buy_price lists as the elements within the three lists are removed at the end
PnL_symbol_list=[]
PnL_quantity_list=[]
PnL_buy_price_list=[]

annotation = ''

sell_price = 0
buy_price = 0

HEIGHT = 600
WIDTH = 800

root = tk.Tk() #create an empty window
root.title("Trading Simulator")


canvas = tk.Canvas(root,height = HEIGHT, width = WIDTH) # Add a canvas
canvas.pack()

background_image= tk.PhotoImage(file='Finance.png') #not JPG
background_label=tk.Label(root,image=background_image)
background_label.place(relwidth =1,relheight =1)

###Everything above looks very ok


#Firstly, I want to have an introduction on the screen, I would like to design this as a button
def introduction():
    messagebox.showinfo("introduction",'Welcome to my trading simulator! Here you can buy and sell American equities and experience the dynamics of the financial market\n'
          'please take your time and expore the simulator. May the odds always be in your favor!')


frame = tk.Frame(root)
frame.place(relx = 0.001, rely =0.15, relwidth=0.15, relheight =0.1) #set up a frame on canvas, relative value


button = tk. Button(frame, text = "Introduction", font = 40,command=introduction) # Add a button that is on the frame
button.place(relx=0.0001, relwidth=1, relheight =1)

##Next, I want to create another frame+entry field+ button to let user input the stock that he is going to buy

frame_get_stock = tk.Frame(root)
frame_get_stock.place(relx = 0.15, rely =0.25, relwidth=0.35, relheight =0.05,anchor = 'n')

button_for_stock = tk. Button(frame_get_stock,text = "Ticker?", font = 5,anchor='w', padx=2,command = lambda : getBuyprice(entry.get()))
button_for_stock.place(relx=0.7,relwidth=1, relheight=1)


entry = tk.Entry(frame_get_stock, font = 40,bd=5)
entry.place(relx = 0.1,rely=0.01, relwidth =0.6, relheight=1)

##I also need to know the quantity of the stock that the user is buying. So I need him to input that number
frame_quantity=tk.Frame(root)
frame_quantity.place(relx=0.15,rely=0.3,relwidth =0.35,relheight =0.05,anchor ='n')

button_for_quantity = tk. Button(frame_quantity,text = "Quantity?", font = 5,anchor='w', padx=2,command = lambda : getQuantity(entry_quantity.get()))
button_for_quantity.place(relx=0.7,relwidth=1, relheight=1)


entry_quantity = tk.Entry(frame_quantity, font = 40,bd=5)
entry_quantity.place(relx = 0.1,rely=0.01, relwidth =0.6, relheight=1)

##Then, I need to have a label area to show the confirmation of purchase. But I need to create a frame first

frame_confirmation=tk.Frame(root,bg = '#80c1ff',bd= 3)
frame_confirmation.place(relx=0.15,rely=0.35,relwidth =0.35,relheight =0.05,anchor ='n')

label_confirmation = tk.Label(frame_confirmation, anchor= 'n',justify='center')
label_confirmation.place(relwidth=1, relheight=1)


##Then I need to create a label are  for the current price
frame_current_price=tk.Frame(root,bg = '#80c1ff',bd= 10)
frame_current_price.place(relx=0.15,rely=0.4,relwidth =0.35,relheight =0.4,anchor ='n')

label_current_price_up = tk.Label(frame_current_price, anchor= 'ne',justify='center',bd=2, fg= 'green')
label_current_price_up.place(relwidth=1, relheight=0.5)

label_current_price_down=tk.Label(frame_current_price, anchor= 'ne',justify='center',bd=2, fg ='red')
label_current_price_down.place(relx=0.01, rely=0.6,relwidth=1, relheight=0.4)

##Then I need to create a label area for inventory

frame_inventory=tk.Frame(root,bg = '#80c1ff',bd= 10)
frame_inventory.place(relx=0.55,rely=0.4,relwidth =0.35,relheight =0.4,anchor ='n')

label_inventory = tk.Label(frame_inventory, anchor= 'nw',justify='center',bd=2)
label_inventory.place(relwidth=1, relheight=1)

##I need to create a sell button
frame_sell_stock = tk.Frame(root)
frame_sell_stock.place(relx = 0.55, rely =0.25, relwidth=0.35, relheight =0.05,anchor = 'n')

button_sell_stock = tk. Button(frame_sell_stock,text = "Sell?", font = 5,anchor='w', padx=2,command = lambda : getSellprice(entry_sell_stock.get()))
button_sell_stock.place(relx=0.7,relwidth=1, relheight=1)


entry_sell_stock = tk.Entry(frame_sell_stock, font = 40,bd=5)
entry_sell_stock.place(relx = 0.1,rely=0.01, relwidth =0.6, relheight=1)

## I need to know how many shares that the user would like to sell
frame_sell_quantity = tk.Frame(root)
frame_sell_quantity.place(relx = 0.55, rely =0.3, relwidth=0.35, relheight =0.05,anchor = 'n')

button_sell_quantity = tk. Button(frame_sell_quantity,text = "Quantity?", font = 5,anchor='w', padx=2,command = lambda : getSellquantity(entry_sell_quantity.get()))
button_sell_quantity.place(relx=0.7,relwidth=1, relheight=1)


entry_sell_quantity = tk.Entry(frame_sell_quantity, font = 40,bd=5)
entry_sell_quantity.place(relx = 0.1,rely=0.01, relwidth =0.6, relheight=1)

##I need to add a sell confirmation

frame_sell_confirmation=tk.Frame(root,bg = '#80c1ff',bd= 3)
frame_sell_confirmation.place(relx=0.55,rely=0.35,relwidth =0.35,relheight =0.05,anchor ='n')

label_sell_confirmation = tk.Label(frame_sell_confirmation, anchor= 'n',justify='center')
label_sell_confirmation.place(relwidth=1, relheight=1)

## I would like to have a screen to show Profit and loss

frame_PnL = tk.Frame(root,bg = '#80c1ff',bd= 3)
frame_PnL.place(relx = 0.38, rely =0.13, relwidth=0.35, relheight =0.1)

label_PnL = tk.Label(frame_PnL, anchor= 'n',justify='center',bd=2 )
label_PnL.place(relwidth=1, relheight=1)

## I need to add a frame+ label+ button to let user input the text that he wants to search in tweeter

frame_tweets = tk.Frame(root)
frame_tweets.place(relx = 0.55, rely =0.85, relwidth=0.35, relheight =0.05,anchor = 'n')

button_tweets = tk. Button(frame_tweets,text = "Tweets?", font = 5,anchor='w', padx=2,command = lambda : getTweets(entry_tweets.get()))
button_tweets.place(relx=0.7,relwidth=1, relheight=1)


entry_tweets = tk.Entry(frame_tweets, font = 40,bd=5)
entry_tweets.place(relx = 0.1,rely=0.01, relwidth =0.6, relheight=1)


## I need to create a countdown frame

frame_countdown=tk.Frame(root)
frame_countdown.place(relx=0.85,rely=0.35,relwidth =0.25,relheight =0.2,anchor ='n')
countdown=Countdown(frame_countdown)
countdown.pack()


## Add a text block to explain the countdown mechanism

frame_countdown_explan=tk.Frame(root)
frame_countdown_explan.place(relx=0.85,rely=0.45,relwidth =0.25,relheight =0.1,anchor ='n')
label_countdown_explan=tk.Label(frame_countdown_explan, anchor= 'n',justify='center',bd=2, text = 'Once clicked "Tweets?" button, click "Start" button here and'+'\n'
'wait until the time runs out.' +'\n'+' Then click "Score?" button to get the sentiment score' )
label_countdown_explan.place(relwidth=1, relheight=1)


## design a frame+ label for sentiment analysis score

frame_sentiment_score=tk.Frame(root,bg = '#80c1ff',bd= 1)
frame_sentiment_score.place(relx = 0.55, rely =0.9, relwidth=0.95, relheight =0.1,anchor = 'n')

button_sentiment_score = tk. Button(frame_sentiment_score,text = "Scores?", font = 5,anchor='w', padx=2,command = lambda :startSentiment())
button_sentiment_score.place(relx=0.7,relwidth=1, relheight=1)

label_sentiment_score = tk.Label(frame_sentiment_score, font = 5,bd=1,text ='test',justify='left')
label_sentiment_score.place(relx = 0.01,rely=0.01, relwidth =0.67, relheight=1)

getCurrentprice()


root.mainloop()
