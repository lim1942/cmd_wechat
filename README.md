命令行版的微信，上班专用，不用打开微信也能够进行收发消息啦。
老板以为我在敲命令，其实我在回微信，办公室利器。
两个命令行窗口，一个用于发消息，一个用于打印消息，两个窗口之间用socket套接字进行通信。

一.依赖 
python3 + itchat

二.环境 
mac/windows/linux

三.运行
1.安装好python3以后，pip install itchat (安装itchat)

2.下载本项目进入项目目录

3.python3 wechat.py

4.运行后，进行扫码登录，即可收发消息啦

（a实现了从所有人中选择一个发消息
b实现了从最近10个联系人中选择一个发消息
c实现了选择上一个联系人发消息
d打印与该联系人的聊天记录）

四.python3 scroll_mess_server.py （可选运行）
  运行后可打印实时收到的新消息,在 wechat.py 运行后才可运行。


 作者：何林 
 e-mail:940711277@qq.com



