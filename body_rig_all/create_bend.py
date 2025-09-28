# -*- coding: UTF-8 -*-

'''
import sys

absolute_path = "C:/Users/meidm/Desktop/body_rig_all/create_bend_all"
sys.path.append(absolute_path)

import create_bend
import importlib
importlib.reload(create_bend)
create_bend.main_arm()
create_bend.main_leg()
'''

import maya.cmds as cmds
import math

def createNodehijt(n, name, parent, num, flag):
    for i in range(num):
        o = cmds.createNode('transform', n=name + '_offset', p=parent)
        cp = cmds.createNode('transform', n=name + '_ctrlSpace', p=o)
        c = cmds.createNode('transform', n=name + '_ctrl', p=cp)
        cmds.matchTransform(o, n, piv=True, pos=True, rot=True)
        
        if flag==0:
            cmds.parent(n, c)
    return(o, cp, c)
        
def create_joint(src_joint, new_joint_name):
    # ジョイントの位置を取得
    position = cmds.xform(src_joint, query=True, translation=True, worldSpace=True)
    
    # ジョイントのワールド座標での回転を取得
    rotation = cmds.xform(src_joint, query=True, rotation=True, worldSpace=True)

    # 同じ位置で新しいジョイントを作成
    new_joint = cmds.joint(name=new_joint_name, position=position)
    
    # 新しいジョイントのワールド座標での回転を設定
    cmds.xform(new_joint, rotation=rotation, worldSpace=True)

    return new_joint

def create_joints_between(start_joint, end_joint, bend_joint, num_joints, j):
    # スタートとエンドのジョイントの位置を取得
    start_pos = cmds.xform(start_joint, query=True, worldSpace=True, translation=True)
    end_pos = cmds.xform(end_joint, query=True, worldSpace=True, translation=True)

    # 間隔を計算
    dx = (end_pos[0] - start_pos[0]) / (num_joints - 1)
    dy = (end_pos[1] - start_pos[1]) / (num_joints - 1)
    dz = (end_pos[2] - start_pos[2]) / (num_joints - 1)

    # ジョイントの配置
    x = start_pos[0] + dx * j
    y = start_pos[1] + dy * j
    z = start_pos[2] + dz * j
    position=(x, y, z)
    cmds.xform(bend_joint, translation=(x, y, z), worldSpace=True)
    
def freeze_rotation(joints):
    for joint in joints:
        cmds.makeIdentity(joint, apply=True, rotate=True)
        
def set_joint_color(joint_name, color):
    # ジョイントの表示オーバーライドを有効にする
    cmds.setAttr(joint_name + '.overrideEnabled', 1)
    cmds.setAttr(joint_name + '.overrideRGBColors', 1)
    cmds.setAttr(joint_name + '.useOutlinerColor', 1)

    # RGB値で色を設定（値は0から1の範囲）
    cmds.setAttr(joint_name + '.overrideColorRGB', color[0], color[1], color[2])
    cmds.setAttr(joint_name + '.outlinerColor', color[0], color[1], color[2])
    
def lock_attr(node, *attrs):
    #アトリビュートをロックする。
    for attr in attrs:
        cmds.setAttr('{}.{}'.format(node, attr), lock=True, keyable=False, channelBox=False)

def bend_joint(num, upjoint, lojoint, endjoint, upper, bend_joint_num):
    part = num #L is 76. R is 82.
    start_joint = 'ble_' + upjoint + '_jt_' + chr(part)
    end_joint = 'ble_' + lojoint + '_jt_' + chr(part)
    bend_j_n = bend_joint_num #4~10
    gp = cmds.createNode('transform', n=chr(part) + '_' + upjoint + '_micro_ctrl_grp')
    set_joint_color(gp, [1, 0.44, 0.7])  # ピンクに近い色
    for j in range(bend_j_n):
        upbend_joint = create_joint('ble_' + upjoint + '_jt_' + chr(part), chr(part) + '_up' + upper + '_bendy_' + str(j+1) + '_drvjnt')
        cmds.setAttr(upbend_joint + '.radius', 0.2)#
        lobend_joint = create_joint('ble_' + lojoint + '_jt_' + chr(part), chr(part) + '_lo' + upper + '_bendy_' + str(j+1) + '_drvjnt')
        cmds.setAttr(lobend_joint + '.radius', 0.2)#
        create_joints_between('ble_' + upjoint + '_jt_' + chr(part), 'ble_' + lojoint + '_jt_' + chr(part), upbend_joint, bend_j_n, j)
        create_joints_between('ble_' + lojoint + '_jt_' + chr(part), 'ble_' + endjoint + '_jt_' + chr(part), lobend_joint, bend_j_n, j)
        freeze_rotation([upbend_joint, lobend_joint])
        up = createNodehijt(upbend_joint, chr(part) + '_up' + upper + '_micro_' + str(j+1), None, 1, 0)
        lo = createNodehijt(lobend_joint, chr(part) + '_lo' + upper + '_micro_' + str(j+1), None, 1, 0)
        cmds.parent(up[0], lo[0], gp)
        set_joint_color(upbend_joint, [1, 1, 0.4])  # 黄色に近い色
        set_joint_color(lobend_joint, [1, 1, 0.4])  # 黄色に近い色
        cmds.select(cl=True) #これをしないと、ここのジョイントを選択した状態で次に行ってしまう。
        
def bend_main_joint(num, upjoint, lojoint, endjoint, upper):
    part = num #L is 76. R is 82.
    start_joint = 'ble_' + upjoint + '_jt_' + chr(part)
    end_joint = 'ble_' + lojoint + '_jt_' + chr(part)
    bend2_joint_num = 3 #3, 5, 9
    for j in range(bend2_joint_num):
        upbend_joint = create_joint('ble_' + upjoint + '_jt_' + chr(part), chr(part) + '_up' + upper + '_bendy_main_' + str(j+1) + '_drvjnt')
        cmds.setAttr(upbend_joint + '.radius', 0.5)#
        lobend_joint = create_joint('ble_' + lojoint + '_jt_' + chr(part), chr(part) + '_lo' + upper + '_bendy_main_' + str(j+1) + '_drvjnt')
        cmds.setAttr(lobend_joint + '.radius', 0.5)#
        create_joints_between('ble_' + upjoint + '_jt_' + chr(part), 'ble_' + lojoint + '_jt_' + chr(part), upbend_joint, bend2_joint_num, j)
        create_joints_between('ble_' + lojoint + '_jt_' + chr(part), 'ble_' + endjoint + '_jt_' + chr(part), lobend_joint, bend2_joint_num, j)
        freeze_rotation([upbend_joint, lobend_joint])
        createNodehijt(upbend_joint, chr(part) + '_up' + upper + '_bendy_main_' + str(j+1), None, 1, 0)
        createNodehijt(lobend_joint, chr(part) + '_lo' + upper + '_bendy_main_' + str(j+1), None, 1, 0)
        set_joint_color(upbend_joint, [1, 0.5, 0])  # orange
        set_joint_color(lobend_joint, [1, 0.5, 0])  # orange
        cmds.select(cl=True) #これをしないと、ここのジョイントを選択した状態で次に行ってしまう。    
    
