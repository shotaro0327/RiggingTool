# -*- coding: UTF-8 -*-
#create by ShotaroYamana

import maya.cmds as cmds

def shift_blend_shapes():
    # シーン内のすべてのブレンドシェイプノードをフルパス名で取得
    blend_shapes = cmds.ls(type='blendShape', long=True)
    if not blend_shapes:
        print("No blendShape nodes found in the scene.")
        return

    for b in blend_shapes:
        # nullノードを作成
        null_node = cmds.group(empty=True, name='NULL_' + b.split('|')[-1])
        print("BlendShape Node: " + b)

        # ブレンドシェイプのターゲットを取得
        targets = cmds.aliasAttr(b, query=True)
        if targets:
            target_names = [targets[i] for i in range(0, len(targets), 2)]  # ターゲット名のみ取得
            target_names.sort()  # 名前順にソート

            for target_name in target_names:
                target_weight = targets[targets.index(target_name) + 1]

                # nullノードに0~1の範囲でアトリビュートを追加
                cmds.addAttr(null_node, ln=target_name, at='float', defaultValue=0, min=0, max=1)
                cmds.setAttr(null_node + '.' + target_name, e=True, keyable=True)

                # nullノードのロックされるアトリビュート設定
                trs_all = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
                for trs in trs_all:
                    cmds.setAttr(null_node + '.' + trs, lock=True, keyable=False, channelBox=False)

                # ブレンドシェイプターゲットにアニメーションのキーがあるか確認
                if cmds.keyframe(b + '.' + target_weight, query=True, keyframeCount=True) > 0:
                    anim_curve = cmds.listConnections(b + '.' + target_weight, type='animCurve')
                    if anim_curve:
                        for curve in anim_curve:
                            try:
                                cmds.connectAttr(curve + '.output', null_node + '.' + target_name)
                                cmds.disconnectAttr(curve + '.output', b + '.' + target_weight)
                            except Exception as e:
                                print("Error connecting animation curve: {}".format(e))

                # アトリビュートをブレンドシェイプのターゲットに接続
                try:
                    cmds.connectAttr(null_node + '.' + target_name, b + '.' + target_weight)
                    print("  Target: " + target_name + ", connected to: " + b + '.' + target_weight)
                except Exception as e:
                    print("Error connecting attribute {}: {}".format(target_name, e))
        else:
            print("  No targets found.")
                
# スクリプトを実行
def main():
    shift_blend_shapes()
