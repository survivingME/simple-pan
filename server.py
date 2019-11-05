#!/usr/bin/env python
# coding=utf-8

import os
import utils

from flask import Flask, request, Response, redirect, render_template as rt

app = Flask(__name__)


@app.route('/get_pie_file_size_data')
def get_pie_file_size_data():
    data = utils.get_files_size_json()
    return data


@app.route('/get_bar_file_exten_data')
def get_bar_file_exten_data():
    data = utils.get_files_extension_json()
    return data


def new_dir():
    if not os.path.exists('./upload'):
        try:
            os.mkdir("./upload/")
        except Exception as e:
            print("make dir error, ", e)


@app.route('/file/upload', methods=['POST'])
def upload_part():  # 接收前端上传的一个分片
    task = request.form.get('task_id')  # 获取文件的唯一标识符
    chunk = request.form.get('chunk', 0)  # 获取该分片在所有分片中的序号
    filename = '%s%s' % (task, chunk)  # 构造该分片的唯一标识符

    upload_file = request.files['file']
    upload_file.save('./upload/%s' % filename)  # 保存分片到本地
    return rt('./index.html')


@app.route('/file/merge', methods=['GET'])
def upload_success():  # 按序读出分片内容，并写入新文件
    target_filename = request.args.get('filename')  # 获取上传文件的文件名
    task = request.args.get('task_id')  # 获取文件的唯一标识符
    chunk = 0  # 分片序号
    with open('./upload/%s' % target_filename, 'wb') as target_file:  # 创建新文件
        while True:
            try:
                filename = './upload/%s%d' % (task, chunk)
                source_file = open(filename, 'rb')  # 按序打开每个分片
                target_file.write(source_file.read())  # 读取分片内容写入新文件
                source_file.close()
            except IOError as msg:
                break

            chunk += 1
            os.remove(filename)  # 删除该分片，节约空间

    return rt('./index.html')


@app.route('/dir', methods=['POST'])
def make_dir():
    dir_name = request.form.get('dir_name')
    print(dir_name)
    pre = './upload/'
    try:
        os.mkdir(pre + dir_name)
    except Exception as e:
        #todo
        print("make new dir error, ", e)
    return rt('./index.html')


@app.route('/', methods=['GET'])
def file_list():
    files = os.listdir('./upload/')  # 获取文件目录
    files_and_size = {}
    for file in files:
        file_abs = './upload/' + file
        file_and_size = []
        if not isinstance(file_abs, str):
            file_abs.decode('utf-8')
        if not file == "None":
            file_and_size.append(file_abs)
            file_and_size.append(utils.get_file_size(file_abs))
            file_and_size.append(utils.get_file_create_time(file_abs))
            files_and_size[file] = file_and_size
    return rt('./list.html', files_and_size=files_and_size)


@app.route('/file/rename', methods=['POST'])
def rename():
    try:
        orig = request.form['orig']
        path = request.form['path']
        new_name = request.form['new_name']
        new_path = path.replace(orig, new_name)
        os.rename(path, new_path)
    except Exception as e:
        print("rename failed, ", e)
    return redirect('/file/list')

'''
@app.route('/file/list/<path:dirname>', methods=['GET'])
def dir_file_list(dirname):
    files = os.listdir('./' + dirname + '/')
    files_and_size = {}
    for file in files:
        file_abs = './upload/' + dirname + '/' + file
        file_and_size = []
        if not isinstance(file_abs, str):
            file_abs.decode('utf-8')
        if not file == "None":
            file_and_size.append(file_abs)
            file_and_size.append(utils.get_file_size(file_abs))
            file_and_size.append(utils.get_file_create_time(file_abs))
            files_and_size[file] = file_and_size
    return rt('./list.html', files_and_size=files_and_size)
'''


@app.route('/file/download/<path:filename>', methods=['GET'])
def file_download(filename):
    def send_chunk():  # 流式读取
        store_path = filename
        with open(store_path, 'rb') as target_file:
            while True:
                chunk = target_file.read(20 * 1024 * 1024)
                if not chunk:
                    break
                yield chunk

    return Response(send_chunk(), content_type='application/octet-stream')


@app.route('/file/delete/<path:filename>', methods=['GET'])
def file_delete(filename):
    if os.path.exists(filename):
        if os.path.isfile(filename):
            os.remove(filename)
        else:
            #todo: forend show noti
            print('not a file')
    else:
        #todo: forend show noti
        print('path not exist')
    return redirect('/file/list')


if __name__ == '__main__':
    app.run(debug=False, threaded=True)
