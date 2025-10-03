import flet as ft
import cv2
import base64
import numpy as np
from ultralytics import YOLO

from photo_picker import PhotoPicker

class LayoutControl(ft.Container):
  def __init__(self, page):
    super().__init__()

    self.padding = 10

    self.photo = None

    # ファイル読み込みボタン
    self.file_btn = ft.FilledButton(
      "ファイル選択",
      on_click=lambda _: self.file_picker.pick_files(allow_multiple=False),
    )

    # ファイル読み込みダイアログ
    self.file_picker = ft.FilePicker(on_result=self.pick_files_result)
    page.overlay.append(self.file_picker)

    # 写真撮影ボタン
    self.photo_btn = ft.FilledButton(
      "写真を撮る",
      on_click=lambda _: [page.open(self.photo_picker), self.photo_picker.start_camera()],
    )

    # 写真撮影ダイアログ
    self.photo_picker = PhotoPicker(page, on_result=self.take_photo_result)

    # 画像表示（検出前）
    self.before_display = ft.Image(src=False, fit=ft.ImageFit.SCALE_DOWN)

    # 物体検出ボタン
    self.yolo_btn = ft.FilledButton(
      "物体検出", on_click=self.execute_yolo, visible=False
    )

    # 画像表示（検出後）
    self.after_display = ft.Image(src=False, fit=ft.ImageFit.SCALE_DOWN)

    # テーブル
    self.table = ft.DataTable(
      columns=[
        ft.DataColumn(ft.Text("クラス名")),
        ft.DataColumn(ft.Text("クラスID")),
        ft.DataColumn(ft.Text("信頼度")),
      ],
      rows=[],
      visible=False,
    )

    # view ------------------------------
    self.content = ft.Column([
      ft.Row(
        [
          self.file_btn,
          ft.Text("or"),
          self.photo_btn,
        ]
      ),
      ft.Row([
        ft.Column([
          self.before_display,
          self.yolo_btn,
        ]),
        self.after_display,
        self.table,
      ])
    ])


  # ファイル読み込み ------------------------------
  def pick_files_result(self, e: ft.FilePickerResultEvent):
    if e.files:
      selected_photo = cv2.imdecode(
        np.fromfile(e.files[0].path, dtype=np.uint8),
        cv2.IMREAD_UNCHANGED
      )
      self.load_photo(selected_photo)
      self.page.update()
        
    
  # 写真撮影 ------------------------------
  def take_photo_result(self, frame):
    self.load_photo(frame)
    self.page.update()


  # 写真を読み込んで表示 ------------------------------
  def load_photo(self, photo):
    self.photo = photo
    retval, encoded_photo = cv2.imencode(".jpg", photo)
    if retval:
      data_base64 = base64.b64encode(encoded_photo)
      data_base64 = data_base64.decode()
      self.before_display.src_base64 = data_base64
      self.yolo_btn.visible = True
      self.after_display.src_base64 = ""
      self.table.visible = False


  # 物体検出 ------------------------------
  def execute_yolo(self, e):
    model = YOLO("yolo11n.pt")
    results = model(self.photo)

    # image
    img = results[0].plot()
    ret, dst_data = cv2.imencode('.jpg', img)
    dst_str = base64.b64encode(dst_data)
    self.after_display.src_base64 = dst_str.decode()

    # class
    df = results[0].to_df()
    self.table.rows = []
    for data in df.to_numpy():
      self.table.rows.append(
        ft.DataRow(
          cells=[
            ft.DataCell(ft.Text(data[0])),
            ft.DataCell(ft.Text(data[1])),
            ft.DataCell(ft.Text(data[2])),
          ]
        )
      )
    self.table.visible = True
    self.page.update()