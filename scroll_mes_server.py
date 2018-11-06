# author : lim
# email : 940711277@qq.com

"""you can run it or not"""
"""script to print recevied message"""

import socket

serSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
serSocket.setsockopt(socket.SOL_SOCKET,socket.SOCK_STREAM,1)
localAddr = ('127.0.0.1',8888)
serSocket.bind(localAddr)
serSocket.listen(5)

print('Start a local server to print message ... \n')
while True:
    newSocket,destAddr = serSocket.accept()
    try:
        recvData = newSocket.recv(100000)
        if len(recvData)>0:
        	print(recvData.decode('utf-8'))
    except Exception as e:
    	print(e)
    finally:
        newSocket.close()

