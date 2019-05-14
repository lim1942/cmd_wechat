# coding=utf-8
# author : lim
"""只能发送文字消息和简单的表情,不能群聊
存在相同好友名时会导致只能选择同名中的一个"""

import time
import itchat
import _thread
import socket


# 维护所有联系人聊天记录的大字典
friends_message_dict = dict()

# 最近联系人的列表
recently_friends_list = list()
# 最近联系人的列表的标注行用于选择
recently_friends_line = str()

# 所有联系人的列表
all_friends_list = list()
# 所有联系人的列表的标注行用于选择
all_friends_line = str()

# 锁，强制原子性操作
a_lock = _thread.allocate_lock()
b_lock = _thread.allocate_lock()


def get_datetime_now():
    """获取当前时间并格式化"""
    return time.strftime('%Y-%m-%d %H:%M:%S ')


def update_recently_friends_list_and_line(friend_name):
    """
    全局用一个长度为10的列表维护最近联系人，用锁的方式保证原子性
    把某个联系人在最近联系人列表置顶，选择某个人发消息
    或者收到某个人发来消息都会把该联系人置顶"""
    global recently_friends_line
    a_lock.acquire()
    if friend_name not in recently_friends_list:
        recently_friends_list.insert(0,friend_name)
    else:
        recently_friends_list.remove(friend_name)
        recently_friends_list.insert(0,friend_name)
    if len(recently_friends_list)>10:
        recently_friends_list.pop()
    recently_friends_line = ''   
    for i,j in enumerate(recently_friends_list):
        recently_friends_line += f"{i+1} :{j}; "
    a_lock.release()


def save_message_and_send_to_terminal(friend_name,line_message):
    """ 
        处理消息函数，存消息到消息记录大字典，发送消息到滚动屏幕。
        全局使用一个大字典，key是用户，value是个列表，
        维护与改联系人的聊天记录，锁的方式保证原子性。
        收到某人的消息，或者发送消息给某人，都会在这个
        大字典里记录其的聊天记录
    """
    b_lock.acquire()
    if friend_name not in friends_message_dict:
        friends_message_dict[friend_name] = [line_message]
    else:
        friends_message_dict[friend_name].append(line_message)
    # 发送到消息滚动屏幕，另一个终端
    _thread.start_new_thread(send_message_to_another_terminal,(line_message,))
    b_lock.release()


def send_message_to_another_terminal(message):
    """
    把消息通过套接字的形式发送出去，用于另一个终端的滚动打印，
    用于正在聊天时还能收到另外用户发来的消息。
    """
    try:
        tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcpCliSock.settimeout(0.01)
        tcpCliSock.connect(('127.0.0.1', 8888))
        try:
            message = message.encode('utf-8', 'ignore')
        except Exception as e:
            message = '不支持的消息'.encode('utf-8')
        tcpCliSock.send(message)
        tcpCliSock.close()
    except Exception as e:
        pass


def update_all_friends_list_and_line():
    """
    获取所有的微信联系人，生成一个联系人目录，用于
    选择进行实时聊天
    """
    global all_friends_line, all_friends_list
    if not all_friends_list:
        index = 1
        all_friends_line = ''
        all_friends_list=[]
        all_friends = itchat.get_friends(update=True)
        for  friend in all_friends:
            friend_name = friend['RemarkName'] or friend['NickName']
            all_friends_line += f"{index}: {friend_name} ; "
            all_friends_list.append(friend_name)
            index+=1


