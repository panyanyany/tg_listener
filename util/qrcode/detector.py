# -*- coding=utf-8 -*-
import os
import cv2
import numpy as np
import copy

img_path = 'images'
img_result = 'results'


def reshape_image(image):
    '''归一化图片尺寸：短边400，长边不超过800，短边400，长边超过800以长边800为主'''
    width, height = image.shape[1], image.shape[0]
    min_len = width
    scale = width * 1.0 / 400
    new_width = 400
    new_height = int(height / scale)
    if new_height > 800:
        new_height = 800
        scale = height * 1.0 / 800
        new_width = int(width / scale)
    out = cv2.resize(image, (new_width, new_height))
    return out


def detecte(image):
    '''提取所有轮廓'''
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)
    contours, hierachy = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return image, contours, hierachy


def compute_1(contours, i, j):
    '''最外面的轮廓和子轮廓的比例'''
    area1 = cv2.contourArea(contours[i])
    area2 = cv2.contourArea(contours[j])
    if area2 == 0:
        return False
    ratio = area1 * 1.0 / area2
    if abs(ratio - 49.0 / 25):
        return True
    return False


def compute_2(contours, i, j):
    '''子轮廓和子子轮廓的比例'''
    area1 = cv2.contourArea(contours[i])
    area2 = cv2.contourArea(contours[j])
    if area2 == 0:
        return False
    ratio = area1 * 1.0 / area2
    if abs(ratio - 25.0 / 9):
        return True
    return False


def compute_center(contours, i):
    '''计算轮廓中心点'''
    M = cv2.moments(contours[i])
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    return cx, cy


def detect_contours(vec):
    '''判断这个轮廓和它的子轮廓以及子子轮廓的中心的间距是否足够小'''
    distance_1 = np.sqrt((vec[0] - vec[2]) ** 2 + (vec[1] - vec[3]) ** 2)
    distance_2 = np.sqrt((vec[0] - vec[4]) ** 2 + (vec[1] - vec[5]) ** 2)
    distance_3 = np.sqrt((vec[2] - vec[4]) ** 2 + (vec[3] - vec[5]) ** 2)
    if sum((distance_1, distance_2, distance_3)) / 3 < 3:
        return True
    return False


def juge_angle(rec):
    '''判断寻找是否有三个点可以围成等腰直角三角形'''
    if len(rec) < 3:
        return -1, -1, -1
    for i in range(len(rec)):
        for j in range(i + 1, len(rec)):
            for k in range(j + 1, len(rec)):
                distance_1 = np.sqrt((rec[i][0] - rec[j][0]) ** 2 + (rec[i][1] - rec[j][1]) ** 2)
                distance_2 = np.sqrt((rec[i][0] - rec[k][0]) ** 2 + (rec[i][1] - rec[k][1]) ** 2)
                distance_3 = np.sqrt((rec[j][0] - rec[k][0]) ** 2 + (rec[j][1] - rec[k][1]) ** 2)
                if abs(distance_1 - distance_2) < 5:
                    if abs(np.sqrt(np.square(distance_1) + np.square(distance_2)) - distance_3) < 5:
                        return i, j, k
                elif abs(distance_1 - distance_3) < 5:
                    if abs(np.sqrt(np.square(distance_1) + np.square(distance_3)) - distance_2) < 5:
                        return i, j, k
                elif abs(distance_2 - distance_3) < 5:
                    if abs(np.sqrt(np.square(distance_2) + np.square(distance_3)) - distance_1) < 5:
                        return i, j, k
    return -1, -1, -1


def find(contours, hierachy):
    '''找到符合要求的轮廓'''
    rec = []
    for i in range(len(hierachy)):
        child = hierachy[i][2]
        child_child = hierachy[child][2]
        if child != -1 and hierachy[child][2] != -1:
            if compute_1(contours, i, child) and compute_2(contours, child, child_child):
                cx1, cy1 = compute_center(contours, i)
                cx2, cy2 = compute_center(contours, child)
                cx3, cy3 = compute_center(contours, child_child)
                if detect_contours([cx1, cy1, cx2, cy2, cx3, cy3]):
                    rec.append([cx1, cy1, cx2, cy2, cx3, cy3, i, child, child_child])
    '''计算得到所有在比例上符合要求的轮廓中心点'''
    i, j, k = juge_angle(rec)
    if i == -1 or j == -1 or k == -1:
        return
    return True


def find0(image, image_name, contours, hierachy, root=0):
    '''找到符合要求的轮廓'''
    rec = []
    for i in range(len(hierachy)):
        child = hierachy[i][2]
        child_child = hierachy[child][2]
        if child != -1 and hierachy[child][2] != -1:
            if compute_1(contours, i, child) and compute_2(contours, child, child_child):
                cx1, cy1 = compute_center(contours, i)
                cx2, cy2 = compute_center(contours, child)
                cx3, cy3 = compute_center(contours, child_child)
                if detect_contours([cx1, cy1, cx2, cy2, cx3, cy3]):
                    rec.append([cx1, cy1, cx2, cy2, cx3, cy3, i, child, child_child])
    '''计算得到所有在比例上符合要求的轮廓中心点'''
    i, j, k = juge_angle(rec)
    if i == -1 or j == -1 or k == -1:
        return
    ts = np.concatenate((contours[rec[i][6]], contours[rec[j][6]], contours[rec[k][6]]))
    rect = cv2.minAreaRect(ts)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    result = copy.deepcopy(image)
    cv2.drawContours(result, [box], 0, (0, 0, 255), 2)
    cv2.drawContours(image, contours, rec[i][6], (255, 0, 0), 2)
    cv2.drawContours(image, contours, rec[j][6], (255, 0, 0), 2)
    cv2.drawContours(image, contours, rec[k][6], (255, 0, 0), 2)
    cv2.imshow('img', image)
    cv2.waitKey(0)
    cv2.imshow('img', result)
    cv2.waitKey(0)
    path = os.path.join(img_result, image_name)
    cv2.imwrite(path, result)
    return


if __name__ == '__main__':
    files = os.listdir(img_path)
    for file in files:
        image = cv2.imread(os.path.join(img_path, file))
        image = reshape_image(image)
        cv2.imshow('img', image)
        cv2.waitKey(0)
        image, contours, hierachy = detecte(image)
        find(image, file, contours, np.squeeze(hierachy))
