from flask import Flask, request
import csv
import requests
from twilio.twiml.messaging_response import MessagingResponse
import os
from twilio.rest import Client
from random import randint, shuffle
import re


# os.remove('phoneNumbers.csv')


app = Flask(__name__)

quest_round = [0]
quest_members = []

quest_members_waiting = [False]

quest_answers_waiting = []

quest_results = [[], [], [], [], []]

version = -1

numbers = []

lady_owner = ''

lady_used = False

lady_of_the_lake = False

successful_missions = [0]

failed_missions = [0]

ACCOUNT_SID = 'AC455daabdc4fc69ab58983cb2bda4a336'
AUTH_TOKEN = '6d71656c18d87bdde5969cdf3a209769'
NUM_HOLDER = ('num', 'name')
CLIENT = Client(ACCOUNT_SID, AUTH_TOKEN)
roles = []

role_set = [

                [
                    'Merlin',
                    'Minion of Mordred',
                    'Minion of Mordred',
                    'Loyal Servant of Arthur',
                    'Loyal Servant of Arthur'
                ],
                [
                    'Merlin',
                    'Morgana',
                    'Mordred',
                    'Percival',
                    'Minion of Mordred',
                    'Loyal Servant of Arthur'
                ],
                [
                    'Merlin',
                    'Morgana',
                    'Mordred',
                    'Percival',
                    'Minion of Mordred',
                    'Loyal Servant of Arthur',
                    'Loyal Servant of Arthur'
                ],
                [
                    'Merlin',
                    'Morgana',
                    'Mordred',
                    'Percival',
                    'Minion of Mordred',
                    'Loyal Servant of Arthur',
                    'Loyal Servant of Arthur',
                    'Loyal Servant of Arthur'
                ],
                [
                    'Merlin',
                    'Morgana',
                    'Mordred',
                    'Percival',
                    'Minion of Mordred',
                    'Loyal Servant of Arthur',
                    'Loyal Servant of Arthur',
                    'Loyal Servant of Arthur',
                    'Loyal Servant of Arthur',
                ],
                [
                    'Merlin',
                    'Morgana',
                    'Mordred',
                    'Percival',
                    'Minion of Mordred',
                    'Loyal Servant of Arthur',
                    'Loyal Servant of Arthur',
                    'Loyal Servant of Arthur',
                    'Loyal Servant of Arthur',
                    'Oberon'
                ],

            ]

goods = [
    'Merlin',
    'Percival',
    'Loyal Servant of Arthur',
         ]

evils = [
    'Morgana',
    'Mordred',
    'Minion of Mordred',
    'Oberon'
         ]

contacts = []

snipe_waiting = [False]

host = ''

regex_parse = '(?P<initialize>((?P<create>create)|(?P<join>join)|(?P<ladyOfTheLake>lady)) *(?P<lady>lady)? *' \
              '(?P<name>[a-zA-Z]+))|(?P<snipe>(snipe) *(?P<target>[a-zA-Z]+))|(?P<players>players)|(?P<start>start)'
parser = re.compile(regex_parse, re.IGNORECASE)

contact_dict = {}


def merlin():
    return roles[0]


def morgana():
    return roles[1]


def mordred():
    return roles[2]


def percival():
    return roles[3]


def minion():
    return roles[4]


def servant():
    return roles[5]


# Helper Functions


def host_num():
    return numbers[0]


def notify_all(message):
    for x in numbers:
        notify_player(x, message)


def notify_player(number, message):
    message = CLIENT.messages \
        .create(
            body=message,
            from_='+14155824135',
            to=number
        )
    print(message.sid)


def notify_host(message):
    message = CLIENT.messages \
        .create(
            body=message,
            from_='+14155824135',
            to=host_num()
    )
    print(message.sid)


def write_new_player(num, name):
    numbers.append(num)
    contacts.append((num, name))
    contact_dict[num] = name


def assign_roles():
    global roles
    global version
    players = contacts
    shuffle(players)
    version = len(numbers)-5
    roles = role_set[version]
    for x in range(len(players)):
        num, name = players[x]
        roles[x] = (roles[x], num, name)
    print("roles:  ")
    print(roles)


def notify_roles():
    global roles
    global version
    global lady_of_the_lake
    global lady_owner
    print('roles in notify_roles')
    print(roles)
    temp_roles = roles
    shuffle(temp_roles)
    print(temp_roles[0])
    _, _, fq_name = temp_roles[0]
    first_quest = ". First quest goes to " + fq_name + ". "
    if lady_of_the_lake:
        _, lady_num, lady_name = temp_roles[1]
        lady_owner = (lady_num, lady_name)
        first_quest += lady_name + " has the lady of the lake. Text 'Lady *someone's name*' to lady them."
    for x in range(len(numbers)):
        role, number, name = roles[x]
        print(roles[x])
        if role == 'Merlin':
            print(roles[1])
            _, _, evil1 = roles[1]
            _, _, evil2 = roles[4]
            evil3 = ''
            if version == 4:
                _, _, evil3 = roles[9]
            notify_player(number, 'You are Merlin. The evils are ' + evil1 + ', ' + evil2 + ', ' + evil3
                          + first_quest)
        if role == 'Morgana':
            _, _, evil1 = roles[2]
            _, _, evil2 = roles[4]
            notify_player(number, 'You are Morgana. The evils are you, ' + evil1 + ', and ' + evil2 + first_quest)
        if role == 'Mordred':
            _, _, evil1 = roles[1]
            _, _, evil2 = roles[4]
            notify_player(number, 'You are Mordred. The evils are you, ' + evil1 + ', and ' + evil2 + first_quest)
        if role == 'Percival':
            _, _, merlin = roles[0]
            _, _, morgana = roles[1]
            if randint(0, 1) == 1:
                notify_player(number, 'You are Percival. Merlin and Morgana are, ' + merlin + ', and ' + morgana +
                              '. Figure out which is witch and which is warlock' + first_quest)
            else:
                notify_player(number, 'You are Percival. Merlin and Morgana are, ' + morgana + ', and ' + merlin +
                              '. Figure out which is witch and which is warlock' + first_quest)

        if role == 'Minion of Mordred':
            _, _, evil1 = roles[1]
            _, _, evil2 = roles[2]
            notify_player(number,
                          'You are a Minion of Mordred. The evils are you, ' + evil1 + ', and ' + evil2 +
                          ". If you're playing a five man you're counted twice" + first_quest)
        if role == 'Loyal Servant of Arthur':
            notify_player(number, 'You are a Loyal Servant of Arthur. Long live the King' + first_quest)
        if role == 'Oberon':
            notify_player(number, "You are Oberon. You seek Arthur's throne. You are Evil." + first_quest)


