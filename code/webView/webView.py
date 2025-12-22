from nicegui import ui, events, app
from nicegui.events import KeyEventArguments
from fastapi import Response
import os
import time
import numpy as np
import cv2
import threading
import json

class UiGen:
    def __init__(self, ww, hh):
        self.videoWW = ww
        self.videoHH = hh
        self.lastImage = np.empty((self.videoHH, self.videoWW, 3))
        self.lastImage[:] = 128
        self.controls = {}
        self.off_x = 0
        self.off_y = 0

        self.spawnGui()

    def run(self):
        self.t = threading.Thread(target=self.host, daemon=True)
        self.t.start()

    def host(self):
        ui.run(reload=False, show=False)


    def moveMarkerAndShowIt(self, lat, lon):
        self.controls["mapMarker"].move(lat, lon)
        self.controls["map"].set_center((lat, lon))

    def spawnGui(self):
        dark = ui.dark_mode()
        dark.enable()
        src = 'https://picsum.photos/id/563/720/480'

        with ui.row():
            with ui.column():
                with ui.card():
                    self.controls["tracking_image"] = ui.interactive_image(src).classes('w-full h-full')
                    self.startPosition = [0, 0]
                    with ui.card().classes("w-full no-wrap; shadow-lg; bg-gray-400").style('height: 480px; width: 1280px'):
                        self.controls["map"] = ui.leaflet(center=self.startPosition).classes('border full-width full-height')
                        self.controls["mapMarker"] = self.controls["map"].marker(latlng=self.startPosition)


            with ui.row():
                with ui.card() as debugCard:
                    debugCard.visible = True
                    with ui.column():
                        ui.label("debug card")

                        self.controls["markdownDebug"] = ui.markdown('''
                            
                        ''').style('white-space: pre-wrap')
                        

                        with ui.row():
                            ui.button('Dark', on_click=dark.enable)
                            ui.button('Light', on_click=dark.disable)






        keyboard = ui.keyboard(on_key=self.handle_key, active=True)


        @app.get('/video/frame', response_class=Response)
        def grabVideoFrame() -> Response:
            _, raw = cv2.imencode(".jpg", self.lastImage)      
            return Response(content=raw.tobytes(), media_type="image/jpg") 

        ui.timer(interval=0.033, callback=lambda: self.controls["tracking_image"].set_source(f'/video/frame?{time.time()}'))   

    def handle_key(self, e: KeyEventArguments):
        if e.action.keydown:
            if e.key.arrow_left:
                ui.notify('going left')
                self.off_x -= 5
            elif e.key.arrow_right:
                ui.notify('going right')
                self.off_x += 5
            elif e.key.arrow_up:
                ui.notify('going up')
                self.off_y -= 5
            elif e.key.arrow_down:
                ui.notify('going down')
                self.off_y +=5

    def setDebugData(self, data):
        try:
            d = data
            js = json.dumps(d, indent=4)
            self.controls["markdownDebug"].content = f"```javascript\n{js}\n```"
        except Exception as e:
            print(e)


if __name__ == "__main__":
    ug = UiGen(640, 480)
    ug.run()
    while(1):
        time.sleep(1)