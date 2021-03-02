# coding:utf-8
from fdfs_client.client import Fdfs_client


def storage(image_data):
    """上传图片接口，对接文件存储服务/系统，此处使用FastDFS
    :param image_data: 图片二进制数据
    :return: fdfs生成的Remote file_id
    """

    # 上传图片到fdfs
    client = Fdfs_client(
        '/home/python/.virtualenvs/ihome/ihome/ihome/utils/fdfs/client.conf')  # 必须传入绝对路径
    ret = client.upload_by_buffer(image_data)
    if ret.get('Status') != 'Upload successed.':
        raise Exception(u'上传图片到FastDFS失败')

    # 返回
    return ret.get('Remote file_id')
