

class OSD:
    def __init__(self):
        self.objects = []

    def addRect(self, x, y, w, h, color):
        rect = {
            "type": "rect",
            "x": x,
            "y": y, 
            "w": w,
            "h": h,
            "color": color
        }
        self.objects.append(rect)

    def addText(self, x, y, size, color, readValue, format):
        t = {
            "type": "text",
            "x": x,  
            "y": y,  
            "size": size,  
            "color": color,  
            "readValue": readValue,
            "format": format
        }
        self.objects.append(t)


    
