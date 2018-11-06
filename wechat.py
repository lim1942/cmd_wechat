# author : lim
# email : 940711277@qq.com

import time
import itchat
import _thread
from socket import *


# get user list and message dict to save user and message
user_list = list()
message_dict = dict()

# get lock for thread safe
a_lock = _thread.allocate_lock()
b_lock = _thread.allocate_lock()

# create a socket send message to local server
tcpCliSock = socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(('127.0.0.1', 8888))




def get_datetime():
    """retuan date now"""
    return time.strftime('%Y-%m-%d %H:%M:%S ')



def handle_user(user_name):
    """ handle user list, thread safe """
    a_lock.acquire()
    if user_name not in user_list:
        user_list.insert(0,user_name)
    else:
        user_list.remove(user_name)
        user_list.insert(0,user_name)
    if len(user_list)>10:
        user_list.pop()
    a_lock.release()



def handle_message(user_name,line_message):
    """ handle message dict func,_thread safe """
    b_lock.acquire()
    if user_name not in message_dict:
        message_dict[user_name] = [line_message]
    else:
        message_dict[user_name].append(line_message)
    b_lock.release()



def send_to_scroll_server(message):
    """send received message to local server for print"""
    try:
        global tcpCliSock
        try:
            message = message.encode('utf-8', 'ignore')
        except Exception as e:
            print(e)
            message = '不支持的消息'.encode('utf-8')
        tcpCliSock.send(message)
    except Exception as e:
        tcpCliSock.close()
        tcpCliSock = socket(AF_INET, SOCK_STREAM)
        tcpCliSock.connect(('127.0.0.1', 8888))
        print(e)



def input_help(_help):
    """function to choose person and send message"""
    print(_help)
    time.sleep(5)
    while 1:
        command = input('>> Type s to select recent user to send ,type a to '
                    'send from all user, type r select last user to send:\n')

        # choose a person in all friends list
        if not user_list or command=='a':
            command = 'a'
            _all = []; j = 1; line = ''
            try:
                all_friends = itchat.get_friends(update=True)
            except:
                print('log in error !!!')
                time.sleep(3)
                continue
            for  friend in all_friends:
                _name = friend['RemarkName'] or friend['NickName']
                line += str(j)+'：'+_name + '; '; _all.append(_name); j+=1
            print(line)
            input_zero = input('>>No more recent user ,type a user (index or name)'
                        ' to send, type b() to back:\n')
            if input_zero ==  'b()':
                continue
            else:
                if input_zero.isdigit():
                    num = int(input_zero)
                    if num>j or num<1:
                        print('You type a bad index ...')
                        continue
                    user_name = _all[num-1]
                else:
                    if input_zero not in _all:
                        print('You type a bad user_name ...')
                        continue
                    user_name = input_zero
            print(user_name)


        # choose a person in 10 recent contact person
        if command == 's':
            line = ''
            for i,j in enumerate(user_list):
                line += str(i+1)  +'：'+  j + '; '
            print(line)
            input_one = input('>> There are recent users ,type a user (index or name)'
                        ' to send message,type b() to back:\n')
            if input_one == 'b()':
                continue
            if input_one.isdigit():
                num = int(input_one)
                if num>10 or num <1:
                    print('You type a bad index ...')
                    continue
                user_name = user_list[num-1]
            else:
                if input_one not in user_list:
                    print('\n>>>You type a bad user_name ...')
                    continue
                user_name =input_one

        # choose a person previous connect with
        if command == 'r':
            user_name = user_list[0]

        # handle bad input
        if command not in ['a','r','s','b()']:
            print('>> bad input \n')
            continue


        # User has been selected,now can send message to this user in the cycle
        print('>>Type b() to exit a conversation,type h() get all chatting records ')
        while 1:
            message = input('{} :'.format(user_name))

            if  message == 'h()':
                if user_name in message_dict.keys():
                    for mes in message_dict[user_name]:
                        print (mes)
                    print()
                continue

            if not message:
                continue

            if message == 'b()':
                break

            user = itchat.search_friends(name=user_name)[0]
            user.send(message)
            line_message = get_datetime() +''+ 'Me' + ':  ' + message
            handle_user(user_name)
            handle_message(user_name, line_message)



@itchat.msg_register(itchat.content.TEXT)
def print_content(msg):
    """ handle message received """
    message = msg['Text']
    user_name = msg['User']['RemarkName'] or msg['User']['NickName']

    handle_user(user_name)
    line_message = get_datetime() +''+user_name + ':  ' + message
    send_to_scroll_server(line_message)
    handle_message(user_name, line_message)



def main():
    """ main func,start a thread to input message,in main 
        process run itchat server to receive message """
    _help = '\nyou can input message after log in .....'
    _thread.start_new_thread (input_help,(_help,))

    itchat.auto_login(hotReload=True)
    itchat.run()




if __name__ == '__main__':
    main()