def calculate_distance(joint1, joint2):
    # ジョイントのワールド座標を取得
    pos1 = cmds.xform(joint1, query=True, worldSpace=True, translation=True)
    pos2 = cmds.xform(joint2, query=True, worldSpace=True, translation=True)

    # ユークリッド距離を計算
    distance = math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2 + (pos2[2] - pos1[2]) ** 2)
    return distance

def position_cv_to_joint(joint_root, joint_end, plane_shape, i, offset):
    # ジョイントの距離を計算
    distance = calculate_distance(joint_root, joint_end)

    # 指定された CV の位置をジョイントの位置に合わせる
    for j in range(4):
        cmds.setAttr(plane_shape + '.controlPoints[' + str(i + j) + '].xValue', distance - offset)

def set_cv_to_interpolated_position(plane_shape, cv1, cv2, cv_target, ratio):
    # 2つのジョイントの位置を取得して補間する
    for j in range(4):
        cv1_pos = cmds.getAttr(plane_shape + '.controlPoints[' + str(cv1 + j) + '].xValue')
        cv2_pos = cmds.getAttr(plane_shape + '.controlPoints[' + str(cv2 + j) + '].xValue')
        d = cv2_pos - cv1_pos
        point = cv1_pos + d * ratio
        cmds.setAttr(plane_shape + '.controlPoints[' + str(cv_target + j) + '].xValue', point)
        
# 距離測定ノードを作成
def create_mesure(start_name, end_name, mesure_name, upjoint, num):
    part = num
    start_point = cmds.createNode('locator', name=chr(part) + start_name + 'Shape')
    start_point_T = cmds.listRelatives(start_point, parent=True)[0]
    end_point = cmds.createNode('locator', name=chr(part) + end_name + 'Shape')
    end_point_T = cmds.listRelatives(end_point, parent=True)[0]
    
    distance_node = cmds.createNode('distanceDimShape', name=chr(part) + mesure_name + 'Shape')
    cmds.connectAttr(start_point + '.worldPosition[0]', distance_node + '.startPoint')
    cmds.connectAttr(end_point + '.worldPosition[0]', distance_node + '.endPoint')
    distance_node_T = cmds.listRelatives(distance_node, parent=True)[0]
    
    cmds.parent(start_point_T, end_point_T, distance_node_T, chr(num)+'_' + upjoint + '_distance_grp')
    
    return(start_point_T, end_point_T, distance_node, distance_node_T)

def create_follicles_on_surface(num_follicles, follicle_name_prefix, surface_name):
    '''
    指定されたNURBSサーフェスにフォリクルを生成する関数

    :param num_follicles: 生成するフォリクルの数
    :param follicle_name_prefix: フォリクルに付ける名前のプレフィックス
    :param surface_name: 操作するNURBSサーフェスの名前
    '''
    # フォリクルを生成
    for i in range(num_follicles):
        # フォリクルの作成
        follicleShape = cmds.createNode('follicle', name=follicle_name_prefix + 'Shape' + str(i))
        follicleTransform = cmds.listRelatives(follicleShape, parent=True)[0]
        cmds.rename(follicleTransform, follicle_name_prefix + str(i))

        # parameterU を等間隔に設定（フォリクルが1つの場合は中央に配置）
        if num_follicles == 1:
            parameterU = 0.5
        else:
            parameterU = float(i) / (num_follicles - 1)

        # フォリクルのパラメータを設定
        cmds.setAttr(follicleShape + '.parameterU', parameterU)
        cmds.setAttr(follicleShape + '.parameterV', 0.5)

        # フォリクルをNURBSサーフェスに接続
        cmds.connectAttr(surface_name + '.local', follicleShape + '.inputSurface')
        cmds.connectAttr(surface_name + '.worldMatrix[0]', follicleShape + '.inputWorldMatrix')
        cmds.connectAttr(follicleShape + '.outTranslate', follicleTransform + '.translate')
        cmds.connectAttr(follicleShape + '.outRotate', follicleTransform + '.rotate')
        
        if i == 0:
            cmds.createNode('transform', name=follicle_name_prefix + '_gp')
            cmds.parent(follicleTransform, follicle_name_prefix + '_gp')
        else:
            cmds.parent(follicleTransform, follicle_name_prefix + '_gp')
    
