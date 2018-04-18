### -*- coding: UTF-8 -*-:
import os,os.path,re,time,html

def parse_path():

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
    xml_path = parse_path()["xml_path"]

    xml_names=[]    

    xml_paths={}
    
    for root,dirs,files in os.walk(xml_path):     

        for name in files:

            if ".xml" in name:

                xml_names.append(name) 

                file_path=os.path.join(root,name)

                xml_paths[name]=file_path
                
    return sorted(xml_names),xml_paths





def open_xml(path_name):

    #打开xml文件，将数据读取成list
    file_object=open(path_name,"r")

    with file_object as xmlfile:

        xmlfile_list=list(xmlfile.readlines())

        return xmlfile_list





def get_sheetdata(sheet_data):

    #根据xml文件的原始数据，读取每行的数据
    row_data=get_rowdata(sheet_data)

    #去除每行后面的空字段，并且补全每行的长度，和表头长度一致
    row_data=["~".join(row).rstrip("~ ").split("~") for row in row_data ]

    head_line=row_data[0]

    max_len=len(head_line)

    sheet_data=[ add_len(row,max_len) for row in row_data]

    return sheet_data



def get_rowdata(sheet_data):

    #将子表每行的数据分割并读取出来    
    #print "\n".join(sheet_data[:100])
    row_data=extract_origindata(sheet_data,"<Row","</Row>")

    row_data=[ get_celldata(row) for row in row_data ]

    row_data=[ row for row in row_data if row]

    row_datas=[ row for row in row_data if len(row)<2]

    return row_data


def extract_origindata(origin_data,start_re,end_re):

    #分割好每行的数据，空行的row不算
    start_index=[ key+1 for key,line in enumerate(origin_data) if start_re in line ]

    end_index=[ key for key,line in enumerate(origin_data) if end_re in line or ( start_re in line and "/>" in line)]

    area_index=zip(start_index,end_index)

    extracted_data=[ origin_data[start:end] for start,end in area_index]

    return extracted_data




def get_celldata(row_data):

    #读取每行的表格真正数据,会有一些行全是换行符，屏蔽这种行
    row_data=restore_xml(row_data)

    cell_data=[]

    #如果有一些奇怪的行长度超过1000，就把多的空格减掉
    if len(row_data)>1000:
        temp_data = list(set(row_data))
        temp_data.sort(key=row_data.index)
        row_data=temp_data
      
    for cell in row_data:
        index_re=re.search("Index=\"([^\W]+)\"",cell)
    
        if index_re:
            index=int(index_re.group(1))-1
    
            for i in range(len(cell_data),index):
                cell_data.append("")
        data_re=re.search(">([^>]+)</",cell)
    
        data=data_re.group(1) if data_re else ""
     
        data=html.unescape(data)
    
        cell_data.append(data)

    
    return cell_data



def add_len(row,max_len):

    #根据表头长度，补全长度不足的行
    cell_len=len(row)

    if cell_len<max_len:

        for i in range(0,max_len-cell_len):

            row.append("")

    return row



def restore_xml(file_line):

    #将因为标签数据过长而换行的行数据恢复              

    xml_file=[]

    ignore_line=[]

    for key,line in enumerate(file_line):

        if key not in ignore_line:

            xml_file.append(line)
            
            slide_count=line.count("<")

            anslide_count=line.count(">")

            if "<Cell" in line and slide_count!=anslide_count:

                for index,cell in enumerate(file_line[key+1:]):

                    if "<" in cell and "<Cell" not in cell:

                        append_line=cell.strip("-+ ")

                        last=len(xml_file)-1

                        xml_file[last]=xml_file[last].strip("\r\n")+" "+append_line

                        ignore_line.append(key+index+1)

                    else:
                        break

    return xml_file


