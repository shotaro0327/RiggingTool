# === GIDE Mirror GUI for Maya (PySide2) ===
# 目的：MyClass.mainA / mainB をボタンで実行
# 前提：gide_joint_conection.py に MyClass が定義されていること
# 追加推奨：MyClass.__init__ に self.gide_joint_path を追加し、
# gide_connection() 内のパスを self.gide_joint_path に変更

from maya import cmds
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore
import importlib
import sys
import os

# ==== 1) MyClass の読み込み ====
# ここは環境に合わせて編集（例：あなたの実ファイル置き場）
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
#MODULE_DIR = os.path.join(script_dir, "gide_joint")  # 例
if MODULE_DIR and MODULE_DIR not in sys.path:
    sys.path.append(MODULE_DIR)

import gide_joint_conection
importlib.reload(gide_joint_conection)
from gide_joint_conection import MyClass   # ← あなたのクラス

# ==== 2) Maya メインウィンドウを PySide2 にラップ ====
def get_maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)

# ==== 3) 本体ウィジェット ====
class GideMirrorWidget(QtWidgets.QDialog):
    WINDOW_TITLE = "GIDE Mirror Tool"

    def __init__(self, parent=None):
        super(GideMirrorWidget, self).__init__(parent or get_maya_main_window())
        self.setObjectName(self.WINDOW_TITLE.replace(" ", "_"))
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumWidth(420)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

        # MyClass のインスタンス
        self.tool = MyClass()

        # --- UI 構築 ---
        self._build_ui()
        self._make_connections()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # gide_joint.txt のパス入力
        path_row = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit()
        # 推奨改造を入れた場合：現在値を反映
        if hasattr(self.tool, "gide_joint_path"):
            self.path_edit.setText(self.tool.gide_joint_path)
        browse_btn = QtWidgets.QPushButton("Browse...")
        path_row.addWidget(QtWidgets.QLabel("gide_joint.txt:"))
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(browse_btn)
        self.browse_btn = browse_btn

        # ボタン群
        btn_row = QtWidgets.QHBoxLayout()
        self.setup_btn = QtWidgets.QPushButton("▶ Setup ")
        self.cleanup_btn = QtWidgets.QPushButton("⟲ Cleanup ")
        btn_row.addWidget(self.setup_btn, 1)
        btn_row.addWidget(self.cleanup_btn, 1)

        # ステータス表示
        self.status_lbl = QtWidgets.QLabel("Ready.")
        self.status_lbl.setStyleSheet("color: #8ae234;")  # 緑っぽい

        # 配置
        layout.addLayout(path_row)
        layout.addSpacing(8)
        layout.addLayout(btn_row)
        layout.addSpacing(6)
        layout.addWidget(self.status_lbl)

    def _make_connections(self):
        self.browse_btn.clicked.connect(self._on_browse)
        self.setup_btn.clicked.connect(self._on_setup)
        self.cleanup_btn.clicked.connect(self._on_cleanup)

    # --- ファイル選択 ---
    def _on_browse(self):
        start_dir = os.path.dirname(self.path_edit.text()) if self.path_edit.text() else os.path.expanduser("~")
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select gide_joint.txt", start_dir, "Text Files (*.txt);;All Files (*.*)")
        if path:
            self.path_edit.setText(path)

    # --- 実行ラッパ（Undo チャンク + 例外処理） ---
    def _run_with_undo(self, func, label):
        # パスを MyClass に反映（推奨改造を入れている前提）
        if hasattr(self.tool, "gide_joint_path"):
            self.tool.gide_joint_path = self.path_edit.text().strip()

        cmds.undoInfo(openChunk=True, chunkName=label)
        try:
            func()
            self._set_status(f"{label} done.", ok=True)
        except Exception as e:
            self._set_status(f"{label} failed: {e}", ok=False)
            raise
        finally:
            cmds.undoInfo(closeChunk=True)

    def _on_setup(self):
        self._run_with_undo(self.tool.mainA, "Setup")

    def _on_cleanup(self):
        self._run_with_undo(self.tool.mainB, "Cleanup")

    def _set_status(self, text, ok=True):
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet("color: %s;" % ("#8ae234" if ok else "#ef2929"))

# ==== 4) ウィンドウを一回だけ出すユーティリティ ====
def show_gide_mirror():
    # 既存があれば閉じる
    for w in QtWidgets.QApplication.topLevelWidgets():
        if isinstance(w, GideMirrorWidget):
            try:
                w.close()
            except:
                pass
    dlg = GideMirrorWidget()
    dlg.show()
    return dlg

# 実行
#show_gide_mirror()
