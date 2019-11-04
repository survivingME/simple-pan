import os
import time
import json


def format_size(bytes):
    try:
        if bytes == "":
            return "dir"
        bytes = float(bytes)
        kb = bytes / 1024
    except Exception as e:
        print("format size error, ", e)
        return "Error"

    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.2fGB" % (G)
        else:
            return "%.2fMB" % (M)
    else:
        return "%.2fKB" % (kb)


def get_file_size(path):
    try:
        if os.path.isfile(path):
            size = os.path.getsize(path)
        else:
            size = ""
        return format_size(size)
    except Exception as err:
        print(err)


def get_file_create_time(file_path):
    t = os.path.getctime(file_path)
    return stamp_to_time(t)


def stamp_to_time(time_stamp):
    time_struct = time.localtime(time_stamp)
    return time.strftime('%Y-%m-%d %H:%M:%S',time_struct)


def get_files_size_json():
    files = os.listdir('./upload/')
    file_list = []
    for file in files:
        file_path = './upload/' + file
        dic = {'value': round(os.path.getsize(file_path) / (1024*1024), 2), 'name': file}
        file_list.append(dic)
    data = json.dumps(file_list, ensure_ascii=False)
    return data


def get_files_extension_json():
    files = os.listdir('./upload')
    ex_dic = {}
    ex_list = []
    num_list = []
    dic = {}
    for file in files:
        exten = os.path.splitext(file)[1].replace('.', '')
        if exten == '':
            exten = 'file'
        if exten in dic:
            dic[exten] += 1
        else:
            dic[exten] = 1
    for key in dic.keys():
        ex_list.append(key)
        num_list.append(dic[key])
    ex_dic['exten'] = ex_list
    ex_dic['num'] = num_list
    return json.dumps(ex_dic, ensure_ascii=False)



