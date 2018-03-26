### -*- coding: UTF-8 -*-:
from basecode.xmlaccess import *
import os,os.path,copy,re
from git import *

path_sum=parse_path()

git_path = path_sum["git_path"]

repo=Repo.init(git_path)

xml_names,xml_paths=get_xmlpath()

nonerefer_list=["language.xml","reward.xml"]



def get_sheetinfo(file_selected,sheet_selected,xml_paths,upgrade_info):

    #获得文件的子表信息，以及准备好子表的数据
    if upgrade_info :
        repo.git.fetch("--all")
        repo.git.reset("--hard")
 

    file_path=xml_paths[file_selected] 

    file_data=open_xml(file_path)

    sheet_names=[ re.search("\"(.+)\"",line).group(1) for line in file_data if "<Worksheet " in line] 

    sheet_namedict=dict( [(sheet,file_selected) for sheet in sheet_names] )

    sheet_data=extract_origindata(file_data,"<Worksheet ","</Worksheet>")

    sheet_datadict=dict(zip(sheet_names,sheet_data))

    sheet_selected=sheet_selected if sheet_selected else sheet_names[0]

    sheet_data=sheet_datadict[sheet_selected]  

    return sheet_namedict,sheet_data



def get_workbookdata(sheet_data,file_selected):

    #读取子表的真正有用数据，然后进行过滤和二次加工
    sheet_data=get_sheetdata(sheet_data)

    #去除每张表最后面的空行，为了美观
    for index in range(len(sheet_data)-1,0,-1):
        if not any(sheet_data[index]):
            sheet_data.pop(index)
        else:
            break
    head_line=sheet_data[0]

    max_len=len(head_line)

    sheet_data=[ map_rowdata(head_line,row,max_len) for row in sheet_data]

    sheet_data= map_reference(sheet_data)  if not any( name==file_selected for name in nonerefer_list) else sheet_data 

    return sheet_data




def map_rowdata(head_line,row,max_len):

    row=[ [head_line[index],row[index] ] for index in range(0,max_len) ]

    return row



def map_reference(sheet_data):

    #根据对应关系对表格数据进行二次加工，替换成最终的数据
    #get_languagedata()

    language_data=make_languagedata()

    reward_data=make_rewarddata()

    sheet_data=[ map_cellrefer(row,language_data,reward_data) for row in sheet_data]

    return sheet_data


def map_cellrefer(row,language_data,reward_data):

    #根据对应关系对表格数据进行二次加工，替换成最终的数据
    for cell in row:

        key=cell[0]

        value=cell[1]

        if key in "Reward" and value:
                
                cell[1]= reward_data[value] if value in reward_data else value 

        if value.startswith("TID_"):

                cell[1]= language_data[value] if value in language_data else value 

    return row



def get_languagedata():

    row_data=get_origindata(xml_paths,"language.xml")

    row_data=[row for row in row_data if len(row)>=2]

    row_datas=[ row for row in row_data if len(row)>2 ]

    language_data=dict(row_data)

    #print language_data

 


    
def make_languagedata():

    #读取language表，准备好要应用的数据
    language_data={}

    row_data=get_origindata(xml_paths,"language.xml")

    for row in row_data:

        if len(row)>=2:

            language_data[row[0]]=row[1]

    return language_data


def get_origindata(xml_paths,file_name):

    #读取文件的原始信息
    file_path=xml_paths[file_name]

    file_data=open_xml(file_path)

    row_data=get_rowdata(file_data)

    return row_data




def make_rewarddata():
 
    #读取reward表，准备好要应用的数据
    reward_data={}

    row_data=get_origindata(xml_paths,"reward.xml")

    for index,row in enumerate(row_data):
        if row[1].isdigit():

            container=[]

            key=row[2]

            add_container(container,row[3:])

            for row_next in row_data[index+1:]:
                if not row_next[1]:
                    
                    add_container(container,row_next[3:])
                else:
                    break
            value=" ".join(container)

            reward_data[key]=value

    return reward_data


def add_container(container,row):

    #reward表的奖励可能会跨行，需要将奖励的所有行数据合并
    value_list=[ cell for cell in row if cell]

    value_str="["+" ".join(value_list)+"]"

    container.append(value_str)

            




if __name__=="__main__":
    pass

