# coding=utf-8
# author : lim
# email : 940711277@qq.com

import time
import itchat
import _thread
import socket



# 维护最近联系人的列表
user_list = list()
# 维护所有聊天记录的列表
message_dict = dict()


# 用于联系人目录的展示的列表
all_friends_list = []
# 用于联系人目录的展示的列表的下标用于选择
all_friends_line =''

# 锁，强制原子性操作
a_lock = _thread.allocate_lock()
b_lock = _thread.allocate_lock()


"""收发消息都在内存中进行，没有进行持久化,
存在相同好友名时会导致只能选择同名中的一个"""


def get_datetime():
    """获取当前时间并格式化"""
    return time.strftime('%Y-%m-%d %H:%M:%S ')


def handle_user(user_name):
    """
    全局用一个长度为10的列表维护最近联系人，用锁的方式保证原子性
    把某个联系人在最近联系人列表置顶，选择某个人发消息
    或者收到某个人发来消息都会把该联系人置顶"""
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
    """ 
        处理消息函数，存消息到消息记录大字典，发送消息到滚动屏幕。
        全局使用一个大字典，key是用户，value是个列表，
        维护与改联系人的聊天记录，锁的方式保证原子性。
        收到某人的消息，或者发送消息给某人，都会在这个
        大字典里记录其的聊天记录
    """
    b_lock.acquire()
    if user_name not in message_dict:
        message_dict[user_name] = [line_message]
    else:
        message_dict[user_name].append(line_message)
    # 发送到消息滚动屏幕，另一个终端
    _thread.start_new_thread(send_to_scroll_server,(line_message,))
    b_lock.release()


def send_to_scroll_server(message):
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
            print(e)
            message = '不支持的消息'.encode('utf-8')
        tcpCliSock.send(message)
        tcpCliSock.close()
    except Exception as e:
        pass


def get_all_friends():
    """
    获取所有的微信联系人，生成一个联系人目录，用于
    选择进行实时聊天
    """
    global all_friends_line, all_friends_list
    if (not all_friends_list) or (not all_friends_line):
        index = 1
        all_friends_line = ''
        all_friends_list=[]
        all_friends = itchat.get_friends(update=True)
        for  friend in all_friends:
            _name = friend['RemarkName'] or friend['NickName']
            all_friends_line += str(index)+'：'+_name + '; '
            all_friends_list.append(_name)
            index+=1


def input_help():
    """
        选择联系人进行实时聊天的。
        第一层选择联系人： l: 选择最近联系人列表的第一个 ”进入聊天“
                        r: 展示最近联系人列表(最多十个)，不输入直接enter相当于输入r。然后再对最近联系人列表选择用户 "进入聊天"
                         :其它的输入，直接展示联系人目录,若为联系人姓名或其在目录的坐标，---“进入聊天”
        第二层与某用户的实时聊天：
                        b: 返回根菜单， “退出聊天”
                         :输入消息后，enter，发送该消息
                         :空白enter，展示与该用户的聊天记录
    """
    time.sleep(5)
    while 1:
        command = input("\n==========根菜单==========\n"
                        "<1> l:  选择上一位联系人 ---”进入聊天“\n"
                        "<2> r:  展示最近联系人列表(最多十个)\n"
                        "<3> : 其它的输入，直接展示联系人目录,若为联系人姓名或其在目录的坐标，---“进入聊天”\n")

        if command and command not in ['l','r']:
            try:
                get_all_friends()
            except:
                time.sleep(3)
                continue
            if command in all_friends_list:
                user_name = command
            else:
                print("\n---------总联系人目录-------")
                print(all_friends_line)
                input_zero = input('>>总联系人目录，输入联系人姓名或坐标 ---”进入聊天“:\n')
                if input_zero.isdigit():
                    num = int(input_zero)
                    if num>len(all_friends_list) or num<1:
                        print('>>> 你输入了错误的坐标 ...\n')
                        continue
                    user_name = all_friends_list[num-1]
                else:
                    if input_zero not in all_friends_list:
                        print('>>> 你输入了错误的联系人姓名 ...\n')
                        continue
                    user_name = input_zero

        if command == 'r' or not command:
            if not user_list:
                continue
            line = ''
            for i,j in enumerate(user_list):
                line += str(i+1)  +'：'+  j + '; '
            print("\n-------最近联系人的目录-----")
            print(line)
            input_one = input('>> 最近联系人目录,输入联系人姓名或坐标 ---”进入聊天“\n')
            if input_one.isdigit():
                num = int(input_one)
                if num>10 or num <1:
                    user_name = user_list[0]
                else:
                    user_name = user_list[num-1]
            else:
                if input_one not in user_list:
                    user_name = user_list[0]
                else:
                    user_name =input_one

        if command == 'l':
            if not user_list:
                continue
            user_name = user_list[0]

        print(f"\n******* ‘{user_name}’ *******")
        print('>>输入 "b" 退出当前聊天 ，"enter" 发送消息或展示聊天记录... ')
        while 1:
            message = input('{} :'.format(user_name))

            # 空白enter，展示与该用户的聊天记录
            if not message:
                if user_name in message_dict.keys():
                    for mes in message_dict[user_name]:
                        print (mes)
                    print()
                continue

            # 返回根菜单， “退出聊天”
            if message == 'b':
                break

            user = itchat.search_friends(name=user_name)[0]
            user.send(message)

            # 格式化发送的消息
            line_message = get_datetime() +''+ '* 我 *' + ':  ' + message
            # 更新最近联系人列表
            handle_user(user_name)
            # 处理消息，存到消息记录大字典，发送到滚动屏幕
            handle_message(user_name, line_message)


@itchat.msg_register(itchat.content.TEXT)
def print_content(msg):
    """ 
    监听新消息，收到新消息都会调用这个函数
    添加消息到消息记录大字典，发送到滚动屏幕
    更新最近联系人列表

    """
    message = msg['Text']
    user_name = msg['User']['RemarkName'] or msg['User']['NickName']

    # 更新最近联系人列表
    handle_user(user_name)
    # 格式化收到的消息
    line_message = get_datetime() +'' + user_name +':  '+ message
    # 添加消息到消息记录大字典，发送到滚动屏幕
    handle_message(user_name, line_message)
    

def main():
    """ 
    入口函数，   
        启动一个where 1 的线程用于实时聊天
        主线程用于监听实时的消息
     """
    _thread.start_new_thread (input_help,())

    itchat.auto_login(hotReload=True)
    itchat.run()






if __name__ == '__main__':
    main()



