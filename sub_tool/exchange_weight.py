# -*- coding: UTF-8 -*-
#weight_copy.py
#先に新しいjointはバインドする
#先にコピーしたいジョイントを選択し、次にウェイトが既にあるジョイントを選択する。

###やってること
#移したいweightを持っているjointの
#worldMatrixとlockInfluenceWeightsとObjectColorRGBとつながっているskinklusterを
#新しいjointに繋ぎなおす。
#inverseMatrixの入れ替えをする
#後に追加したジョイントとsukinclusterの繋ぎは消す。

import maya.cmds as cmds

sel = cmds.ls(sl=True)
new_j = cmds.getAttr(sel[0] + '.worldInverseMatrix[0]')
a1 = cmds.listConnections(sel[0] + '.objectColorRGB', p=True)
a2 = cmds.listConnections(sel[0] + '.worldMatrix', p=True)
a3 = cmds.listConnections(sel[0] + '.lockInfluenceWeights', p=True)
cmds.disconnectAttr(sel[0] + '.objectColorRGB', a1[0])
cmds.disconnectAttr(sel[0] + '.worldMatrix', a2[0])
cmds.disconnectAttr(sel[0] + '.lockInfluenceWeights', a3[0])
skin_num = cmds.listConnections(sel[1] + '.worldMatrix', p=True) #各スキンクラスターの番号と格納アドレスの二つを取得する。
print skin_num

for n in range(len(skin_num)):
	skin_numA = int(skin_num[n].split('skinCluster')[-1].split('.')[0])
	skin_numB = int(skin_num[n].split('[')[-1].split(']')[0])
	numA = format(skin_numA)
	numB = '[' + format(skin_numB) + ']'
	cmds.connectAttr(sel[0] + '.objectColorRGB', 'skinCluster' + numA + '.influenceColor' + numB, f=True)
	cmds.connectAttr(sel[0] + '.worldMatrix[0]', 'skinCluster' + numA + '.matrix' + numB, f=True)
	cmds.connectAttr(sel[0] + '.lockInfluenceWeights', 'skinCluster' + numA + '.lockWeights' + numB, f=True)
	cmds.setAttr('skinCluster' + numA + '.bindPreMatrix' + numB, new_j, type='matrix') #