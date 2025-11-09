import maya.cmds as cmds
import maya.mel as mel
import os
import xml.etree.ElementTree as ET

def import_fbx(file_path):
    cmds.file(file_path, i=True, ignoreVersion=True, mergeNamespacesOnClash=False, namespace=":", options="fbx", pr=True)

def define_humanik():
    mel.eval('hikCreateCharacter("Character1");')
    
def create_rig():
    mel.eval('hikCreateControlRig')#
    
    _HUMAN_IK_SOURCE_MENU = "hikSourceList"
    _HUMAN_IK_SOURCE_MENU_OPTION = _HUMAN_IK_SOURCE_MENU + "|OptionMenu"

    target = 'Character1'
    source = 'None'

    mel.eval('hikUpdateCurrentCharacterFromUI();')
    mel.eval('hikUpdateContextualUI();')
    mel.eval('hikSetCurrentCharacter("{0}")'.format(target))

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
            
def bake_to_control_rig(character_name):
    """
    HumanIKのキャラクターに対してBake to Control Rigを実行するスクリプト
    """
    # HumanIKのキャラクターを選択
    cmds.select(character_name)

    # HumanIKリグを選択し、ベイクを実行
    mel.eval('hikBakeToControlRig "{}"'.format(character_name))
    
def setupSceneForAnimation(x, y, z):
    cmds.currentUnit(time='film')#24fpsに変更

    end_frame = cmds.playbackOptions(q=True, max=True)#フレームレンジを整数に直す
    end_frame_int = int(round(end_frame))
    cmds.playbackOptions(min=0, max=end_frame_int)


    cmds.currentTime(-1)
    a = cmds.select(root_joint, hi=True)
    sel = cmds.ls(sl=True)

    for s in sel:
        cmds.setAttr(s + '.rotateX', 0)
        cmds.setAttr(s + '.rotateY', 0)
        cmds.setAttr(s + '.rotateZ', 0)

    cmds.setAttr("mixamorig:Hips.translateX", x)
    cmds.setAttr("mixamorig:Hips.translateY", y)
    cmds.setAttr("mixamorig:Hips.translateZ", z)
    
def get_last_keyframe_for_selected_joints():
    # 選択したオブジェクトを取得
    selected_joints = cmds.ls(root_joint)
    
    if not selected_joints:
        print("ジョイントが選択されていません。")
        return None
    
    last_frame = None
    
    for joint in selected_joints:
        # ジョイントのアニメーションカーブを取得
        connected_curves = cmds.listConnections(joint, type='animCurve', source=True) or []
        
        # 各カーブのキーが打たれている最終フレームを取得
        for curve in connected_curves:
            keyframes = cmds.keyframe(curve, query=True, timeChange=True)
            
            if keyframes:
                curve_last_frame = max(keyframes)
                
                # 全体の最終フレームを更新
                if last_frame is None or curve_last_frame > last_frame:
                    last_frame = curve_last_frame
    
    cmds.playbackOptions(max = last_frame)
    return last_frame

def select_joints(root_joint):
    all_joints = cmds.listRelatives(root_joint, allDescendents=True, type='joint') or []
    all_joints.append(root_joint)
    cmds.select(clear=True)
    cmds.select(all_joints)

def get_joint_info_from_XML(template_path):
    tree = ET.parse(template_path)
    root = tree.getroot()
    items = root.findall('./match_list/item')

    joint_items = {}
    for index, item in enumerate(items):
        value = item.get('value')
        if value:
            joint_items[index] = value
    return joint_items

def assign_humanik_template(template_path):
    joint_dict = get_joint_info_from_XML(template_path)
    for key, value in joint_dict.items():
        print key, value
        mel.eval('setCharacterObject("{0}", "Character1", {1}, 0);'.format(value, key))

def save_scene(file_path):
    cmds.file(rename = file_path)
    cmds.file(save = True, type = 'mayaAscii')

def setting_hik_from_fbx(folder_path, root_joint, template_path, save_folder):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            print("FBX file:",file)
            if file.lower().endswith(".fbx"):
                fbx_file_path = os.path.join(root, file)
                cmds.file(new=True, force=True) 
                import_fbx(fbx_file_path)
                
                #get_last_keyframe_for_selected_joints()
                #setupSceneForAnimation(-1.01, 81.252, 0)#fpsや初期ポーズの設定
                
                define_humanik()
                select_joints(root_joint)
                
                assign_humanik_template(template_path)
                
                create_rig()#コントローラの追加
                #bake_to_control_rig("Character1")#アニメーションのベイク
                
                base_name = os.path.splitext(os.path.basename(fbx_file_path))[0]
                save_file_path = os.path.join(save_folder, base_name + ".ma")
                save_scene(save_file_path)
                


fbx_folder = R"\\192.168.11.207\vfx\works\s_yamana\test"
maflie_save_folder = R"\\192.168.11.207\vfx\works\s_yamana\test"
hik_template_path = R"\\192.168.11.207\vfx\works\s_yamana\test\tmp\template.xml"
root_joint = "pelvis"

print ("#####__START__#####")
# execute
setting_hik_from_fbx(fbx_folder, root_joint, hik_template_path, maflie_save_folder)

print ("#####__FINISH__#####")