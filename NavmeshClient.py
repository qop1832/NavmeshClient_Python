import socket
import struct
import json


class MessageType:
    PATH = 0
    MOVE_ALONG_SURFACE = 1
    RANDOM_POINT = 2
    RANDOM_POINT_AROUND = 3
    CAST_RAY = 4
    RANDOM_PATH = 5


class WorldPoint:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class AnTcpClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    def connect(self):
        try:
            self.client_socket.connect((self.ip, self.port))
            self.connected = True
        except Exception:
            raise Exception(f"无法连接: {self.ip}:{self.port}")

    def send(self, msg_type, map_id, start, end, flags=4):
        if not self.connected:
            return []
        # 验证坐标有效性
        if not self._validate_coordinates(start) or not self._validate_coordinates(end):
            raise ValueError("Invalid coordinates provided")

        request = self._build_request(msg_type, map_id, start, end, flags)
        self.client_socket.send(request)
        response = self._receive_response()
        return self._parse_response(response)

    def _receive_response(self):
        # 接收响应
        # 接收第一条数据: 数据包含第二条数据的长度并转成整数,长度为4字节.
        data_len = int.from_bytes(self.client_socket.recv(4), byteorder='big')
        # 接收第二条数据: 数据包含计算好的路径及坐标,长度信息在第一条数据里.
        response = self.client_socket.recv(data_len)
        return response

    @staticmethod
    def _validate_coordinates(coordinates):
        # 假设有效坐标范围是 -10000 到 10000，根据实际情况修改
        return all(-10000 <= coord <= 10000 for coord in coordinates)

    @staticmethod
    def _build_request(msg_type, map_id, start, end, flags):
        # 构建要发送的数据,把数据转成相应类型的二进制.
        if msg_type == 0:
            msg_type_bytes = struct.pack("i", msg_type)
        else:
            msg_type_bytes = struct.pack("!i", msg_type)

        map_id_bytes = struct.pack("i", map_id)
        flags_bytes = struct.pack("i", flags)

        start_bytes = struct.pack("fff", *start)
        end_bytes = struct.pack("fff", *end)

        if msg_type in (MessageType.PATH, MessageType.RANDOM_PATH):
            request = msg_type_bytes + map_id_bytes + flags_bytes + start_bytes + end_bytes
        else:
            request = msg_type_bytes + map_id_bytes + start_bytes + end_bytes

        data_length = len(request)

        # 将长度编码为一个字节，并添加到数据的前面
        length_byte = bytes([data_length])
        result_data = length_byte + request

        return result_data

    @staticmethod
    def _parse_response(response):
        # 去掉第一个字节, 第一个字节=消息类型
        try:
            data = list(struct.unpack(f'{len(response[1:]) // 4}f', response[1:]))
        except struct.error as e:
            print(f"解包数据时出错: {e}")
            return []

        # 格式化数据
        # formatted_data = [f"{data[i]:.4f},{data[i + 1]:.4f},{data[i + 2]:.4f}" for i in range(0, len(data), 3)]

        formatted_data = [f"{data[i]},{data[i + 1]},{data[i + 2]}" for i in range(0, len(data), 3)]

        # 使用竖线分隔坐标点
        result = "|".join(formatted_data)

        path = result.split("|")
        if not path or path == ["0.0,0.0,0.0"] or path == ['']:
            return []

        ret = []
        for p in path:
            tmp = p.split(",")
            w = WorldPoint(float(tmp[0]), float(tmp[1]), float(tmp[2]))
            ret.append({"x": w.x, "y": w.y, "z": w.z})
        json_data = json.dumps(ret)
        return json_data


if __name__ == "__main__":

    """
        命令行格式：navmeshClient.exe MessageType mapId x1 y1 z1 x2 y2 z2 flags
        MessageType可取值：
                PATH,
                MOVE_ALONG_SURFACE,
                RANDOM_POINT,
                RANDOM_POINT_AROUND, # 用不了,可能调用方式有问题 , 服务器报错 : 无法调用 findRandomPointAroundCircle: 2147483656
                CAST_RAY,            # 不知道有什么用,总是返回 空数据
                RANDOM_PATH,
        flags取值：
            0：普通
            1：Chaikin曲线算法
            2：CatmullRom插值算法
            4：FIND_LOCATION        
    """

    ip = "127.0.0.1"
    port = 47110
    client = AnTcpClient(ip, port)

    try:
        client.connect()
    except Exception as e:
        raise Exception(f"无法连接: {ip}:{port} ({e}")

    start = (-9919.75, 69.56018829345703, 34.426273345947266)
    end = (-8779.5537109375, -2579.640625, 132.49649047851562)

    msg_type = MessageType.PATH
    map_id = 0
    flags = 1
    while True:
        path = client.send(msg_type, map_id, start, end)
        print(path)
