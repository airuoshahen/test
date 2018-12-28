import matplotlib.patches as patches
import matplotlib.pyplot as plt
import time

import numpy as np
from matplotlib.legend import Legend

sendMsgId = 0
pointCnt = 5
maxPoint = 10
col = ['bo', 'ro', 'go', 'co', 'mo', 'yo', 'ko', 'wo']
class TagData:
    _idx = 0
    def __init__(self, tagId):
        self.locs = []
        self.idx = TagData._idx
        self.id = tagId
        self.leftCnt = 100
        self.col = col[self.idx % len(col)]
        TagData._idx += 1

    def update(self, loc):
        self.locs.insert(0, loc)
        if len(self.locs) > maxPoint:
            self.locs.pop()

    def std(self):
        a = np.array(self.locs)
        return np.std(a, axis=0)

class TagDataDict(dict):

    def getTagData(self, tagId):
        if tagId in self:
            ret = self[tagId]
            ret.leftCnt -= 1
            # if ret.leftCnt <= 0:
            #     del self[tagId]
            return ret
        ret = TagData(tagId)
        self[tagId] = ret
        return ret

    def clear(self):
        toDel = filter(lambda k: self[k].leftCnt <= 0, self.keys())
        for k in toDel:
            del self[k]

class LocFig:
    def __init__(self, plt, tagDatas):
        self.plt = plt
        self.plt.close()
        self.plt.ion()
        self.fig = plt.figure()
        self.bgax = self.fig.add_subplot(1,1,1)
        self.tagDatas = tagDatas
        self.xyFormat = '{0:.2f}'

    def draw(self):
        self.bgax.clear()
        self.bgax.grid(True)
        self.bgax.axis("equal")
        self.bgax.axis([-25, 25, -20, 20])
        self.bgax.add_patch(patches.Rectangle((-0.147, -0.179), 0.294, 0.358))
        for tagId in self.tagDatas:
            tagData = self.tagDatas.getTagData(tagId)
            x = list(map(lambda xy: xy[0], tagData.locs[-pointCnt:]))
            y = list(map(lambda xy: xy[1], tagData.locs[-pointCnt:]))
            label = tagData.std()
            label = list(map(lambda x: str(self.xyFormat.format(x)), label))
            self.bgax.plot(x, y, tagData.col, alpha = 0.7, label=str(tagId)+" ["+ ' '.join(label) + "]")
            self.bgax.text(x[0]+0.2,y[0]+0.2,[self.xyFormat.format(x[0]), self.xyFormat.format(y[0])])
        #self.bgax.legend()
        self.plt.pause(0.01)

class DisplayLoc:

    tagDatas = TagDataDict()
    fig = False
    def get_fig(self):
        if not self.fig:
            self.fig = LocFig(plt, self.tagDatas)
        return self.fig

    def display_forever(self, interval = 0.2):
        self.get_fig()
        while True:
            self.display_once()
            time.sleep(interval)

    def display_once(self):
        self.get_fig()
        self.fig.draw()
        self.fig.plt.pause(0.01)

    def update(self, tagId, xyz):
        self.tagDatas.getTagData(tagId).update(xyz)

class PhaseFig:
    def __init__(self):
        self.plt = plt
        self.plt.close()
        self.plt.ion()
        self.fig = plt.figure()
        self.plots = []
        self.format = '{0:.2f}'
        for i in range(1, 5):
            subp = self.fig.add_subplot(2, 2, i)
            # legend = Legend(padding=10, align="ur")
            # legend.plots = subp
            # subp.overlays.append(legend)
            self.plots.append(self.fig.add_subplot(2, 2, i))


    def to_180_180(self, phase):
        while phase > 180:
            phase -= 360
        while phase <= -180:
            phase += 360
        return phase

    his_stds = [[], [], []]
    def draw(self, datas, fixes):
        if len(datas) < 3 or len(fixes) < 3:
            return

        tmps = []
        stds = []
        ave_stds = []
        for i in range(len(datas)):
            tmp = list(map(lambda x: self.to_180_180(x + fixes[i]), datas[i]))
            std = np.std(tmp, ddof=1)
            stds.append(std)
            tmps.append(tmp)

        for j in range(3):
            self.his_stds[j].append(stds[j])
            if len(self.his_stds[j]) > 10:
                self.his_stds[j].pop(0)
            ave_stds.append(np.std(self.his_stds[j], ddof=1))

        for i in range(3):
            plot = self.plots[i]
            plot.clear()
            data = tmps[i]
            plot.plot(range(len(data)), data, 'o')
        self.plots[3].clear()
        self.plots[3].text(0.1, 0.8, ["stds:"])
        self.plots[3].text(0.2, 0.7, list(map(self.format.format, stds)))
        self.plots[3].text(0.1, 0.6, ["stds of stds:"])
        self.plots[3].text(0.2, 0.5, list(map(self.format.format, ave_stds)))
        self.plots[3].text(0.1, 0.2, ["fixes", fixes])
        self.plt.pause(0.01)


if __name__ == '__main__':
    print("test display")
    display = DisplayLoc()
    for i in range(1000):
        display.update(123, [i, i, i])
        display.display_once()
        time.sleep(0.5)