def choose_friend_and_chat():
    """
        选择联系人进行实时聊天的。
        第一层选择联系人： l: 选择最近联系人列表的第一个 ”进入聊天“
                        r: 展示最近联系人列表(最多十个)，不输入直接enter相当于输入r。然后再对最近联系人列表选择用户 "进入聊天"
                         :其它的输入，直接展示联系人目录,若为联系人姓名或其在目录的坐标，---“进入聊天”
        第二层与某用户的实时聊天：
                        b: 返回根菜单， “退出聊天”
                         :输入消息后，enter，发送该消息
                         :空白enter，展示与该用户的聊天记录"""
    time.sleep(5)
    while 1:
        # 根菜单输入
        command = input("\n==========根菜单==========\n"
                        "<1> l:  选择上一位联系人\n"
                        "<2> r:  展示最近联系人列表(最多十个)\n"
                        "<3> : 其它的输入，直接展示联系人目录,若为联系人姓名或其在目录的坐标\n")

        # 根据输入选择用户
        if command == 'l':
            if not recently_friends_list:
                continue
            friend_name = recently_friends_list[0]

        elif command == 'r' or command =='':
            if not recently_friends_list:
                continue
            print("\n-------最近联系人的目录-----")
            print(recently_friends_line)
            recent_friend_command = input('>>> 最近联系人目录,输入联系人姓名或坐标__')
            if recent_friend_command.isdigit():
                num = int(recent_friend_command)
                if num>10 or num <1:
                    friend_name = recently_friends_list[0]
                else:
                    friend_name = recently_friends_list[num-1]
            else:
                if recent_friend_command not in recently_friends_list:
                    friend_name = recently_friends_list[0]
                else:
                    friend_name =recent_friend_command

        else:
            try:
                update_all_friends_list_and_line()
            except:
                print("正在登录 。。。")
                time.sleep(3)
                continue
            if command in all_friends_list:
                friend_name = command
            else:
                print("\n---------总联系人目录-------")
                print(all_friends_line)
                all_friend_command = input('>>> 总联系人目录，输入联系人姓名或坐标:__')
                if all_friend_command.isdigit():
                    num = int(all_friend_command)
                    if num>len(all_friends_list) or num<1:
                        print('>>> 你输入了错误的坐标 ...\n')
                        continue
                    friend_name = all_friends_list[num-1]
                else:
                    if all_friend_command not in all_friends_list:
                        print('>>> 你输入了错误的联系人姓名 ...\n')
                        continue
                    friend_name = all_friend_command            

        # 1v1聊天
        print(f"\n******* {friend_name} *******")
        print('>> 输入 "b" 退出当前聊天 ，"enter" 发送消息或展示聊天记录... ')
        while 1:
            message = input(f"To {friend_name} :")
            # 返回根菜单， “退出聊天”
            if message == 'b':
                break
            # 空白enter，展示与该用户的聊天记录
            elif message == '':
                if friend_name in friends_message_dict.keys():
                    for mes in friends_message_dict[friend_name]:
                        print (mes)
                    print()  
            else:
                friend = itchat.search_friends(name=friend_name)[0]
                friend.send(message)
                # 格式化发送的消息
                line_message = f"{get_datetime_now()} 我:  {message}"
                # 更新最近联系人列表
                update_recently_friends_list_and_line(friend_name)
                # 处理消息，存到消息记录大字典，发送到滚动屏幕
                save_message_and_send_to_terminal(friend_name, line_message)


@itchat.msg_register(itchat.content.TEXT)
def receive_handle(msg):
    """ 
    监听新消息，收到新消息都会调用这个函数
    添加消息到消息记录大字典，发送到滚动屏幕
    更新最近联系人列表
    """
    message = msg['Text']
    friend_name = msg['User']['RemarkName'] or msg['User']['NickName']

    # 更新最近联系人列表
    update_recently_friends_list_and_line(friend_name)
    # 格式化收到的消息
    line_message = f"{get_datetime_now()} {friend_name}: {message}"
    # 添加消息到消息记录大字典，发送到滚动屏幕
    save_message_and_send_to_terminal(friend_name, line_message)
    

def main():
    """ 
    入口函数，   
        启动一个where 1 的线程用于实时聊天
        主线程用于监听实时的消息
     """
    _thread.start_new_thread (choose_friend_and_chat,())
    itchat.auto_login(hotReload=True)
    itchat.run()






if __name__ == '__main__':
    main()



