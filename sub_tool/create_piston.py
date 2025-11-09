import math
import maya.cmds as cmds


def create_joint(src_joint, new_joint_name, rot):
    
    cmds.select(clear=True)
    # ジョイントの位置を取得
    position = cmds.xform(src_joint, query=True, translation=True, worldSpace=True)
    
    # ジョイントのワールド座標での回転を取得
    rotation = cmds.xform(src_joint, query=True, rotation=True, worldSpace=True)
    
    print('jojo')

    # 同じ位置で新しいジョイントを作成
    new_joint = cmds.joint(name=new_joint_name, position=position)
    
    if rot == 1:
        # 新しいジョイントのワールド座標での回転を設定
        cmds.xform(new_joint, rotation=rotation, worldSpace=True)

    return new_joint


def calculate_distance(joint1, joint2):
    # ジョイントのワールド座標を取得
    pos1 = cmds.xform(joint1, query=True, worldSpace=True, translation=True)
    pos2 = cmds.xform(joint2, query=True, worldSpace=True, translation=True)

    # ユークリッド距離を計算
    distance = math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2 + (pos2[2] - pos1[2]) ** 2)
    
    # 二つの位置の中間点を計算
    mid_pos = [(pos1[0] + pos2[0]) / 2, (pos1[1] + pos2[1]) / 2, (pos1[2] + pos2[2]) / 2]
    return distance, mid_pos
    

def main():    
    sels = cmds.ls(sl=True)
    
    if len(sels) != 2:
        cmds.error("Please select exactly two joints.")
        return
    
    '''
    二つのジョイントを選択
    ジョイントの距離を図る
    二つのジョイントの間に新ジョイントを配置し、距離/2のxの位置に配置
    他のエンドジョイントの二つも距離を参考に配置する
    '''
    
    #cmds.makeIdentity(sels[0], a=True, t=False, r=True, s=False, n=False, pn=True)
    
    dis = calculate_distance(sels[0], sels[1])
    middle_jt = create_joint(sels[0], 'middle_jt', 1)
    cmds.xform(middle_jt, worldSpace=True, translation=dis[1])
    cmds.move(-dis[0]/2, 0, 0, middle_jt, r=True, os=True, wd=True)
    
    bottom_jt = create_joint(sels[0], 'bottom_jt', 1)
    cmds.move(0, dis[0]/5, 0, bottom_jt, r=True, os=True, wd=True)
    
    top_jt = create_joint(sels[1], 'top_jt', 1)
    cmds.move(-dis[0]/5, 0, 0, top_jt, r=True, os=True, wd=True)
    
    cmds.parent(sels[0], bottom_jt)
    cmds.parent(middle_jt, bottom_jt)
    cmds.parent(top_jt, middle_jt)
    cmds.parent(sels[1], top_jt)
    
    aim_LOC_top = cmds.spaceLocator(n='aim_LOC_top')[0]
    cmds.matchTransform(aim_LOC_top, top_jt, piv=True, pos=True, rot=True)
    cmds.xform(aim_LOC_top, worldSpace=True, translation=dis[1])
    cmds.move(dis[0]/2, 0, 0, aim_LOC_top, r=True, os=True, wd=True)
    
    aim_LOC_bottom = cmds.spaceLocator(n='aim_LOC_bottom')[0]
    cmds.matchTransform(aim_LOC_bottom, bottom_jt, piv=True, pos=True, rot=True)
    cmds.xform(aim_LOC_bottom, worldSpace=True, translation=dis[1])
    cmds.move(dis[0]/2, 0, 0, aim_LOC_bottom, r=True, os=True, wd=True)
    
    cmds.parent(aim_LOC_top, top_jt)
    cmds.parent(aim_LOC_bottom, bottom_jt)
    
    print(sels[0])
    cmds.makeIdentity(bottom_jt, a=True, t=False, r=True, s=False, n=False, pn=True)

    cmds.ikHandle(n='IK_piston', sj=bottom_jt, ee=top_jt, sol='ikRPsolver', s='sticky')
    
    cmds.aimConstraint(sels[0], sels[1], aim=(0,1,0), u=(0,1,0), wu=(0,1,0), wuo=aim_LOC_top, wut='object', mo=True)
    cmds.aimConstraint(sels[1], sels[0], aim=(0,1,0), u=(0,1,0), wu=(0,1,0), wuo=aim_LOC_bottom, wut='object', mo=True)
    
    
main()












