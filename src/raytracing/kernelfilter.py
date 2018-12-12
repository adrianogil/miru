
class KernelFilter:
    """
        KernelFilter for each color channels
    """
    def __init__(self, kernel, sizex, sizey):
        self.kernel = kernel
        self.filter_size_x = sizex
        self.filter_size_y = sizey

    def apply_effect(self, render_data):
        for x in range(0, render_data.pixel_width):
            for y in range(0, render_data.pixel_height):
                
                colors = [0,0,0]

                for c in range(0, 3):

                    sum_kernel = 0.0

                    for fx in range(0, self.filter_size_x):
                        for fy in range(0, self.filter_size_y):
                            ix = int(x + fx - 0.5*self.filter_size_x)
                            iy = int(y + fy - 0.5*self.filter_size_y)

                            if ix >= 0 and ix < render_data.pixel_width and \
                               iy >= 0 and iy < render_data.pixel_height:
                               
                               sum_kernel = sum_kernel + self.kernel[fx,fy]*float(render_data.pixels[ix,iy][c])

                    colors[c] = int(sum_kernel)

                # print(str(colors))
                render_data.pixels[x,y] = tuple(colors)
