#arnold>vrayMat
#create by shotaro_yamana
# -*- coding: UTF-8 -*-
import maya.cmds as cmds

def exchange(now_m, next_m, inputNode, outputNode):

    sel = cmds.ls(type = now_m)

    for s in sel:
        cmds.hyperShade(objects = s)
        shapes = cmds.ls(sl=1)
        next = cmds.shadingNode(next_m, name=s, asShader=True)
        SG = cmds.sets(renderable=1, noSurfaceShader=1, empty=1, name=('%sSG' % next)) #shadingEngine作成
        cmds.connectAttr(next + ".outColor", SG + ".surfaceShader", force=1)
        
        for i in range(len(inputNode)):
            texture = cmds.listConnections(s + "." + inputNode[i], scn=True, plugs=True) #繋がってるアトリビュートごと取得
            
            if inputNode[i] == "normalCamera": #Arnoldのバンプノードのとき bumpMap
                bump = cmds.listConnections(s + "." + inputNode[i], scn=False, plugs=False)
                print(bump)
                if bump is not None:
                    bump_type = cmds.getAttr(bump[0] + ".bumpInterp")
                    print(bump_type)
                    if bump_type == 0:
                        new_bump = cmds.setAttr(next + ".bumpMapType", 0)
                    elif bump_type == 1:
                        new_bump = cmds.setAttr(next + ".bumpMapType", 1)
            
            if texture == None:
                nowParameter = cmds.getAttr(s + "." + inputNode[i])
                nextParameter = cmds.getAttr(next + "." + outputNode[i])
                nowParameterType = cmds.getAttr(s + "." + inputNode[i], type=True)
                nextParameterType = cmds.getAttr(next + "." + outputNode[i], type=True)
                
                if nowParameterType == nextParameterType:
                    if nowParameterType == "float":
                        answer = nowParameter
                        cmds.setAttr(next + "." + outputNode[i], answer)
                    elif nowParameterType == "float3":
                        answer = nowParameter[0]
                        cmds.setAttr(next + "." + outputNode[i] ,answer[0], answer[1], answer[2])
                    
                elif nowParameterType == "float" and nextParameterType == "float3": #同じ値を入れる。
                    answer = (nowParameter, nowParameter, nowParameter)
                    cmds.setAttr(next + "." + outputNode[i] ,answer[0], answer[1], answer[2])
                
                elif nowParameterType == "float3" and nextParameterType == "float": #値の平均をとる。
                    answer = 0
                    for n in nowParameter[0]:
                        answer += n
                    answer /= len(nowParameter[0])
                    cmds.setAttr(next + "." + outputNode[i], answer)
                    
                if inputNode[i] == "emissionColor": #Arnoldのemmisonは二つあるので
                    arnold_em = cmds.getAttr(s + ".emission")
                    answer = (arnold_em, arnold_em, arnold_em)
                    cmds.setAttr(next + "." + outputNode[i] ,answer[0], answer[1], answer[2])
                
            else:
                
                if inputNode[i] == "normalCamera": #バンプの時、vrayはbump2dを間に挟まない。
                    bump2d = cmds.listConnections(s + "." + inputNode[i], scn=False, plugs=False)
                    bump_texture = cmds.listConnections(bump2d[0] + ".bumpValue")
                    cmds.connectAttr(bump_texture[0] + ".outColor", next + "." + outputNode[i], f=1)#
                    
                else:
                    if outputNode[i] != "bumpMap":
                        cmds.connectAttr(texture[0], next + "." + outputNode[i], f=1)#
                    
                cmds.disconnectAttr(texture[0], s + "." + inputNode[i])#
                
        cmds.setAttr(next + ".useRoughness", 1)
                
        
        cmds.hyperShade(objects=s)
        cmds.sets(e=1, forceElement=SG)
        
        cmds.delete(s)
       
    print ("#####__FINISH__#####")
    
now_m = "aiStandardSurface"
next_m = "VRayMtl"
input_at = ["baseColor", "emissionColor", "specularColor", "specularRoughness", "normalCamera", "metalness"] 
output_at = ["color", "illumColor", "reflectionColor", "reflectionGlossiness", "bumpMap", "metalness"]    
exchange(now_m, next_m, input_at, output_at)