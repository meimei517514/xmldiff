from git import *
import os,os.path


def parse_config():

    #读path.txt配置文件，获得git地址信息
    path_dict={}
    with open("basecode/path.txt") as path:

        for line in path.readlines():

            if not line.startswith("#"): 

                line_info=line.split("=")
                
                line_info=[ x.strip("\n") for x in line_info ]

                path_name=line_info[0]

                path_info=line_info[1]

                path_dict[path_name]=path_info

        
    return path_dict
        
def get_xmlpath():

    #获得common目录下所有xml文件的真实路径
    xml_path = parse_config()["common_path"]

    xml_names=[]    

    xml_paths={}
    
    for root,dirs,files in os.walk(xml_path):     

        for name in files:

            if ".xml" in name:

                xml_names.append(name) 

                file_path=os.path.join(root,name)

                xml_paths[name]=file_path
                
    return sorted(xml_names),xml_paths


def get_filepath():

    #获得common目录下所有文件的真实路径
    common_path = parse_config()["common_path"]


    file_paths={}
    
    for root,dirs,files in os.walk(common_path):     

        for name in files:
                
                refer_root=root.split(common_path)[1]

                file_path=os.path.join(refer_root,name) if refer_root else name

                file_paths[name]=file_path
                
    return file_paths




path_sum=parse_config()

project_path = path_sum["project_path"]

git_path = path_sum["git_path"]

repo=Repo.init(git_path)
















