#!/usr/bin/python

import re
import os
import psutil

# tracepoint:syscalls:sys_enter_statfs
#     int __syscall_nr;
#     const char * pathname;
#     struct statfs * buf;

# "PID", "COMM", "FD", "ERR", "PATH"

rules = [
    {
        "desc": "[SYSTEM - GNOME]",
        "process": r"gnome-keyring-daemon|gdm-password|gdm-session-worker",
        "near": r"libgcrypt\.so\..+|libgck\-1\.so\.0|_pammodutil_getpwnam_|gkr_system_authtok",
    },
    {
        "desc": "[SYSTEM - LightDM]",  # Ubuntu/xubuntu login screen :) https://doc.ubuntu-fr.org/lightdm
        "process": r"lightdm",
        "near": r"_pammodutil_getpwnam_|gkr_system_authtok",
    },
    {
        "desc": "[SYSTEM - SSH Server]",
        "process": r"/sshd$",
        "near": r"sudo.+|_pammodutil_getpwnam_",
    },
    {
        "desc": "[SSH Client]",
        "process": r"/ssh$",
        "near": r"sudo.+|/tmp/ICE-unix/[0-9]+",
    },
    {
        "desc": "[SYSTEM - VSFTPD]",
        "process": r"vsftpd",
        "near": r"^::.+\:[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$",
    },
]  
regex_type = type(re.compile("^plop$"))
# precompile regexes to optimize speed
for x in rules:
    if "near" in x:
        if type(x["near"]) != regex_type:
            x["near"] = re.compile(x["near"])
    if "process" in x:
        if type(x["process"]) != regex_type:
            x["process"] = re.compile(x["process"])  


# chats模块
prefix =    [".config/psi/profiles",".local/psi+/profiles",                         #chats
                "sitemanager.xml", "recentservers.xml", "filezilla.xml",            #  |    #filezilla                                                          
            ]                                                                       #  |        |
suffix  =   ["accounts.xml","accounts.xml",                                         #chats      |
                ".filezilla", ".config/filezilla",                                          #filezilla  
            ]


seq_1 = [".ssh/id_rsa",".ssh/id_dsa",".ssh/id_ecdsa",".ssh/id_ed25519",]         #sysadmin-ssh
seq_2 = [".ssh/config",".ssh/config",".ssh/config",".ssh/config",]


monitorfiles = [
                "signons.sqlite","logins.json",  "Login Data",          #browsers                   
                "/.purple/accounts.xml",                                #chats
                "/.git-credentials","/.config/git/credentials",         #git
                "/.dbvis/config70/dbvis.xml", "/.sqldeveloper/SQL Developer/connections.xml", "/.squirrel-sql/SQLAliases23.xml", #databases
                
                # "/.claws-mail/accountrc","/.claws-mail/accountrc/passwordstorerc",  #mails 
                "/.claws-mail",  #"/.thunderbird",    #mails   -test_ok     由于未发现指定文件夹所以不再往下搜索                 
                "/etc/NetworkManager/system-connections/","/etc/wpa_supplicant/wpa_supplicant.conf",  #wifi
                # "/etc/shadow",                                          #!!!但是易误检!!! sysadmin-shadow    TODO
                
                # ".config/keepassx/config.ini",".config/KeePass/KeePass.config.xml",    #sysadmin-keepassconfig
                ".config/keepassx",".config/KeePass",               #sysadmin-keepassconfig    -test_ok  由于未发现指定文件夹所以不再往下搜索
                "/boot/grub/menu.lst","/boot/grub/grub.conf","/boot/grub/grub.cfg" ,     #sysadmin-grup
                
                # ".gftp/bookmarks",".gftp/bookmarks/gftprc",                            #sysadmin-gftp 
                ".gftp",                        #!!!但是易误检!!!  sysadmin-gftp  -test_ok   由于未发现指定文件夹所以不再往下搜索   TODO
                # "/etc/fstab",                   #!!!但是易误检!!!  sysadmin-fstab    TODO
                ".docker/config.json",          #sysadmin-docker
                
                # ".history",".sh_history",".bash_history",".zhistory",   #sysadmin-cli  -cli 无法运行单个参数 dhz todo: all need?
                ".local/share/mc/history",
                ".aws/credentials",                  #sysadmin-aws  
                 
                # ".ApacheDirectoryStudio/.metadata/.plugins/org.apache.directory.studio.connection.core/connections.xml"         #sysadmin-apachedirectorystudio 
                ".ApacheDirectoryStudio",              #sysadmin-apachedirectorystudio   -test_ok 由于未发现指定文件夹所以不再往下搜索
                ]

