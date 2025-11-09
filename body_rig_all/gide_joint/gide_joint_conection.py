# -*- coding: UTF-8 -*-
#左右のジョイントやロケータをつなげる
import sys
import os
import io
import maya.cmds as cmds

class MyClass:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.gide_joint_path = os.path.join(self.script_dir, "gide_joint.txt")
        self.gide_LOC_L = ['ball_swivel_guide_L', 'toe_swivel_guide_L', 'foot_tilt_inner_guideL_L', 'foot_tilt_inner_guideR_L', 'heel_swivel_guide_L']
        self.gide_LOC_R = ['ball_swivel_guide_R', 'toe_swivel_guide_R', 'foot_tilt_inner_guideR_R', 'foot_tilt_inner_guideL_R', 'heel_swivel_guide_R']

    def gide_connection(self):

        #ガイドのジョイントの名前を読み込んでる
        with io.open(self.gide_joint_path, 'r') as f1:
            gide_joint = [m.strip() for m in f1.readlines() if m.strip()]
            
        for g in gide_joint:
            
            joint_L = g + '_L'
            joint_R = g + '_R'
            
            jl_x = cmds.getAttr(joint_L + '.jointOrientX')
            jl_y = cmds.getAttr(joint_L + '.jointOrientY')
            jl_z = cmds.getAttr(joint_L + '.jointOrientZ')
            if (joint_L == 'shoulder_L') or (joint_L == 'leg_L'):
                cmds.setAttr(joint_R + '.jointOrientX', -180 + jl_x)
                cmds.setAttr(joint_R + '.jointOrientY', jl_y * -1) 
                cmds.setAttr(joint_R + '.jointOrientZ', jl_z * -1)
            
            else:
                cmds.setAttr(joint_R + '.jointOrientX', jl_x)
                cmds.setAttr(joint_R + '.jointOrientY', jl_y) 
                cmds.setAttr(joint_R + '.jointOrientZ', jl_z) 
            
            mt = cmds.createNode('multiplyDivide')
            mr = cmds.createNode('multiplyDivide')
            
            if (g=='shoulder') or (g=='leg'):
                cmds.setAttr(mt + '.input2X', -1)
            else:
                cmds.setAttr(mt + '.input2X', -1)
                cmds.setAttr(mt + '.input2Y', -1)
                cmds.setAttr(mt + '.input2Z', -1)
                
            cmds.connectAttr(joint_L + '.translateX', mt + '.input1X')
            cmds.connectAttr(joint_L + '.translateY', mt + '.input1Y')
            cmds.connectAttr(joint_L + '.translateZ', mt + '.input1Z')
            cmds.connectAttr(joint_L + '.rotateX', mr + '.input1X')
            cmds.connectAttr(joint_L + '.rotateY', mr + '.input1Y')
            cmds.connectAttr(joint_L + '.rotateZ', mr + '.input1Z')
            
            cmds.connectAttr(mt + '.outputX', joint_R + '.translateX')
            cmds.connectAttr(mt + '.outputY', joint_R + '.translateY')
            cmds.connectAttr(mt + '.outputZ', joint_R + '.translateZ')
            cmds.connectAttr(mr + '.outputX', joint_R + '.rotateX')
            cmds.connectAttr(mr + '.outputY', joint_R + '.rotateY')
            cmds.connectAttr(mr + '.outputZ', joint_R + '.rotateZ')
            
        for i in range(len(self.gide_LOC_L)):
            mt = cmds.createNode('multiplyDivide')
            
            cmds.setAttr(mt + '.input2X', -1)
            if (self.gide_LOC_L[i] == 'foot_tilt_inner_guideL_L') or (self.gide_LOC_L[i] == 'foot_tilt_inner_guideR_L'):
                cmds.setAttr(mt + '.input2Y', -1)
            cmds.setAttr(mt + '.input2Z', -1)
                
            cmds.connectAttr(self.gide_LOC_L[i] + '.translateX', mt + '.input1X')
            cmds.connectAttr(self.gide_LOC_L[i] + '.translateY', mt + '.input1Y')
            cmds.connectAttr(self.gide_LOC_L[i] + '.translateZ', mt + '.input1Z')
            
            cmds.connectAttr(mt + '.outputX', self.gide_LOC_R[i] + '.translateX')
            cmds.connectAttr(mt + '.outputY', self.gide_LOC_R[i] + '.translateY')
            cmds.connectAttr(mt + '.outputZ', self.gide_LOC_R[i] + '.translateZ')
    


    def multiply_node_delete(self):
        cmds.select(all=True) #シーン内のオブジェクトの全ての親を選ぶ
        cmds.select(cmds.ls(selection=True, dagObjects=False, type=('multiplyDivide'))) #上で選んだ物から、lsコマンドで各コンストを格納し、selectコマンドで再度選ぶ
        cmds.delete()
        
    def LOC_parent(self):
        cmds.parent(self.gide_LOC_L[0:4], 'foot_ball_L')
        cmds.parent(self.gide_LOC_L[4], 'foot_heel_L')
        cmds.parent(self.gide_LOC_R[0:4], 'foot_ball_R')
        cmds.parent(self.gide_LOC_R[4], 'foot_heel_R')
        
    def LOC_unparent(self):
        cmds.parent(self.gide_LOC_L ,w=True)
        cmds.parent(self.gide_LOC_R ,w=True)
        
    def mainA(self):
        self.gide_connection()
        self.LOC_parent()
        
    def mainB(self):
        self.multiply_node_delete()
        self.LOC_unparent()
        
'''
import sys
import importlib

absolute_path = "C:/Users/meidm/Desktop/body_rig_all"
sys.path.append(absolute_path)

import gide_joint_conection
importlib.reload(gide_joint_conection)
from gide_joint_conection import MyClass
     
my_instance = MyClass()
my_instance.mainA()
my_instance.mainB()
'''