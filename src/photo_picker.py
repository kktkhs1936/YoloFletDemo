import flet as ft
import cv2
import base64


class PhotoPicker(ft.AlertDialog):
  def __init__(self, page, on_result):
    super().__init__()

    self.page = page
    self.on_result = on_result

    self.capture = None
    self.camera_is_used = False
    self.photo_is_taken = False

    self.image_display = ft.Image(src=False, fit=ft.ImageFit.SCALE_DOWN)

    self.content = ft.Column([
      self.image_display,
      ft.Row(
        [
          ft.FilledButton("撮影", on_click=self.take_photo),
          ft.FilledButton("キャンセル", on_click=self.cancel_photo),
        ]
      )
    ])

  def cancel_photo(self, e):
    self.camera_is_used = False
    self.photo_is_taken = False
    self.page.close(self)

  def take_photo(self, e):
    self.camera_is_used = False
    self.photo_is_taken = True
    self.page.close(self)

  def start_camera(self):
    self.capture = cv2.VideoCapture(0)
    self.camera_is_used = True
    while self.capture.isOpened() & self.camera_is_used:
      success, frame = self.capture.read()
      retval, encoded_frame = cv2.imencode(".jpg", frame)
      data = base64.b64encode(encoded_frame)
      data_str = data.decode()
      self.image_display.src_base64 = data_str
      self.page.update()
      if success:
        pass
      else:
        break
    if self.photo_is_taken:
      self.on_result(frame)
    #   self.photo = frame
    #   self.before_display.src_base64 = data_str
    #   yolo_control.after_display.src_base64 = ""
    #   yolo_control.yolo_btn.visible = True
    #   yolo_control.table.visible = False
    # image_picker.image_display.src = False
    # image_picker.image_display.src_base64 = ""
    self.capture.release()
    cv2.destroyAllWindows()
    self.page.update()