memory_cnt = 3

#test_code
# ma = re.match(r'/proc/[1-9]+/stat', '/proc/212575/stat')
# if ma:
#     print(ma.group()) 
#     # print(ma) 
# else:
#     print("no match") 

# print(psutil.pids())
piddict_stat = dict()
pidsum_stat=0
for pid in psutil.pids():
    piddict_stat[pid] = 0
    pidsum_stat=pidsum_stat+1

#test_code
# str='/proc/212575/stat'
# x=str.split('/') # [-1]
# print(x)
# pid=x[2]
# print(pid)

#test_code
# y=os.path.split(str)
# z=os.path.split(y[0])
# print(z[1])

ssh_state = 2
rules_flag = 0

while 1:
    str =  input()
    str = str.split()
    # print(str[-1])
    
    # find  单个敏感目录项
    for mnfile in monitorfiles:
        if mnfile in str[-1]:
            print("+++ *** be Scanned +++  PID:",str[0],"  COMM:",str[1],"  SensitiveFile:",str[-1])
    
    # prefix*suffix  前缀后缀的笛卡尔积任意组合
    for prefix_index in range(len(prefix)):
        for suffix_index in range(len(suffix)):
            if prefix[prefix_index] in str[-1] and suffix[suffix_index] in str[-1]:
                print("+++ *** be Scanned +++  PID:",str[0],"  COMM:",str[1],"  SensitiveFile:",str[-1])
    
    # seq 基于读取序列 seq_1 -> seq_2   
    for seq_o in seq_1:
        if ssh_state==2 and seq_o in str[-1]:
            ssh_state=1
    for seq_t in seq_2:
        if ssh_state==1 and seq_t in str[-1]:
            ssh_state=2
            print("+++ ssh be Scanned  : 先读取key 再扫描敏感文件 +++  PID:",str[0],"  COMM:",str[1])
    
    # memory模块open文件序列检测 
    # 敏感rules 
    # for rule in rules:
    #     if re.search(rule["process"], str[-1]):
    #         rules_flag = 1
    #         print("+++ rules get +++  PID:",str[0],"  COMM:",str[1])
    
    # memorpy库检测序列
    # if str[-1] == "/proc/sys/kernel/yama/ptrace_scope" and memory_cnt==3:
    if str[-1] == "/proc/sys/kernel/yama/ptrace_scope" and memory_cnt==3 :
        memory_cnt -= 1
    
    # if str[-1] == "/proc/[1-9]+/mem" and memory_cnt==2:
    if re.match(r"/proc/[1-9]+/mem",str[-1]) and memory_cnt==2 :
        memory_cnt -= 1
     
    # if str[-1] == "/proc/[1-9]+/maps" and memory_cnt==1:
    if re.match(r"/proc/[1-9]+/maps",str[-1]) and memory_cnt==1 :
        memory_cnt -= 1   
    
    if memory_cnt == 0:
        # if rules_flag ==1:
        #     print("+++ proc/pid/mem be Scanned +++  PID:",str[0],"  COMM:",str[1]) 
        print("+++ proc/pid/mem be Scanned +++  PID:",str[0],"  COMM:",str[1]) 
        memory_cnt = 3
        # rules_flag = 0
    
    
    
    # 分pid统计/proc/*/stat
    ma = re.match(r'/proc/[1-9]+/stat', str[-1])
    # print(str[-1])
    if ma:
        #test_code
        # print(ma.group())
        # print(ma)     
        # x=str[-1].split('/') # [-1]
        # print(x)
        # pid=x[2]
        # print(pid)
        
        if str[0] in piddict_stat :
            piddict_stat[str[0]] = piddict_stat[str[0]]+1
            # print("piddict_stat[" , str[0] , "] = ", piddict_stat[str[0]])
        else:
            piddict_stat[str[0]] = 0
            pidsum_stat=pidsum_stat+1
            # print("[new] piddict_stat[" , str[0] , "] = ", piddict_stat[str[0]])
        
        # print("+++  psutil.pids().count " ,psutil.pids().count() ) 
        if piddict_stat[str[0]] == pidsum_stat and str[1]!='ps':
            print("+++ *** be Scanned +++  PID:",str[0],"  COMM:",str[1]," /proc/*/stat   ")   
    # else:
    #     print("no match")
    
    # for procdic in Process.list():
    #     name = procdic["name"]
    #     pid = int(procdic["pid"])


        