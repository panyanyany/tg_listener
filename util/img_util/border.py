import os

import cv2
import numpy as np
from io import BytesIO
import base64
from PIL import Image


class BorderRm:
    def nms(self, boxes, overlap=0.8):
        boxes = [[i[0], i[2], i[1], i[3], s] for i, s in boxes.lp_addresses()]
        boxes = sorted(boxes, key=lambda N: N[4])
        if not boxes:
            pick = []
        else:
            trial = np.zeros((len(boxes), 5), dtype=np.float32)
            trial[:] = boxes[:]
            x1 = trial[:, 0]
            y1 = trial[:, 1]
            x2 = trial[:, 2]
            y2 = trial[:, 3]
            score = trial[:, 4]
            area = (x2 - x1 + 1) * (y2 - y1 + 1)

            I = np.argsort(score)
            pick = []
            while (I.size != 0):
                last = I.size
                i = I[last - 1]
                pick.append(i)
                suppress = [last - 1]
                for pos in range(last):
                    j = I[pos]
                    xx1 = max(x1[i], x1[j])
                    yy1 = max(y1[i], y1[j])
                    xx2 = min(x2[i], x2[j])
                    yy2 = min(y2[i], y2[j])
                    w = xx2 - xx1 + 1
                    h = yy2 - yy1 + 1
                    if (w > 0 and h > 0):
                        o = w * h / max(area[i], area[j])
                        if (o > overlap):
                            if pos != i:
                                boxes[i][4] += boxes[pos][4]
                            suppress.append(pos)
                I = np.delete(I, suppress)
        newBox = []
        for i in pick:
            newBox.append(boxes[i])
        newBox = sorted(newBox, key=lambda N: N[4], reverse=True)

        return newBox[0][:4]

    def remove_border_imgs(self, imgs):
        borders = {}
        for img in imgs:
            img = Image.open(BytesIO(base64.b64decode(img))).convert("RGB")
            img = img.convert('RGB')
            im = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            (x1, x2), (y1, y2) = self.sobel(im)
            if (x1, x2, y1, y2) not in borders:
                borders[(x1, x2, y1, y2)] = 1
            else:
                borders[(x1, x2, y1, y2)] += 1
        x1, y1, x2, y2 = self.nms(borders)
        return x1, y1, x2, y2

    def detectBorder(self, im, ori, width, length, side):
        border = {}
        if side == 'X':
            im = im.T
            ori = ori.T

        for i, ix in enumerate(im):
            border[i] = (np.sum(ix) * 0.003921568627451, np.sum(ori[i]) * 0.003921568627451)

        border = self.checkborder(border, width, length, side)
        return border

    def checkborder(self, border, width, length, side):
        border = [(k, border[k]) for k in sorted(border.keys())]
        Nborder = []
        colorSum = 0
        for i in range(int(length * 0.375)):
            colorSum += border[i][1][1] + border[length - i - 1][1][1]
            Nborder.append((i, border[i][1][0] + border[length - i - 1][1][0], colorSum))

        res = sorted(Nborder, key=lambda N: N[1], reverse=True)[0]

        cw = res[0]
        Bvalue = res[1] * 0.5
        Cvalue = res[2] * 0.5 / (cw + 1)
        if side == 'Y':
            B = 0.30
            C = 0.40
        else:
            B = 0.40
            C = 0.40
        if Bvalue < width * B or (Cvalue > width * C and Cvalue < width * (1 - C)):
            cw = 0
        return cw, length - cw

    def sobel(self, img):
        imgh, imgw = img.shape
        hist = cv2.calcHist([img], [0], None, [256], [0.0, 255.0])
        hist = [int(v[0]) for i, v in enumerate(hist.tolist())]
        std = np.std(np.array(hist))
        if std < 1024:
            return (0, imgw), (0, imgh)

        th, img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)

        x = cv2.Sobel(img, cv2.CV_16S, 1, 0)
        y = cv2.Sobel(img, cv2.CV_16S, 0, 1)

        absX = cv2.convertScaleAbs(x)
        absY = cv2.convertScaleAbs(y)

        Yborder = self.detectBorder(absY, img, imgw, imgh, 'Y')
        absX = absX[Yborder[0]:Yborder[1], :]
        img = img[Yborder[0]:Yborder[1], :]
        Xborder = self.detectBorder(absX, img, Yborder[1] - Yborder[0], imgw, 'X')
        return Xborder, Yborder


def rm_border(img_path, save_path=None):
    """去黑边, 即使黑边上有水印干扰也能去"""
    BR = BorderRm()
    with open(img_path, 'rb') as fp:
        content = base64.b64encode(fp.read())

    img: Image.Image = Image.open(img_path)
    raw_w, raw_h = img.size
    size = BR.remove_border_imgs([content])
    w0, h0, w1, h1 = size
    span = 2
    if raw_w != w1:
        w0 += span
        w1 -= span
    if raw_h != h1:
        h0 += span
        h1 += span

    size = (w0, h0, w1, h1)
    img = img.crop(size)

    if not save_path:
        name, ext = os.path.splitext(img_path)
        save_path = '%s.cut%s' % (name, ext)
    img.save(save_path, optimize=True)
    return save_path


if __name__ == '__main__':
    BR = BorderRm()
    import requests as req

    # url = 'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1539943879975&di=7a0db77b3ad4dbd171b8b3c6ac1804b5&imgtype=0&src=http%3A%2F%2Fwww.guangyuanol.cn%2Fuploads%2Fallimg%2F170430%2F21525H143-0.jpg'
    # response = req.get(url)
    rm_border('storage/tmp/rm-01.jpeg')
    rm_border('storage/tmp/万磁王的4个儿女，第3火遍各种小视频网站，是很多人心头爱.jpg')
