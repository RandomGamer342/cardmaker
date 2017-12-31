from common import Model

class Figure(Model):
    filename = ""
    source = ""
        # material-icons = https://material.io/icons/
        # mdi            = https://materialdesignicons.com/
        # fa             = http://fontawesome.io/icons/
        # svg            = the svgs/ folder
    color = ""
    top = 0
    bottom = 0
    left = 0
    right = 0
    size = 0
    autoscale = True
    scale = 100.
    width = 0
    height = 0
    rotate = 0

    def __init__(self, line, source = ""):
        data = line.split(",")
        self.filename = data[0].strip()
        if len(data) > 1:
            for key, val in [[y.strip() for y in x.split(":")] for x in data[1:]]:
                if key in ("width", "height", "size", "autoscale"):
                    continue
                elif key in ("top", "bottom", "left", "right", "scale"):
                    if key == "scale" and val != "auto":
                        self.autoscale = False
                    val = float(val)
                elif key in ("rotate"):
                    val = int(val)
                if key:
                    setattr(self, key, val)

        if not self.source:
            self.source = source

        if self.autoscale and self.top + self.bottom + self.left + self.right > 0:
            l = 0
            r = 0
            t = 0
            b = 0
            s = 0

            if self.top + self.bottom > self.left + self.right:
                s = self.top + self.bottom
                l += (self.top + self.bottom) / 2
                r += (self.top + self.bottom) / 2
                ratio_t = self.top / s
                ratio_b = self.bottom / s

                if self.left <= r:
                    r -= self.left
                else:
                    temp = self.left - r
                    r = 0
                    s += temp
                    t += temp * ratio_t
                    b += temp * ratio_b

                if self.right <= l:
                    l -= self.right
                else:
                    temp = self.right - l
                    l = 0
                    s += temp
                    t += temp / 2
                    b += temp / 2
            else:
                s = self.left + self.right
                t += (self.left + self.right) / 2
                b += (self.left + self.right) / 2
                ratio_l = self.left / s
                ratio_r = self.right / s

                if self.top <= b:
                    b -= self.top
                else:
                    temp = self.top - b
                    b = 0
                    s += temp
                    l += temp * ratio_l
                    r += temp * ratio_r

                if self.bottom <= t:
                    t -= self.bottom
                else:
                    temp = self.bottom - t
                    t = 0
                    s += temp
                    l += temp * ratio_l
                    r += temp * ratio_r

            self.top += t
            self.bottom += b
            self.left += l
            self.right += r
            self.size = s