def create_nurbs(num, upjoint, lojoint, upper):
    part = num #L is 76. R is 82.
    
    # NURBS プレーンの作成
    upPlane = cmds.nurbsPlane(name=chr(part) + '_up' + upper + '_bendyRibbon_surf', width=1, lengthRatio=1, patchesU=3, patchesV=1, ax=(0,1,0))[0]
    # NURBSプレーンのピボットを移動
    cmds.move(-0.5, 0, 0, upPlane + '.scalePivot', upPlane + '.rotatePivot', relative=True)
    upPlane_shape = cmds.listRelatives(upPlane, pa = True)
    
    loPlane = cmds.nurbsPlane(name=chr(part) + '_lo' + upper + '_bendyRibbon_surf', width=1, lengthRatio=1, patchesU=3, patchesV=1, ax=(0,1,0))[0]
    # NURBSプレーンのピボットを移動
    cmds.move(-0.5, 0, 0, loPlane + '.scalePivot', loPlane + '.rotatePivot', relative=True)
    loPlane_shape = cmds.listRelatives(loPlane, pa = True)
    
    # ジョイントAの位置と回転をプレーンに合わせる
    up = 'ble_' + upjoint + '_jt_' + chr(part)
    lo = 'ble_' + lojoint + '_jt_' + chr(part)
    #cmds.matchTransform(upPlane, up)
    #cmds.matchTransform(loPlane, lo)
    
    if part == 76:
        cmds.matchTransform(upPlane, up)
        cmds.matchTransform(loPlane, lo)
    elif part == 82:
        cmds.matchTransform(upPlane, up)
        cmds.matchTransform(loPlane, lo)
        cmds.rotate(0,0,180, upPlane, r=True)
        cmds.rotate(0,0,180, loPlane, r=True)
    
    
    
    # 各ジョイントに対して CV を配置
    position_cv_to_joint(chr(part) + '_up' + upper + '_bendy_1_drvjnt', chr(part) + '_up' + upper + '_bendy_1_drvjnt', upPlane_shape[0], 0, 0)
    position_cv_to_joint(chr(part) + '_up' + upper + '_bendy_1_drvjnt', chr(part) + '_up' + upper + '_bendy_2_drvjnt', upPlane_shape[0], 8, 0.333)
    position_cv_to_joint(chr(part) + '_up' + upper + '_bendy_1_drvjnt', chr(part) + '_up' + upper + '_bendy_3_drvjnt', upPlane_shape[0], 12, 0.666)
    position_cv_to_joint(chr(part) + '_up' + upper + '_bendy_1_drvjnt', chr(part) + '_up' + upper + '_bendy_4_drvjnt', upPlane_shape[0], 20, 1)
    # CV[1][0:3] を [0][0:3] と [2][0:3] の間の 1/3 の位置に設定
    set_cv_to_interpolated_position(upPlane_shape[0], 0, 8, 4, 1.0/3.0)
    # CV[4][0:3] を [3][0:3] と [5][0:3] の間の 2/3 の位置に設定
    set_cv_to_interpolated_position(upPlane_shape[0], 12, 20, 16, 2.0/3.0)
    
    position_cv_to_joint(chr(part) + '_lo' + upper + '_bendy_1_drvjnt', chr(part) + '_lo' + upper + '_bendy_1_drvjnt', loPlane_shape[0], 0, 0)
    position_cv_to_joint(chr(part) + '_lo' + upper + '_bendy_1_drvjnt', chr(part) + '_lo' + upper + '_bendy_2_drvjnt', loPlane_shape[0], 8, 0.333)
    position_cv_to_joint(chr(part) + '_lo' + upper + '_bendy_1_drvjnt', chr(part) + '_lo' + upper + '_bendy_3_drvjnt', loPlane_shape[0], 12, 0.666)
    position_cv_to_joint(chr(part) + '_lo' + upper + '_bendy_1_drvjnt', chr(part) + '_lo' + upper + '_bendy_4_drvjnt', loPlane_shape[0], 20, 1)
    # CV[1][0:3] を [0][0:3] と [2][0:3] の間の 1/3 の位置に設定
    set_cv_to_interpolated_position(loPlane_shape[0], 0, 8, 4, 1.0/3.0)
    # CV[4][0:3] を [3][0:3] と [5][0:3] の間の 2/3 の位置に設定
    set_cv_to_interpolated_position(loPlane_shape[0], 12, 20, 16, 2.0/3.0)
    
    create_follicles_on_surface(4, chr(part) + '_' + upjoint + '_up_follicle', chr(part) + '_up' + upper + '_bendyRibbon_surf')
    create_follicles_on_surface(4, chr(part) + '_' + upjoint + '_lo_follicle', chr(part) + '_lo' + upper + '_bendyRibbon_surf')
    
    cmds.duplicate(upPlane, name = chr(part) + '_up' + upper + '_bendyRibbon_IKmid_surf')
    cmds.duplicate(loPlane, name = chr(part) + '_lo' + upper + '_bendyRibbon_IKmid_surf')
    create_follicles_on_surface(1, chr(part) + '_' + upjoint + '_up2_follicle', chr(part) + '_up' + upper + '_bendyRibbon_IKmid_surf')
    create_follicles_on_surface(1, chr(part) + '_' + upjoint + '_lo2_follicle', chr(part) + '_lo' + upper + '_bendyRibbon_IKmid_surf')


def create_nurbs2(num, upjoint, lojoint, upper, bend_joint_num):
    part = num #L is 76. R is 82.
    
    bend_j_n = bend_joint_num
    
    # NURBS プレーンの作成
    upPlane = cmds.nurbsPlane(name=chr(part) + '_up' + upper + '_bendyRibbon_surf', width=1, lengthRatio=1, patchesU=bend_j_n-1, patchesV=1, ax=(0,1,0))[0]
    # NURBSプレーンのピボットを移動
    cmds.move(-0.5, 0, 0, upPlane + '.scalePivot', upPlane + '.rotatePivot', relative=True)
    upPlane_shape = cmds.listRelatives(upPlane, pa = True)
    
    loPlane = cmds.nurbsPlane(name=chr(part) + '_lo' + upper + '_bendyRibbon_surf', width=1, lengthRatio=1, patchesU=bend_j_n-1, patchesV=1, ax=(0,1,0))[0]
    # NURBSプレーンのピボットを移動
    cmds.move(-0.5, 0, 0, loPlane + '.scalePivot', loPlane + '.rotatePivot', relative=True)
    loPlane_shape = cmds.listRelatives(loPlane, pa = True)
    
    # ジョイントAの位置と回転をプレーンに合わせる
    up = 'ble_' + upjoint + '_jt_' + chr(part)
    lo = 'ble_' + lojoint + '_jt_' + chr(part)
    #cmds.matchTransform(upPlane, up)
    #cmds.matchTransform(loPlane, lo)
    
    if part == 76:
        cmds.matchTransform(upPlane, up)
        cmds.matchTransform(loPlane, lo)
    elif part == 82:
        cmds.matchTransform(upPlane, up)
        cmds.matchTransform(loPlane, lo)
        cmds.rotate(0,0,180, upPlane, r=True, fo=True, os=True)
        cmds.rotate(0,0,180, loPlane, r=True, fo=True, os=True)
        print('binbin')
    
    
    
    # 各ジョイントに対して CV を配置
    last_cv = 4*(bend_j_n+1)
    
    for n in range(bend_j_n):
        up_start = chr(part) + '_up' + upper + '_bendy_1_drvjnt'
        up_end = chr(part) + '_up' + upper + '_bendy_' + str(n+1) + '_drvjnt'
        
        div = 1/(bend_j_n-1) * n
        
        if n == 0:
            position_cv_to_joint(up_start, up_end, upPlane_shape[0], 0, 0)
        elif n + 1 == bend_j_n:
            position_cv_to_joint(up_start, up_end, upPlane_shape[0], last_cv, 1)
        else:
            position_cv_to_joint(up_start, up_end, upPlane_shape[0], 8 + 4*(n-1), div)
        

    # CV[1][0:3] を [0][0:3] と [2][0:3] の間の 1/3 の位置に設定
    set_cv_to_interpolated_position(upPlane_shape[0], 0, 8, 4, 1.0/3.0)
    # CV[4][0:3] を [3][0:3] と [5][0:3] の間の 2/3 の位置に設定
    set_cv_to_interpolated_position(upPlane_shape[0], last_cv-8, last_cv, last_cv-4, 2.0/3.0)
    
    
    for n in range(bend_j_n):
        lo_start = chr(part) + '_lo' + upper + '_bendy_1_drvjnt'
        lo_end = chr(part) + '_lo' + upper + '_bendy_' + str(n+1) + '_drvjnt'
        
        div = 1/(bend_j_n-1) * n
        
        if n == 0:
            position_cv_to_joint(lo_start, lo_end, loPlane_shape[0], 0, 0)
        elif n + 1 == bend_j_n:
            position_cv_to_joint(lo_start, lo_end, loPlane_shape[0], last_cv, 1)
        else:
            position_cv_to_joint(lo_start, lo_end, loPlane_shape[0], 8 + 4*(n-1), div)
            
    # CV[1][0:3] を [0][0:3] と [2][0:3] の間の 1/3 の位置に設定
    set_cv_to_interpolated_position(loPlane_shape[0], 0, 8, 4, 1.0/3.0)
    # CV[4][0:3] を [3][0:3] と [5][0:3] の間の 2/3 の位置に設定
    set_cv_to_interpolated_position(loPlane_shape[0], last_cv-8, last_cv, last_cv-4, 2.0/3.0)
    
    create_follicles_on_surface(bend_j_n, chr(part) + '_' + upjoint + '_up_follicle', chr(part) + '_up' + upper + '_bendyRibbon_surf')
    create_follicles_on_surface(bend_j_n, chr(part) + '_' + upjoint + '_lo_follicle', chr(part) + '_lo' + upper + '_bendyRibbon_surf')
    
    cmds.duplicate(upPlane, name = chr(part) + '_up' + upper + '_bendyRibbon_IKmid_surf')
    cmds.duplicate(loPlane, name = chr(part) + '_lo' + upper + '_bendyRibbon_IKmid_surf')
    create_follicles_on_surface(1, chr(part) + '_' + upjoint + '_up2_follicle', chr(part) + '_up' + upper + '_bendyRibbon_IKmid_surf')
    create_follicles_on_surface(1, chr(part) + '_' + upjoint + '_lo2_follicle', chr(part) + '_lo' + upper + '_bendyRibbon_IKmid_surf')    


