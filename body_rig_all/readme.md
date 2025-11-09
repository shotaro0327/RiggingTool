# Maya 自動リグ生成ツール（Auto Rig Generator）

このプロジェクトは、**Autodesk Maya 向けの自動リグ生成システム**です。  
ガイドの配置から、スケルトン（ジョイント）の自動作成、コントローラの生成、FK/IK 切り替え、スイッチ制御などを Python スクリプトで自動化し、
**キャラクターリグ構築の効率化**を目的としています。

---

## 🎯 概要

このツールは、CGアニメーション業界での制作業務の中で生まれました。  
手作業で行っていた複雑なリギング工程を自動化し、**作業時間を短縮**しつつ、**安定した品質のリグ**を量産できるように設計しています。

このスクリプト群は Maya の `maya.cmds` API を使用しており、  
**Python のプログラミングスキル**と **3Dリグ構造の理解**の両方を活かして作成しました。

---

## ⚙️ 主な機能

### ① ガイド配置・左右ミラー補助 🎛
- gide_joint_conection.py  
- gide_joint_conection_UI.py  

キャラクターに合わせてガイドを置く際、L側を動かすだけでR側も反転して動く  
「ガイドミラー」機能を提供。  
PySide2 GUIにより、Setup/Cleanupも1クリック。

### ② 腕・脚のFK/IKコントローラ作成 💪🦵
- create_all_ctrl.py
- **腕・脚のコントローラ**を自動生成（FK + IK 両対応）  
- 左右のコントローラを自動的にミラーリングして作成  
- **足のロール・つま先の回転・ヒールチルト**などの制御属性を自動追加

### ③ ベンドジョイント生成（リボンシステム）🧩  
- create_bend.py
- 腕・脚などに使用される **ベンドジョイント（bendy joint）** の自動生成  
- **NURBSリボン** を利用したスムーズな変形表現  
- **フォリクル（follicle）ノード**の自動作成により、安定したスキン挙動を実現

### ④ 体幹コントローラ生成 💀
- body_ctrl.py
- 背骨（spine）や首（neck）のコントローラ生成
- **FK / IK / Micro** コントロールの自動作成  
- `maintainVolume` や `IK_ctrl` などの属性を付与して操作性を向上

### ⑤ フォロー制御 + FK/IKスイッチ 🤝
- combine_ctrl.py
- 体幹と四肢（腕・脚）のリグを統合  
- **条件ノード（condition node）** による FK / IK スイッチシステムを構築  
- 各部位のフォロー（Follow）設定を自動で接続

### ⑥ 階層整理・バインドジョイントセットアップ 📂
- AutoRigHierarchySetup.py
- 最終的にバインド用ジョイント階層を整理し、  
`segmentScaleCompensate = 0` へ統一。  
安定したスケール挙動を実現。

### ⑦ ストレッチIK 🏋️
- create_stretch_all.py
- 腕の IK チェーンに距離ベースの Stretch を付与します。`distanceDimension` と カーブの `arcLength` を比較し、
`condition(Greater Than)` の出力で 上腕/肘/手首 の `scaleX` を駆動します。  
実行すると、補助ノードは `stretch_curve_gp`（controls_grp配下）と `stretch_distance_gp`（rig_grp配下）に自動整理されます

---

## 🧠 技術的特徴

| 項目 | 内容 |
|------|------|
| 使用言語 | Python 3（Maya Embedded） |
| 開発環境 | Autodesk Maya |
| 使用API | `maya.cmds` |
| 開発スタイル | モジュール分割型（各機能を独立ファイルとして管理） |
| 数学処理 | ベクトル計算・距離計算・補間（interpolation）などを使用 |
| 色分け機能 | 各リグ要素に視覚的な識別のための RGB カラー設定を付与 |

---

## 🧩 ファイル構成
```
/body_rig_all/
├── ctrl_gide # 対象のキャラクターに合わせて骨を生成するためのガイドジョイント
├── gide_joint # ガイド配置・左右ミラー補助 
├── create_bend.py # ベンドジョイントとリボンシステムの作成
├── body_ctrl.py # 背骨・首のコントローラ生成
├── create_all_ctrl.py # 腕・脚のコントローラ生成（FK/IK対応）
├── combine_ctrl.py # 全体統合とスイッチ制御
├── AutoRigHierarchySetup.py # 階層整理・バインドジョイントセットアップ
├── create_stretch_all.py # 足と腕にIKストレッチを作成
└── README_JP.md # 日本語版の説明書（このファイル）
```