def get_quest():
    quest_members_waiting[0] = True
    print(quest_members_waiting)
    print(host)
    notify_host('Who is on the quest?')


def convert(string):
    li = list(string.split(" "))
    return li


def notify_quest_members():
    for x in quest_members:
        for j in roles:
            _, number, name = j
            if name.lower() == x.lower():
                notify_player(number, 'pass or fail?')


def list_to_string(s):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        str1 += ele + '   '

        # return string
    return str1


def send_quest_results():
    global lady_used
    quest = quest_results[quest_round[0] - 1]
    shuffle(quest)
    results = list_to_string(quest)
    message = ''
    if 'fail' in quest:
        failed_missions[0] += 1
        message = 'The Quest has failed. Results: ' + results + "-- Host must send in members' names for next quest"
    else:
        successful_missions[0] += 1
        message = 'The Quest was successful! Results: ' + results + "-- Host must send in members' names for next quest"
    if successful_missions[0] == 3:
        _, mord_num, mord_name = mordred()
        message = '3 successful quests! Evils have a chance to snipe Merlin.(' + mord_name + 'is your Assassin)'
        snipe_waiting[0] = True
    elif failed_missions[0] == 3:
        message = '3 failed quests. Camelot is Ruined.'
    else:
        quest_members_waiting[0] = True
    quest_round[0] += 1
    notify_all(message)
    lady_used = False


# Main Operator

@app.route('/bot', methods=['POST'])
def bot():
    global parser
    global lady_of_the_lake
    global lady_owner
    global lady_used
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False
    num = request.values.get('From', '')
    messenger_name = ''
    if num in contact_dict:
        messenger_name = contact_dict[num]
    print(messenger_name)
    print('pass' in incoming_msg or 'fail' in incoming_msg)
    print(messenger_name in quest_members)
    parsing = re.match(parser, incoming_msg)
    print(parsing)
    if parsing:
        if parsing.group('create'):
            if parsing.group('lady'):
                lady_of_the_lake = True
            write_new_player(num, parsing.group('name'))
            msg.body('Game created. Waiting on others')
            responded = True
        elif parsing.group('start'):
            assign_roles()
            notify_roles()
            get_quest()
            responded = False
            quest_round[0] = 1
        elif parsing.group('join'):
            # join group
            write_new_player(num, parsing.group('name'))
            _, host_name = contacts[0]
            msg.body('You joined ' + host_name + 's game. Waiting on others...')
            responded = True
        elif parsing.group('players'):
            players = 'Players:  '
            for x in contact_dict:
                players += contact_dict[x] + '  '
            msg.body(players)
            responded = True
        elif parsing.group('snipe') and snipe_waiting[0] and num in mordred():
            if incoming_msg.replace('snipe', '') in merlin():
                notify_all('The Great Merlin has been sniped! Evil reigns in Camelot!')
            else:
                notify_all('The noble' + parsing.group('target') +
                           ' has taken the arrow for Merlin! Long live the King!')
        elif parsing.group('ladyOfTheLake') and num in lady_owner and quest_round[0] > 2 and not lady_used:
            msg.body("Couldn't find the player you were asking for. Text 'players' to get the list of player names.")
            _, ladier = lady_owner
            responded = True
            for i in roles:
                role, num, name = i
                if name.lower() == parsing.group('name').lower():
                    if role in goods:
                        msg.body(name + " is good!")
                    else:
                        msg.body(name + " is evil!")
                    lady_owner = (num, name)
                    notify_all(ladier + " is ladying " + name)
                    lady_used = True

    elif quest_members_waiting[0] and num == host_num():
        print(msg)
        quest_members_waiting[0] = False
        members = convert(incoming_msg)
        for x in members:
            quest_members.append(x.lower())
            quest_answers_waiting.append(True)
        notify_quest_members()
        print(quest_answers_waiting)
        print(quest_members)
        responded = False
    elif ('pass' in incoming_msg or 'fail' in incoming_msg) and \
            quest_answers_waiting and messenger_name.lower() in quest_members:
        print('DECISION RECEIVED')
        quest_members.remove(messenger_name)
        quest_answers_waiting.pop(0)
        quest_results[quest_round[0]-1].append(incoming_msg)
        print(quest_answers_waiting)
        print(quest_members)
        print(quest_results)
        if not quest_answers_waiting:
            send_quest_results()
        responded = True
        msg.body('decision received')
    else:
        print(messenger_name)
    if not responded:
        resp.message("")
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
