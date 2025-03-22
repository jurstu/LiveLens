from nicegui import ui, events, app
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
        self.controls = {}
        self.spawnGui()

    def run(self):
        self.t = threading.Thread(target=self.host, daemon=True)
        self.t.start()

    def host(self):
        ui.run(reload=False, show=False)


    def spawnGui(self):
        dark = ui.dark_mode()
        dark.enable()
        src = 'https://picsum.photos/id/563/720/480'
        with ui.row():
            with ui.column():
                with ui.card():
                    self.controls["tracking_image"] = ui.interactive_image(src).classes('w-full h-full')
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


        @app.get('/video/frame', response_class=Response)
        def grabVideoFrame() -> Response:
            _, raw = cv2.imencode(".jpg", self.lastImage)      
            return Response(content=raw.tobytes(), media_type="image/jpg") 

        ui.timer(interval=0.033, callback=lambda: self.controls["tracking_image"].set_source(f'/video/frame?{time.time()}'))   

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