def create_bendy_ctrl(num, upjoint, lojoint, endjoint, upper):
    part = num #L is 76. R is 82.
    a = cmds.createNode('transform', name=chr(part)+'_' + upjoint + '_bendy_ctrl_A_grp')
    cmds.setAttr(a + '.rotateZ', -90) #RとLもここは同じでいい
    
    '''
    if upjoint == 'leg':
        cmds.matchTransform(a, 'ble_' + upjoint + '_jt_' + chr(part), piv=True, pos=True, rot=True)
        if part == 82:
            cmds.setAttr(a + '.rotateY', 0) #bのrotateを0にするため→L側は0でいいが、Rには180の反転した値が必要
    '''
    
    #up' + upper + '_bendy
    b = cmds.createNode('transform', name=chr(part)+'_up' + upper + '_bendy_space_LOC')
    c = cmds.createNode('transform', name=chr(part)+'_up' + upper + '_bendy_' + lojoint + 'space_LOC')
    set_joint_color(b, [1, 0, 0])  # 赤色
    set_joint_color(c, [1, 0, 0])  # 赤色
    cmds.parent(c, b)
    cmds.matchTransform(b, 'ble_' + upjoint + '_jt_' + chr(part), piv=True, pos=True, rot=True)
    cmds.parent(b, a)
    cmds.parent(chr(part) + '_up' + upper + '_bendy_main_3_offset', c)
    cmds.parent(chr(part) + '_up' + upper + '_bendy_main_1_offset', b)
    
    #lo' + upper + '_bendy
    d = cmds.createNode('transform', name=chr(part)+'_lo' + upper + '_bendy_space_LOC')
    e = cmds.createNode('transform', name=chr(part)+'_lo' + upper + '_bendy_' + endjoint + 'space_LOC')
    set_joint_color(d, [1, 0, 0])  # 赤色
    set_joint_color(e, [1, 0, 0])  # 赤色
    cmds.parent(e, d)
    cmds.matchTransform(d, 'ble_' + lojoint + '_jt_' + chr(part), piv=True, pos=True, rot=True)
    cmds.parent(d, a)
    cmds.parent(chr(part) + '_lo' + upper + '_bendy_main_3_offset', e)
    cmds.parent(chr(part) + '_lo' + upper + '_bendy_main_1_offset', d)
    
    #mid_bendy
    cmds.parent(chr(part) + '_up' + upper + '_bendy_main_2_offset', a)
    cmds.parent(chr(part) + '_lo' + upper + '_bendy_main_2_offset', a)
    
    if upjoint == 'arm':
        #shoulder_loc
        f = cmds.spaceLocator(n=chr(part) + '_clav_ctrl_LOC_upLOC')[0]
        cmds.matchTransform(f, 'shoulder_' + chr(part), piv=True, pos=True, rot=True)
        cmds.parent(f, 'shoulder_' + chr(part) + '_ctrl')
        cmds.parent(a, 'shoulder_' + chr(part) + '_ctrl')
        
    '''
    if upjoint == 'leg':
        #shoulder_loc
        f = cmds.spaceLocator(n=chr(part) + '_clav_ctrl_LOC_upLOC')[0]
        cmds.matchTransform(f, 'shoulder_' + chr(part), piv=True, pos=True, rot=True)
        cmds.parent(f, 'shoulder_' + chr(part) + '_ctrl')
        cmds.parent(a, 'shoulder_' + chr(part) + '_ctrl')
    '''
    
