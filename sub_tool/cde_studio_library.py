# -*- coding: UTF-8 -*-
import shutil
import os
import sys
import time
from maya import cmds
from maya import mel
from studiolibrarymaya import animitem
from mutils import playblast

#########
# animationのmaファイルをHIKのSourceに適用してStudioLibraryに登録する
#########
_HUMAN_IK_SOURCE_MENU = "hikSourceList"
_HUMAN_IK_SOURCE_MENU_OPTION = _HUMAN_IK_SOURCE_MENU + "|OptionMenu"

# アニメーションデータフォルダのパス
animation_folder_path = R"\\192.168.11.207\vfx\sozai\model\cde_peopleanimation\002_A-set\104_Sota\Animation(mixamo)"
studio_path = R"\\192.168.11.207\cde\assets\Anim"

#hik_character_name = "male"
hik_source_name = "Character1"
animation_root_joint_path = "mixamorig:Hips"
rig_root = "Character1_Ctrl_Reference"

start_frame = 0
end_frame = 100 # [変更不可]update_playback_range_to_keys()でanimation範囲の最後のframeに置き換えられる
#########

def update_playback_range_to_keys():
    cmds.select(animation_root_joint_path)
    selected_objects = cmds.ls(selection=True)

    if not selected_objects:
        cmds.warning("select obj nothing")
        return
        
    all_keys = []
    for obj in selected_objects:
        key_times = cmds.keyframe(obj, query=True, timeChange=True)
        if key_times:
            all_keys.extend(key_times)

    if not all_keys:
        cmds.warning("select obj anim key nothing")
        return

    animation_start_frame = min(all_keys)
    animation_end_frame = max(all_keys)

    global end_frame
    end_frame = animation_end_frame

    cmds.playbackOptions(min=animation_start_frame, max=animation_end_frame)



def hik_retarget(source, target):
    u"""
    Args:
        source (unicode): ソースのキャラクター
        target (unicode): リターゲット先のキャラクター
    """

    mel.eval('hikUpdateCurrentCharacterFromUI();')
    mel.eval('hikUpdateContextualUI();')
    mel.eval('hikSetCurrentCharacter("{0}")'.format(target))

    # hikSetCurrentSourceFromCharacterが動作しないので、optionMenuのアップデートで実現する
    # https://forums.autodesk.com/t5/maya-animation-and-rigging/pythonic-mel-way-to-retarget-hik/td-p/7609798
    items = cmds.optionMenuGrp(_HUMAN_IK_SOURCE_MENU, q=True, ill=True)

    retargeting_result = False
    for i in range(0, len(items)):
        label = cmds.menuItem(items[i], q=True, l=True)
        # 空白が頭に入っているので除去
        if label.lstrip() == source:
            print("Match found. Setting source to:", source)
            cmds.optionMenu(_HUMAN_IK_SOURCE_MENU_OPTION, e=True, sl=i + 1)
            mel.eval('hikUpdateCurrentSourceFromUI()')
            mel.eval('hikUpdateContextualUI()')
            mel.eval('hikControlRigSelectionChangedCallback')
            retargeting_result=True
            break

    if(not retargeting_result):
        cmds.warning('Retargeting failure. no source of arguments')
        return

def hik_source_match_position():
    a = cmds.ls('HIKproperties1')[0]
    cmds.setAttr(a + '.ForceActorSpace', 1)
    cmds.setAttr(a + '.AnkleHeightCompensationMode', 0)

def hik_bake_to_controlRig():
    mel.eval('hikBakeToControlRig 0')
    mel.eval('hikSetCurrentSourceFromCharacter(hikGetCurrentCharacter())')
    mel.eval('hikUpdateSourceList')
    mel.eval('hikUpdateContextualUI')

def create_studiolibrary_thumbnail(thumbnail_path):
    playblast_file_path = thumbnail_path
    width = 512
    height = 512
    frame_range = (start_frame, end_frame) 
    format = "image"
    compression = "jpg"
    quality = 100
    viewer = False

    # Playblastを実行
    cmds.playblast(
        filename=playblast_file_path,
        format=format,
        compression=compression,
        quality=quality,
        width=width,
        height=height,
        startTime=frame_range[0],
        endTime=frame_range[1],
        viewer=viewer,
    )

def delete_meshes_and_joints():
    # メッシュを持つオブジェクトをリスト化
    all_meshes = cmds.ls(type='mesh')
    # メッシュのシェイプからトランスフォームノードを取得
    transform_meshes = cmds.listRelatives(all_meshes, parent=True, fullPath=True) if all_meshes else []

    # ジョイントをリスト化
    all_joints = cmds.ls(type='joint')

    # メッシュのトランスフォームとジョイントを削除
    if transform_meshes:
        cmds.delete(transform_meshes)
    if all_joints:
        cmds.delete(all_joints)
    cmds.delete('Character1_Ctrl_Reference')

    # 完了メッセージ
    print("メッシュとジョイントの削除が完了しました。")

def delete_animation_joint_and_hik():
    if cmds.objExists(animation_root_joint_path) and cmds.objExists(hik_source_name) :
        cmds.delete(animation_root_joint_path)
        cmds.delete(hik_source_name)
    else:
        cmds.warning('delete node not found:', animation_root_joint_path,hik_source_name)

def camera_setting():
    cmds.setAttr("persp.translateX", 216.409)
    cmds.setAttr("persp.translateY", 78.189)
    cmds.setAttr("persp.translateZ", 210.149)
    cmds.setAttr("persp.rotateX", 0)
    cmds.setAttr("persp.rotateY", 46.2)
    cmds.setAttr("persp.rotateZ", 0)


def main():
    # アニメーションデータフォルダ内のファイルを取得
    animation_files = [f for f in os.listdir(animation_folder_path) if f.endswith('.ma')]
    if(len(animation_files) == 0):
        cmds.warning('no animation file')
        return

    for animation_file in animation_files:
        print('start create'+animation_file+'file')
        # import animation file
        animation_file_path = os.path.join(animation_folder_path, animation_file)            
        cmds.file(animation_file_path, i=True)
        
        camera_setting()#カメラの設置

        # update playback range from animation keys
        update_playback_range_to_keys()

        # setting humanIK and bake keys to controller
        '''
        hik_retarget(hik_source_name, hik_character_name)
        hik_source_match_position()
        hik_bake_to_controlRig()
        '''

        # saving an animation item
        print('# animitem.save start #')
        ctrl_all = cmds.listRelatives(rig_root, allDescendents=True, fullPath=False, shapes=False)

        save_animation_path = studio_path+'\\'+animation_file.partition('.')[0]
        animitem.save(save_animation_path, objects=ctrl_all, frameRange=(start_frame, end_frame), bakeConnected=False)
        print('# animitem.save end #')

        thumbnail_path = save_animation_path + '.anim' + '\sequence'
        os.makedirs(thumbnail_path)
        thumbnail_filename_path = thumbnail_path+'\\thumbnail'
        print('thumbnail_path'+thumbnail_filename_path)
        create_studiolibrary_thumbnail(thumbnail_filename_path)

        # clean outliner and hik
        #delete_meshes_and_joints()
        #delete_animation_joint_and_hik()
        
        cmds.file(new=True, force=True)

print('###### start ######')
main()
print('###### end ######')
