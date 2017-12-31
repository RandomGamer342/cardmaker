from common import Model

class Figure(Model):
    filename = ""
    source = ""
        # material-icons = https://material.io/icons/
        # mdi            = https://materialdesignicons.com/
        # fa             = http://fontawesome.io/icons/
        # svg            = the svgs/ folder
    color = "aaa"
    top = 0.
    bottom = 0.
    left = 0.
    right = 0.
    size = 100.

    def __init__(self, line, source = ""):
        data = line.split(",")
        self.filename = data[0].strip()
        if len(data) > 1:
            for key, val in [[y.strip() for y in x.split(":")] for x in data[1:]]:
                if key in ("top", "bottom", "left", "right", "size"):
                    val = float(val)
                setattr(self, key, val)

        if not self.source:
            self.source = source

        l = 0
        r = 0
        t = 0
        b = 0
        s = 100

        s = s - self.top - self.bottom
        l += (self.top + self.bottom) / 2
        r += (self.top + self.bottom) / 2

        if self.left <= r:
            r -= self.left
        else:
            temp = self.left - r
            r = 0
            s -= temp
            t += temp / 2
            b += temp / 2

        if self.right <= l:
            l -= self.right
        else:
            temp = self.right - l
            l = 0
            s -= temp
            t += temp / 2
            b += temp / 2

        self.top += t
        self.bottom += b
        self.left += l
        self.right += r
        self.size = s