def create_offset_ctrl(num, upjoint, lojoint, endjoint, upper):
    part = num #L is 76. R is 82.
    
    #elbow_offset
    elbow_bend = createNodehijt('ble_' + lojoint + '_jt_' + chr(part), chr(part) + '_' + lojoint + '_offset', None, 1, 1)
    lock_attr(elbow_bend[2], 'ry', 'rz', 'sx', 'sy', 'sz', 'visibility')
    a = cmds.spaceLocator(n=chr(part) + '_' + upjoint + '_' + lojoint + '_offset_ctrl_aimLOC')[0]
    set_joint_color(a, [1, 0, 0])  # 赤色
    b = cmds.spaceLocator(n=chr(part) + '_' + upjoint + '_' + lojoint + '_offset_ctrl_upLOC')[0]
    cmds.parent(b, a)
    distance = calculate_distance('ble_' + lojoint + '_jt_' + chr(part), 'ble_' + endjoint + '_jt_' + chr(part))
    
    #cmds.setAttr(b + '.translateZ', -1 * distance)
    
    if part == 76 and upjoint == 'arm':
        cmds.setAttr(b + '.translateZ', -1 * distance)
    elif part == 82 and upjoint == 'arm':
        cmds.setAttr(b + '.translateZ', distance)
        
    #足の場合
    elif part == 76 and upjoint == 'leg':
        cmds.setAttr(b + '.translateZ', distance)
    elif part == 82 and upjoint == 'leg':
        cmds.setAttr(b + '.translateZ', -1 * distance)
    
        
    cmds.matchTransform(a, 'ble_' + lojoint + '_jt_' + chr(part), piv=True, pos=True, rot=True)
    c = cmds.spaceLocator(n=chr(part) + '_up' + upper + '_' + lojoint + '_bendcorrect_LOC')[0]
    d = cmds.spaceLocator(n=chr(part) + '_lo' + upper + '_' + lojoint + '_bendcorrect_LOC')[0]
    set_joint_color(c, [1, 0, 1])  # 桃色
    set_joint_color(d, [1, 0, 1])  # 桃色
    cmds.matchTransform(c, 'ble_' + lojoint + '_jt_' + chr(part), piv=True, pos=True, rot=True)
    cmds.matchTransform(d, 'ble_' + lojoint + '_jt_' + chr(part), piv=True, pos=True, rot=True)
    
    cmds.parent(a, chr(part) + '_' + lojoint + '_offset_ctrl')
    cmds.parent(c, chr(part) + '_' + lojoint + '_offset_ctrl')
    cmds.parent(d, chr(part) + '_' + lojoint + '_offset_ctrl')
    
    #wrist_offset
    wrist_bend = createNodehijt('ble_' + endjoint + '_jt_' + chr(part), chr(part) + '_' + endjoint + '_offset', None, 1, 1)
    lock_attr(wrist_bend[2], 'tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'visibility')
    e = cmds.spaceLocator(n=chr(part) + '_' + upjoint + '_' + endjoint + '_offset_ctrl_aimLOC')[0]
    set_joint_color(e, [1, 0, 0])  # 赤色
    f = cmds.spaceLocator(n=chr(part) + '_' + upjoint + '_' + endjoint + '_offset_ctrl_upLOC')[0]
    cmds.parent(f, e)
    cmds.parent(e, chr(part) + '_' + endjoint + '_offset_ctrl')
    cmds.matchTransform(e, 'ble_' + endjoint + '_jt_' + chr(part), piv=True, pos=True, rot=True)
    
    #cmds.setAttr(f + '.translateZ', -1 * distance)
    
    if part == 76 and upjoint == 'arm':
        cmds.setAttr(f + '.translateZ', -1 * distance)
    elif part == 82 and upjoint == 'arm':
        cmds.setAttr(f + '.translateZ', distance)
    
    #足の場合
    elif part == 76 and upjoint == 'leg':
        cmds.setAttr(f + '.translateX', distance)
        cmds.setAttr(f + '.rotateY', 90)
    elif part == 82 and upjoint == 'leg':
        cmds.setAttr(f + '.translateX', -1 * distance)
        cmds.setAttr(f + '.rotateY', 90)
    
    

def const_ctrl(num, upjoint, lojoint, endjoint, upper, bend_joint_num):
    part = num #L is 76. R is 82.
    for i in range(bend_joint_num):
        cmds.parentConstraint(chr(part) + '_' + upjoint + '_up_follicle' + str(i), chr(part) + '_up' + upper + '_micro_' + str(i+1) + '_offset', mo=True)
        cmds.parentConstraint(chr(part) + '_' + upjoint + '_lo_follicle' + str(i), chr(part) + '_lo' + upper + '_micro_' + str(i+1) + '_offset', mo=True)
        
    cmds.aimConstraint(chr(part) + '_up' + upper + '_' + lojoint + '_bendcorrect_LOC', chr(part) + '_up' + upper + '_bendy_' + lojoint + 'space_LOC',
    aim=(1,0,0), u=(0,1,0), wu=(0,1,0), wuo=chr(part) + '_' + upjoint + '_' + lojoint + '_offset_ctrl_upLOC', wut='objectrotation', mo=True)
    
    if upjoint == 'arm':
        cmds.aimConstraint(chr(part) + '_up' + upper + '_' + lojoint + '_bendcorrect_LOC', chr(part) + '_up' + upper + '_bendy_space_LOC',
        aim=(1,0,0), u=(0,1,0), wu=(0,1,0), wuo=chr(part) + '_clav_ctrl_LOC_upLOC', wut='objectrotation', mo=True) #wut='None'
    elif upjoint == 'leg':
        cmds.aimConstraint(chr(part) + '_up' + upper + '_' + lojoint + '_bendcorrect_LOC', chr(part) + '_up' + upper + '_bendy_space_LOC',
        aim=(1,0,0), u=(0,1,0), wu=(0,1,0), wut='None', mo=True) #wut='None'
    
    cmds.pointConstraint('ble_' + upjoint + '_jt_' + chr(part), chr(part) + '_up' + upper + '_bendy_space_LOC', mo=True)
    
    cmds.aimConstraint(chr(part) + '_' + upjoint + '_' + endjoint + '_offset_ctrl_aimLOC', chr(part) + '_lo' + upper + '_bendy_' + endjoint + 'space_LOC',
    aim=(1,0,0), u=(0,0,1), wu=(0,0,1), wuo=chr(part) + '_' + upjoint + '_' + endjoint + '_offset_ctrl_upLOC', wut='objectrotation', mo=True)#ここ大事！
    cmds.aimConstraint(chr(part) + '_' + upjoint + '_' + endjoint + '_offset_ctrl_aimLOC', chr(part) + '_lo' + upper + '_bendy_space_LOC',
    aim=(1,0,0), u=(0,1,0), wu=(0,1,0), wuo=chr(part) + '_' + upjoint + '_' + lojoint + '_offset_ctrl_upLOC', wut='objectrotation', mo=True)
    cmds.pointConstraint(chr(part) + '_lo' + upper + '_' + lojoint + '_bendcorrect_LOC', chr(part) + '_lo' + upper + '_bendy_space_LOC', mo=True)
    
    cmds.parentConstraint(chr(part) + '_' + upjoint + '_up2_follicle0', chr(part) + '_up' + upper + '_bendy_main_2_offset', mo=True)
    cmds.parentConstraint(chr(part) + '_' + upjoint + '_lo2_follicle0', chr(part) + '_lo' + upper + '_bendy_main_2_offset', mo=True)
    
    cmds.pointConstraint('ble_' + lojoint + '_jt_' + chr(part), chr(part) + '_' + lojoint + '_offset_offset', mo=True)#
    cmds.orientConstraint('ble_' + lojoint + '_jt_' + chr(part), chr(part) + '_' + lojoint + '_offset_offset', mo=True)#
    
    cmds.parentConstraint('ble_' + endjoint + '_jt_' + chr(part), chr(part) + '_' + endjoint + '_offset_offset', mo=True)#
    
def create_scale(num, upjoint, lojoint, endjoint, upper):
    part = num #L is 76. R is 82.
    if not cmds.objExists('globalScale_grp'):
        cmds.createNode('transform', name='globalScale_grp')
        set_joint_color('globalScale_grp', [0, 1, 1])  # 青色
        cmds.addAttr('globalScale_grp', ln='globalScale', at='float', defaultValue=1.0)
        cmds.setAttr('globalScale_grp' + '.globalScale', e=True, keyable=True)
        cmds.setAttr('globalScale_grp' + '.globalScale', 1)
        if cmds.objExists('rig_grp'):
            cmds.connectAttr('rig_grp.globalScale', 'globalScale_grp.globalScale')
    
    a = cmds.createNode('transform', name=chr(part) + '_' + upjoint + '_toHide_grp')
    set_joint_color(a, [1, 0, 0])  # 赤色
    b = cmds.createNode('transform', name=chr(part) + '_' + upjoint + '_follicle_grp')
    c = cmds.createNode('transform', name=chr(part) + '_' + upjoint + '_distance_grp')
    d = cmds.createNode('transform', name=chr(part) + '_' + upjoint + '_ribbonSurface_grp')
    
    cmds.parent(chr(part) + '_' + upjoint + '_up_follicle_gp', chr(part) + '_' + upjoint + '_lo_follicle_gp',
    chr(part) + '_' + upjoint + '_up2_follicle_gp', chr(part) + '_' + upjoint + '_lo2_follicle_gp', b)
    cmds.parent(chr(part) + '_up' + upper + '_bendyRibbon_surf', chr(part) + '_lo' + upper + '_bendyRibbon_surf',
    chr(part) + '_up' + upper + '_bendyRibbon_IKmid_surf' , chr(part) + '_lo' + upper + '_bendyRibbon_IKmid_surf', d)
    
    upS, upE, upD, upDT = create_mesure('_up' + upper + '_bendy_distance_LOCa', '_up' + upper + '_bendy_distance_LOCb', '_up' + upper + '_bendy_distance', upjoint, num)
    cmds.matchTransform(upS, 'ble_' + upjoint + '_jt_' + chr(part), piv=True, pos=True, rot=True)
    cmds.matchTransform(upE, 'ble_' + upjoint + '_jt_' + chr(part), piv=True, pos=True, rot=True)
    cmds.pointConstraint('ble_' + upjoint + '_jt_' + chr(part), upS)
    cmds.pointConstraint(chr(part)+'_up' + upper + '_' + lojoint + '_bendcorrect_LOC', upE)
    
    loS, loE, loD, loDT = create_mesure('_lo' + upper + '_bendy_distance_LOCa', '_lo' + upper + '_bendy_distance_LOCb', '_lo' + upper + '_bendy_distance', upjoint, num)
    cmds.matchTransform(loS, 'ble_' + lojoint + '_jt_' + chr(part), piv=True, pos=True, rot=True)
    cmds.matchTransform(loE, 'ble_' + endjoint + '_jt_' + chr(part), piv=True, pos=True, rot=True)
    cmds.pointConstraint(chr(part)+'_lo' + upper + '_' + lojoint + '_bendcorrect_LOC', loS)
    cmds.pointConstraint('ble_' + endjoint + '_jt_' + chr(part), loE)
    
    cmds.parent(b, c, d, a)
    
    #distanceノードから繋いでいく処理
    ma = cmds.shadingNode('multiplyDivide', asUtility=True)
    cmds.setAttr(ma + '.operation', 2)  # 2 は割り算を表します
    cmds.connectAttr(upD + '.distance', ma + '.input1X')
    cmds.connectAttr(loD + '.distance', ma + '.input1Y')
    cmds.connectAttr(ma + '.outputX', chr(part) + '_up' + upper + '_bendy_space_LOC.scaleX')
    cmds.connectAttr(ma + '.outputY', chr(part) + '_lo' + upper + '_bendy_space_LOC.scaleX')
    mb = cmds.shadingNode('multiplyDivide', asUtility=True)
    upD_D = cmds.getAttr(upD + '.distance')
    loD_D = cmds.getAttr(loD + '.distance')
    cmds.setAttr(mb + '.input2X', upD_D)
    cmds.setAttr(mb + '.input2Y', loD_D)
    cmds.connectAttr('globalScale_grp.globalScale', mb + '.input1X')
    cmds.connectAttr('globalScale_grp.globalScale', mb + '.input1Y')
    cmds.connectAttr(mb + '.outputX', ma + '.input2X')
    cmds.connectAttr(mb + '.outputY', ma + '.input2Y')
    
def bindskin(num, upper):
    part = num #L is 76. R is 82.
    up_joints1 = [chr(part) + '_up' + upper + '_bendy_main_1_drvjnt', chr(part) + '_up' + upper + '_bendy_main_2_drvjnt', chr(part) + '_up' + upper + '_bendy_main_3_drvjnt']
    cmds.skinCluster(up_joints1, chr(part) + '_up' + upper + '_bendyRibbon_surf', toSelectedBones=True, mi=3)
    lo_joints1 = [chr(part) + '_lo' + upper + '_bendy_main_1_drvjnt', chr(part) + '_lo' + upper + '_bendy_main_2_drvjnt', chr(part) + '_lo' + upper + '_bendy_main_3_drvjnt']
    cmds.skinCluster(lo_joints1, chr(part) + '_lo' + upper + '_bendyRibbon_surf', toSelectedBones=True, mi=3)
    
    up_joints2 = [chr(part) + '_up' + upper + '_bendy_main_1_drvjnt', chr(part) + '_up' + upper + '_bendy_main_3_drvjnt']
    cmds.skinCluster(up_joints2, chr(part) + '_up' + upper + '_bendyRibbon_IKmid_surf', toSelectedBones=True, mi=2)
    lo_joints2 = [chr(part) + '_lo' + upper + '_bendy_main_1_drvjnt', chr(part) + '_lo' + upper + '_bendy_main_3_drvjnt']
    cmds.skinCluster(lo_joints2, chr(part) + '_lo' + upper + '_bendyRibbon_IKmid_surf', toSelectedBones=True, mi=2)

def hand_scale(num):
    part = num #L is 76. R is 82.
    a = cmds.createNode('transform', name=chr(part) + '_finger_drvjnt_grp')
    set_joint_color(a, [0, 0, 1])  # 蒼色
    cmds.matchTransform(a, 'wrist_' + chr(part), piv=True, pos=True, rot=True)
    
    b = cmds.createNode('transform', name=chr(part) + '_hand_ctrl_grp')
    set_joint_color(b, [1, 1, 0])  # 黄色
    cmds.matchTransform(b, 'wrist_' + chr(part), piv=True, pos=True, rot=True)
    cmds.parent(b, chr(part) + '_arm_ctrl_grp')
    cmds.setAttr(b + '.rotateY', 0)
    cmds.setAttr(b + '.scaleZ', 1)
    
    c = cmds.createNode('transform', name=chr(part) + '_hand_deform_grp')
    cmds.parent(c, b)
    wrist_option = createNodehijt('wrist_' + chr(part), chr(part) + '_arm_option', None, 1, 1)
    cmds.addAttr(wrist_option[2], ln='handScale', at='float', defaultValue=1.0)
    cmds.setAttr(wrist_option[2] + '.handScale', e=True, keyable=True)
    cmds.setAttr(wrist_option[2] + '.handScale', 1)
    cmds.parent(wrist_option[0], c)##
    
    hand_j = create_joint('wrist_' + chr(part), chr(part) + '_hand_drvjnt')
    finger_parts = ['thoumb' ,'finger' ,'middle' ,'ring' ,'little']
    for f in finger_parts:
        cmds.parent('ble_' + f + '_A_jt_' + chr(part), hand_j)
    cmds.parent('finger_ctrl_gp_' + chr(part), c)
    cmds.parent(hand_j, a)
    cmds.parentConstraint(b, hand_j, mo=True)
    cmds.parentConstraint(chr(part) + '_wrist_offset_ctrl', b, mo=True)
    
    global_scale_attr = wrist_option[2] + '.handScale'
    
    # ドライバージョイントとその子孫の全ジョイントを取得
    descendant_joints = cmds.listRelatives(hand_j, allDescendents=True, type='joint') or []
    
    # ドライバージョイントをリストの最初に追加
    joints_to_connect = [hand_j] + [b] + descendant_joints
    
    # 各ジョイントに対してスケール属性にグローバルスケールを接続
    for joint in joints_to_connect:
        cmds.connectAttr(global_scale_attr, joint + '.scaleX', force=True)
        cmds.connectAttr(global_scale_attr, joint + '.scaleY', force=True)
        cmds.connectAttr(global_scale_attr, joint + '.scaleZ', force=True)
        
def move_to_GP(num, upjoint, lojoint, endjoint):
    if num == 76:
        cmds.parent(chr(num) + '_' + upjoint + '_micro_ctrl_grp',
        chr(num) + '_' + lojoint + '_offset_offset',
        chr(num) + '_' + endjoint + '_offset_offset',
        chr(num) + '_' + upjoint + '_ctrl_grp',)
    elif num == 82:
        cmds.parent(chr(num) + '_' + upjoint + '_micro_ctrl_grp',
        chr(num) + '_' + lojoint + '_offset_offset',
        chr(num) + '_' + endjoint + '_offset_offset',
        chr(num) + '_' + upjoint + '_ctrl_grp',)
        
        cmds.setAttr(chr(num) + '_' + lojoint + '_offset_offset' + '.scaleZ', 1)
        cmds.setAttr(chr(num) + '_' + endjoint + '_offset_offset' + '.scaleZ', 1)

def all_ctrl_option(num, main_parts):
    part = num #L is 76. R is 82.
    if not cmds.objExists('rig_grp'):
        rig_gp = cmds.createNode('transform', n='rig_grp')
        set_joint_color(rig_gp, [1, 0, 0])
        #cmds.addAttr(rig_gp, ln='globalScale', at='double', min=0, max=1, dv=1)
        cmds.addAttr(rig_gp, ln='globalScale', at='double', min=0, dv=1)
        cmds.setAttr(rig_gp + '.globalScale', e=True, keyable=True) #AttributeをchannelBoxに表示する
        cmds.connectAttr(rig_gp + '.globalScale', 'globalScale_grp.globalScale')
        

    if not cmds.objExists('driver_jnt_grp'):
        driver_jnt_gp = cmds.createNode('transform', n='driver_jnt_grp')
        set_joint_color(driver_jnt_gp, [0.26, 0.62, 1])
        cmds.connectAttr('rig_grp' + '.globalScale', driver_jnt_gp + '.scaleX')
        cmds.connectAttr('rig_grp' + '.globalScale', driver_jnt_gp + '.scaleY')
        cmds.connectAttr('rig_grp' + '.globalScale', driver_jnt_gp + '.scaleZ')
        cmds.parent(driver_jnt_gp, rig_gp)
        
    if not cmds.objExists('controls_grp'):
        ctrl_gp = cmds.createNode('transform', n='controls_grp')
        set_joint_color(ctrl_gp, [0.26, 0.62, 1])
        cmds.connectAttr('rig_grp' + '.globalScale', ctrl_gp + '.scaleX')
        cmds.connectAttr('rig_grp' + '.globalScale', ctrl_gp + '.scaleY')
        cmds.connectAttr('rig_grp' + '.globalScale', ctrl_gp + '.scaleZ')
        cmds.parent(ctrl_gp, rig_gp)
        
    if not cmds.objExists('null_grp'):
        null_gp = cmds.createNode('transform', n='null_grp')
        set_joint_color(null_gp, [1, 0.23, 0.23])
        cmds.parent(null_gp, rig_gp)
        cmds.parent('globalScale_grp', null_gp)
        
    if not cmds.objExists('null_toHide_grp'):
        null_toHide_gp = cmds.createNode('transform', n='null_toHide_grp')
        set_joint_color(null_toHide_gp, [1, 0.23, 0.23])
        cmds.parent(null_toHide_gp, null_gp)
        
    if main_parts == 'arm':
        if not cmds.objExists('arm_ctrl_grp'):
            arm_ctrl_gp = cmds.createNode('transform', n='arm_ctrl_grp')
            set_joint_color(arm_ctrl_gp, [1, 1, 0.39])
            cmds.parent(arm_ctrl_gp, ctrl_gp)
        
        cmds.parent(chr(part) + '_arm_toHide_grp', 'null_toHide_grp')
        
        cmds.parent(chr(part) + '_finger_drvjnt_grp', 'arm_drvjnt_grp')
        
    elif main_parts == 'leg':

        cmds.parent(chr(part) + '_leg_loc_toHide_grp', chr(part) + '_leg_toHide_grp')

        cmds.parent(chr(part) + '_leg_toHide_grp', 'null_toHide_grp')
        
        cmds.parent(chr(part) + '_leg_bendy_ctrl_A_grp', chr(part) + '_leg_ctrl_grp')
        
        cmds.parent(chr(part) + '_revFoot_grp', chr(part) + '_leg_drvjnt_grp')


#バインド用のジョイントを生成かつ、ドライバージョイントと接続    
def create_bind_bend_joint(num, parts, upper, joint_num):
    cmds.select(cl=True)
    part = num #L is 76. R is 82.
    for j in range(joint_num):
        upbend_joint = chr(part) + '_up' + upper + '_bendy_' + str(j+1) + '_drvjnt'
        bind_upbend_joint = 'bin_' + 'up' + upper + str(j+1) + '_jt_' + chr(part)
        create_joint(upbend_joint, bind_upbend_joint)
    
    for j in range(joint_num): 
        lobend_joint = chr(part) + '_lo' + upper + '_bendy_' + str(j+1) + '_drvjnt'
        bind_lobend_joint = 'bin_' + 'lo' + upper + str(j+1) + '_jt_' + chr(part)
        create_joint(lobend_joint, bind_lobend_joint)
        
    cmds.select(cl=True)
    
    #ドライバー用のジョイントとバインドジョイントの接続
    for j in range(joint_num): 
        upbend_joint = chr(part) + '_up' + upper + '_bendy_' + str(j+1) + '_drvjnt'
        bind_upbend_joint = 'bin_' + 'up' + upper + str(j+1) + '_jt_' + chr(part)
        cmds.parentConstraint(upbend_joint, bind_upbend_joint, mo=True)
        cmds.connectAttr(upbend_joint + ".scale", bind_upbend_joint + ".scale")
        
    for j in range(joint_num): 
        lobend_joint = chr(part) + '_lo' + upper + '_bendy_' + str(j+1) + '_drvjnt'
        bind_lobend_joint = 'bin_' + 'lo' + upper + str(j+1) + '_jt_' + chr(part)
        cmds.parentConstraint(lobend_joint, bind_lobend_joint, mo=True)
        cmds.connectAttr(lobend_joint + ".scale", bind_lobend_joint + ".scale")
    
    if parts == 'arm':
        create_joint(chr(part) + '_hand_drvjnt', 'bin_hand_jt_' + chr(part))
        
        #ドライバー用のジョイントとバインドジョイントの接続
        cmds.parentConstraint(chr(part) + '_hand_drvjnt', 'bin_hand_jt_' + chr(part), mo=True)
        cmds.connectAttr(chr(part) + '_hand_drvjnt' + ".scale", 'bin_hand_jt_' + chr(part) + ".scale")
        
    cmds.select(cl=True)

def main_arm():
    bend_joint_num = 4
    bend_joint(76, 'arm', 'elbow', 'wrist', 'Arm', bend_joint_num)
    bend_main_joint(76, 'arm', 'elbow', 'wrist', 'Arm')
    #create_nurbs(76, 'arm', 'elbow', 'Arm')
    create_nurbs2(76, 'arm', 'elbow', 'Arm', bend_joint_num)
    create_bendy_ctrl(76, 'arm', 'elbow', 'wrist', 'Arm')
    create_offset_ctrl(76, 'arm', 'elbow', 'wrist', 'Arm')
    move_to_GP(76, 'arm', 'elbow', 'wrist') #ここでコントローラたちをRarmGPのおおもとに入れる
    const_ctrl(76, 'arm', 'elbow', 'wrist', 'Arm', bend_joint_num)
    create_scale(76, 'arm', 'elbow', 'wrist', 'Arm')
    bindskin(76, 'Arm') #ベンドジョイントの数によってはここの影響地も考える必要がある
    hand_scale(76)
    all_ctrl_option(76, 'arm')

    bend_joint(82, 'arm', 'elbow', 'wrist', 'Arm', bend_joint_num)
    bend_main_joint(82, 'arm', 'elbow', 'wrist', 'Arm')
    #create_nurbs(82, 'arm', 'elbow', 'Arm')
    create_nurbs2(82, 'arm', 'elbow', 'Arm', bend_joint_num)
    create_bendy_ctrl(82, 'arm', 'elbow', 'wrist', 'Arm')
    create_offset_ctrl(82, 'arm', 'elbow', 'wrist', 'Arm')
    move_to_GP(82, 'arm', 'elbow', 'wrist') #ここでコントローラたちをRarmGPのおおもとに入れる
    const_ctrl(82, 'arm', 'elbow', 'wrist', 'Arm', bend_joint_num)
    create_scale(82, 'arm', 'elbow', 'wrist', 'Arm')
    bindskin(82, 'Arm')
    hand_scale(82)
    all_ctrl_option(82, 'arm')
    
    create_bind_bend_joint(76, 'arm', 'Arm', bend_joint_num)
    create_bind_bend_joint(82, 'arm', 'Arm', bend_joint_num)

def main_leg():
    bend_joint_num = 4
    bend_joint(76, 'leg', 'knees', 'ankle', 'Leg', bend_joint_num)
    bend_main_joint(76, 'leg', 'knees', 'ankle', 'Leg')
    #create_nurbs(76, 'leg', 'knees', 'Leg')
    create_nurbs2(76, 'leg', 'knees', 'Leg', bend_joint_num)
    create_bendy_ctrl(76, 'leg', 'knees', 'ankle', 'Leg')
    create_offset_ctrl(76, 'leg', 'knees', 'ankle', 'Leg')
    move_to_GP(76, 'leg', 'knees', 'ankle') #ここでコントローラたちをRarmGPのおおもとに入れる
    const_ctrl(76, 'leg', 'knees', 'ankle', 'Leg', bend_joint_num)
    create_scale(76, 'leg', 'knees', 'ankle', 'Leg')
    bindskin(76, 'Leg')
    all_ctrl_option(76, 'leg')
    
    bend_joint(82, 'leg', 'knees', 'ankle', 'Leg', bend_joint_num)
    bend_main_joint(82, 'leg', 'knees', 'ankle', 'Leg')
    #create_nurbs(82, 'leg', 'knees', 'Leg')
    create_nurbs2(82, 'leg', 'knees', 'Leg', bend_joint_num)
    create_bendy_ctrl(82, 'leg', 'knees', 'ankle', 'Leg')
    create_offset_ctrl(82, 'leg', 'knees', 'ankle', 'Leg')
    move_to_GP(82, 'leg', 'knees', 'ankle') #ここでコントローラたちをRarmGPのおおもとに入れる
    const_ctrl(82, 'leg', 'knees', 'ankle', 'Leg', bend_joint_num)
    create_scale(82, 'leg', 'knees', 'ankle', 'Leg')
    bindskin(82, 'Leg')
    all_ctrl_option(82, 'leg')
    
    create_bind_bend_joint(76, 'leg', 'Leg', bend_joint_num)
    create_bind_bend_joint(82, 'leg', 'Leg', bend_joint_num)