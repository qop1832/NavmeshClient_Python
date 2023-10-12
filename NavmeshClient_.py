import subprocess
import time
"""
    命令行格式：navmeshClient.exe MessageType mapId x1 y1 z1 x2 y2 z2 flags
    MessageType可取值：
            PATH,
            MOVE_ALONG_SURFACE,
            RANDOM_POINT,
            RANDOM_POINT_AROUND,
            CAST_RAY,
            RANDOM_PATH,
    flags取值：
        0：普通
        1：Chaikin曲线算法
        2：CatmullRom插值算法
        4：FIND_LOCATION        
"""


class WorldPoint:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class NavmeshClient:
    def __init__(self):
        self.exe = "navmeshClient.exe"
        # start = WorldPoint(10344.6591796875, -6301.26611328125, 25.01284408569336)
        # to = WorldPoint(9497.625, -6821.7578125, 16.492191314697266)
        #
        # print("开始加载地图数据，可能需要1-2分钟时间，请等待。。。。。。。。。。")
        # print("开始加载 东部王国 地图数据,mapId=0 。。。。。。")
        # self.getPath(0, start, to, flags=0)
        # print("开始加载 卡利姆多 地图数据,mapId=1 。。。。。。")
        # self.getPath(1, start, to, flags=0)
        # print("地图数据加载完成")

    def getPath(self, mapId, fromPos, toPos, type="CAST_RAY", flags=0):
        fromStr = str(fromPos.x) + " " + str(fromPos.y) + " " + str(fromPos.z)
        toStr = str(toPos.x) + " " + str(toPos.y) + " " + str(toPos.z)
        cmd = self.exe + " " + type + " " + str(mapId) + " " + fromStr + " " + toStr + " " + str(flags)
        pi = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0]
        pi = pi.decode()
        if "can not connect to:127.0.0.1:47110" in pi:
            return []

        path = pi.split("|")
        if path == "" or path is None or path == ["0,0,0"]:
            return []

        ret = []
        for p in path:
            tmp = p.split(",")
            w = WorldPoint(float(tmp[0]), float(tmp[1]), float(tmp[2]))
            ret.append({"x": w.x, "y": w.y, "z": w.z})
        return ret


if __name__ == '__main__':
    map = NavmeshClient()
    #while True:
    start = WorldPoint(-9919.75, 69.56018829345703, 34.426273345947266)
    to = WorldPoint(-8779.5537109375, -2579.640625, 132.49649047851562)
    a = map.getPath(0, start, to)
    print(a)
        #time.sleep(.005)


