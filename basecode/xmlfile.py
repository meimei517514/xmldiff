### -*- coding: UTF-8 -*-:
from basecode.xmlaccess import *
from basecode.xmlconfig import *
from datetime import datetime
import re,copy,json


def get_matchfile(input_name):

    #匹配用户输入的配置表名字

    match_file=[]

    file_dict = get_filepath()

    for file_name,path in file_dict.items():

        if file_name.find(input_name)==0:

            match_file.append(path)

    return match_file


def get_fileinfo(upgrade_info,branch_name,file_name):

    #获取提交的hash列表,作者列表
    if upgrade_info :
        repo.git.fetch("--all")
        repo.git.reset("--hard","origin/"+branch_name)
        repo.git.pull()

    commit_hash,commit_list=get_latestcommit(file_name) 

    return commit_hash,commit_list

def get_latestcommit(file_name):

    #循环查找该分支最近的提交记录,找到记录或者时间太长就跳出循环
    days=50

    if not file_name:
        return [],{}

    file_name = "design/"+file_name

    while True:

        log_time='--after={%s,days,ago}'%(days)
        
        commit_message=repo.git.log('--pretty=format:%cn:%s',log_time,file_name)

        if commit_message or days>168:

            commit_message=[ message.strip() for message in commit_message.split("\n")]

            commit_hash=repo.git.log('--pretty=format:%H',log_time,file_name).split("\n")

            commit_list=zip(commit_hash,commit_message)

            return commit_hash,commit_list
        else:
            days=days+7




if __name__=="__main__":
    pass

