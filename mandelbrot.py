

import math
import numpy as np
import matplotlib.pyplot as plt
from numba import jit
from matplotlib.widgets import Slider, Button
from numba import cuda
from PIL import Image
import imageio


def sin_colortable(rgb_thetas=[.85, .0, .15], ncol=2**12):
    def colormap(x, rgb_thetas):

        y = np.column_stack(((x + rgb_thetas[0]) * 2 * math.pi,
                             (x + rgb_thetas[1]) * 2 * math.pi,
                             (x + rgb_thetas[2]) * 2 * math.pi))

        val = 0.5 + 0.5*np.sin(y)
        return val
    return colormap(np.linspace(0, 1, ncol), rgb_thetas)


@jit(nopython=True)
def blinn_phong(normal, light):
    normal = normal / abs(normal)

    ldiff = (normal.real*math.cos(light[0])*math.cos(light[1]) +
             normal.imag*math.sin(light[0])*math.cos(light[1]) +
             1*math.sin(light[1]))
    ldiff = ldiff/(1+1*math.sin(light[1]))

    phi_half = (math.pi/2 + light[1])/2
    lspec = (normal.real*math.cos(light[0])*math.sin(phi_half) +
             normal.imag*math.sin(light[0])*math.sin(phi_half) +
             1*math.cos(phi_half))
    lspec = lspec/(1+1*math.cos(phi_half))
    lspec = lspec ** light[6]

    bright = light[3] + light[4]*ldiff + light[5]*lspec
    bright = bright * light[2] + (1-light[2])/2
    return(bright)


@jit(nopython=True)
def smooth_iter(c, maxiter, stripe_s, stripe_sig):
    esc_radius_2 = 10**10
    z = complex(0, 0)

    stripe = (stripe_s > 0) and (stripe_sig > 0)
    stripe_a = 0
    dz = 1+0j

    for n in range(maxiter):
        dz = dz*2*z + 1
        z = z*z + c
        if stripe:
            stripe_t = (math.sin(stripe_s*math.atan2(z.imag, z.real)) + 1) / 2

        if z.real*z.real + z.imag*z.imag > esc_radius_2:

            modz = abs(z)
            log_ratio = 2*math.log(modz)/math.log(esc_radius_2)
            smooth_i = 1 - math.log(log_ratio)/math.log(2)

            if stripe:
                stripe_a = (stripe_a * (1 + smooth_i * (stripe_sig-1)) +
                            stripe_t * smooth_i * (1 - stripe_sig))
                stripe_a = stripe_a / (1 - stripe_sig**n *
                                       (1 + smooth_i * (stripe_sig-1)))

            u = z/dz
            normal = u

            dem = modz * math.log(modz) / abs(dz) / 2

            return (n+smooth_i, stripe_a, dem, normal)

        if stripe:
            stripe_a = stripe_a * stripe_sig + stripe_t * (1-stripe_sig)

    return (0, 0, 0, 0)


@jit(nopython=True)
def color_pixel(matxy, niter, stripe_a, step_s, dem, normal, colortable,
                ncycle, light):

    ncol = colortable.shape[0] - 1
    niter = math.sqrt(niter) % ncycle / ncycle
    col_i = round(niter * ncol)

    def overlay(x, y, gamma):
        if (2*y) < 1:
            out = 2*x*y
        else:
            out = 1 - 2 * (1 - x) * (1 - y)
        return out * gamma + x * (1-gamma)

    bright = blinn_phong(normal, light)

    dem = -math.log(dem)/12
    dem = 1/(1+math.exp(-10*((2*dem-1)/2)))

    nshader = 0
    shader = 0
    if stripe_a > 0:

        nshader += 1
        shader = shader + stripe_a

    if step_s > 0:

        step_s = 1/step_s
        col_i = round((niter - niter % step_s) * ncol)

        x = niter % step_s / step_s
        light_step = 6*(1-x**5-(1-x)**100)/10

        step_s = step_s/8
        x = niter % step_s / step_s
        light_step2 = 6*(1-x**5-(1-x)**30)/10

        light_step = overlay(light_step2, light_step, 1)
        nshader += 1
        shader = shader + light_step

    if nshader > 0:
        bright = overlay(bright, shader/nshader, 1) * (1-dem) + dem * bright

    for i in range(3):

        matxy[i] = colortable[col_i, i]

        matxy[i] = overlay(matxy[i], bright, 1)

        matxy[i] = max(0, min(1, matxy[i]))


@jit(nopython=True)
def compute_set(creal, cim, maxiter, colortable, ncycle, stripe_s, stripe_sig,
                step_s, diag, light):
    xpixels = len(creal)
    ypixels = len(cim)

    mat = np.zeros((ypixels, xpixels, 3))

    for x in range(xpixels):
        for y in range(ypixels):

            c = complex(creal[x], cim[y])

            niter, stripe_a, dem, normal = smooth_iter(c, maxiter, stripe_s,
                                                       stripe_sig)

            if niter > 0:

                color_pixel(mat[y, x, ], niter, stripe_a, step_s, dem/diag,
                            normal, colortable,
                            ncycle, light)
    return mat


@cuda.jit
def compute_set_gpu(mat, xmin, xmax, ymin, ymax, maxiter, colortable, ncycle,
                    stripe_s, stripe_sig, step_s, diag, light):

    index = cuda.grid(1)
    x, y = index % mat.shape[1], index // mat.shape[1]

    if (y < mat.shape[0]) and (x < mat.shape[1]):

        creal = xmin + x / (mat.shape[1] - 1) * (xmax - xmin)
        cim = ymin + y / (mat.shape[0] - 1) * (ymax - ymin)

        c = complex(creal, cim)

        niter, stripe_a, dem, normal = smooth_iter(c, maxiter, stripe_s,
                                                   stripe_sig)

        if niter > 0:
            color_pixel(mat[y, x, ], niter, stripe_a, step_s, dem/diag, normal,
                        colortable, ncycle, light)


class Mandelbrot():

    def __init__(self, xpixels=1280, maxiter=500,
                 coord=[-2.6, 1.845, -1.25, 1.25], gpu=True, ncycle=32,
                 rgb_thetas=[.0, .15, .25], oversampling=3, stripe_s=0,
                 stripe_sig=.9, step_s=0,
                 light=[.125, .5, .75, .2, .5, .5, 20]):
        self.range = []
        self.xpixels = xpixels
        self.maxiter = maxiter
        self.coord = coord
        self.gpu = gpu
        self.ncycle = ncycle
        self.os = oversampling
        self.rgb_thetas = rgb_thetas
        self.stripe_s = stripe_s
        self.stripe_sig = stripe_sig
        self.step_s = step_s

        self.light = np.array(light)
        self.light[0] = 2*math.pi*self.light[0]
        self.light[1] = math.pi/2*self.light[1]

        self.ypixels = round(self.xpixels / (self.coord[1]-self.coord[0]) *
                             (self.coord[3]-self.coord[2]))

        self.colortable = sin_colortable(self.rgb_thetas)

        self.update_set()

    def update_set(self):

        ncycle = math.sqrt(self.ncycle)
        diag = math.sqrt((self.coord[1]-self.coord[0])**2 +
                         (self.coord[3]-self.coord[2])**2)

        xp = self.xpixels*self.os
        yp = self.ypixels*self.os

        if(self.gpu):

            self.set = np.zeros((yp, xp, 3))

            npixels = xp * yp
            nthread = 32
            nblock = math.ceil(npixels / nthread)
            compute_set_gpu[nblock,
                            nthread](self.set, *self.coord, self.maxiter,
                                     self.colortable, ncycle, self.stripe_s,
                                     self.stripe_sig, self.step_s, diag,
                                     self.light)
        else:

            creal = np.linspace(self.coord[0], self.coord[1], xp)
            cim = np.linspace(self.coord[2], self.coord[3], yp)

            self.set = compute_set(creal, cim, self.maxiter,
                                   self.colortable, ncycle, self.stripe_s,
                                   self.stripe_sig, self.step_s, diag,
                                   self.light)
        self.set = (255*self.set).astype(np.uint8)

        if self.os > 1:
            self.set = (self.set
                        .reshape((self.ypixels, self.os,
                                  self.xpixels, self.os, 3))
                        .mean(3).mean(1).astype(np.uint8))

    def draw(self, filename=None):

        img = Image.fromarray(self.set[::-1, :, :], 'RGB')
        if filename is not None:
            img.save(filename)
        else:
            img.show()

    def draw_mpl(self, filename=None, dpi=72):
        plt.subplots(figsize=(self.xpixels/dpi, self.ypixels/dpi))
        plt.imshow(self.set, extent=self.coord, origin='lower')

        plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        plt.axis('off')

        if filename is not None:
            plt.savefig(filename, dpi=dpi)
        else:
            plt.show()

    def zoom_at(self, x, y, s):
        xrange = (self.coord[1] - self.coord[0])/2
        yrange = (self.coord[3] - self.coord[2])/2
        self.coord = [x - xrange * s,
                      x + xrange * s,
                      y - yrange * s,
                      y + yrange * s]

    def szoom_at(self, x, y, s):
        xrange = (self.coord[1] - self.coord[0])/2
        yrange = (self.coord[3] - self.coord[2])/2
        x = x * (1-s**2) + (self.coord[1] + self.coord[0])/2 * s**2
        y = y * (1-s**2) + (self.coord[3] + self.coord[2])/2 * s**2
        self.coord = [x - xrange * s,
                      x + xrange * s,
                      y - yrange * s,
                      y + yrange * s]

    def animate(self, x, y, file_out, n_frames=150, loop=True):

        def gaussian(n, sig=1):
            x = np.linspace(-1, 1, n)
            return np.exp(-np.power(x, 2.) / (2 * np.power(sig, 2.)))
        s = 1 - gaussian(n_frames, 1/2)*.3

        self.update_set()
        images = [self.set]

        for i in range(1, n_frames):

            self.szoom_at(x, y, s[i])

            self.update_set()
            images.append(self.set)

        if(loop):
            images += images[::-2]

        imageio.mimsave(file_out, images)

    def explore(self, dpi=72):

        self.explorer = Mandelbrot_explorer(self, dpi)


class Mandelbrot_explorer():

    def __init__(self, mand, dpi=172):
        self.mand = mand

        self.mand.update_set()

        self.fig, self.ax = plt.subplots(figsize=(mand.xpixels/dpi,
                                                  mand.ypixels/dpi))
        self.graph = plt.imshow(mand.set,
                                extent=mand.coord, origin='lower')
        plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        plt.axis('off')

        self.sld_maxit = Slider(plt.axes([0.1, 0.005, 0.2, 0.02]), 'Iterations',
                                0, 5000, mand.maxiter, valstep=5)
        self.sld_maxit.on_changed(self.update_val)
        self.sld_r = Slider(plt.axes([0.1, 0.04, 0.2, 0.02]), 'R',
                            0, 1, mand.rgb_thetas[0], valstep=.001)
        self.sld_r.on_changed(self.update_val)
        self.sld_g = Slider(plt.axes([0.1, 0.06, 0.2, 0.02]), 'G',
                            0, 1, mand.rgb_thetas[1], valstep=.001)
        self.sld_g.on_changed(self.update_val)
        self.sld_b = Slider(plt.axes([0.1, 0.08, 0.2, 0.02]), 'B',
                            0, 1, mand.rgb_thetas[2], valstep=.001)
        self.sld_b.on_changed(self.update_val)
        self.sld_n = Slider(plt.axes([0.1, 0.10, 0.2, 0.02]), 'ncycle',
                            0, 200, mand.ncycle, valstep=1)
        self.sld_n.on_changed(self.update_val)
        self.sld_p = Slider(plt.axes([0.1, 0.12, 0.2, 0.02]), 'phase',
                            0, 1, 0, valstep=0.001)
        self.sld_p.on_changed(self.update_val)
        self.sld_st = Slider(plt.axes([0.7, 0.19, 0.2, 0.02]), 'step_s',
                             0, 100, mand.step_s, valstep=1)
        self.sld_st.on_changed(self.update_val)
        self.sld_s = Slider(plt.axes([0.7, 0.17, 0.2, 0.02]), 'stripe_s',
                            0, 32, mand.stripe_s, valstep=1)
        self.sld_s.on_changed(self.update_val)
        self.sld_li1 = Slider(plt.axes([0.7, 0.14, 0.2, 0.02]), 'light_angle',
                              0, 1, mand.light[0]/(2*math.pi), valstep=.01)
        self.sld_li1.on_changed(self.update_val)
        self.sld_li2 = Slider(plt.axes([0.7, 0.12, 0.2, 0.02]), 'light_azim',
                              0, 1, mand.light[1]/(math.pi/2), valstep=.01)
        self.sld_li2.on_changed(self.update_val)
        self.sld_li3 = Slider(plt.axes([0.7, 0.10, 0.2, 0.02]), 'light_i',
                              0, 1, mand.light[2], valstep=.01)
        self.sld_li3.on_changed(self.update_val)
        self.sld_li4 = Slider(plt.axes([0.7, 0.08, 0.2, 0.02]), 'k_ambiant',
                              0, 1, mand.light[3], valstep=.01)
        self.sld_li4.on_changed(self.update_val)
        self.sld_li5 = Slider(plt.axes([0.7, 0.06, 0.2, 0.02]), 'k_diffuse',
                              0, 1, mand.light[4], valstep=.01)
        self.sld_li5.on_changed(self.update_val)
        self.sld_li6 = Slider(plt.axes([0.7, 0.04, 0.2, 0.02]), 'k_specular',
                              0, 1, mand.light[5], valstep=.01)
        self.sld_li6.on_changed(self.update_val)
        self.sld_li7 = Slider(plt.axes([0.7, 0.02, 0.2, 0.02]), 'shininess',
                              1, 100, mand.light[6], valstep=1)
        self.sld_li7.on_changed(self.update_val)

        self.coord = Button(
            plt.axes([0.9, 0.9, 0.1, 0.1]), 'Save Coordinate')
        self.coord.on_clicked(self.save_coord)

        plt.sca(self.ax)

        self.cid1 = self.fig.canvas.mpl_connect('scroll_event', self.onclick)
        self.cid2 = self.fig.canvas.mpl_connect('button_press_event',
                                                self.onclick)
        plt.show()

    def save_coord(self, val):

        self.mand.range = self.mand.coord
        plt.close()

    def update_val(self, val):
        rgb = [x + self.sld_p.val for x in [self.sld_r.val, self.sld_g.val,
                                            self.sld_b.val]]
        self.mand.rgb_thetas = rgb
        self.mand.colortable = sin_colortable(rgb)
        self.mand.maxiter = self.sld_maxit.val
        self.mand.ncycle = self.sld_n.val
        self.mand.stripe_s = self.sld_s.val
        self.mand.step_s = self.sld_st.val
        self.mand.light = np.array([2*math.pi*self.sld_li1.val,
                                    math.pi/2*self.sld_li2.val, self.sld_li3.val,
                                    self.sld_li4.val, self.sld_li5.val,
                                    self.sld_li6.val, self.sld_li7.val])
        self.mand.update_set()
        self.graph.set_data(self.mand.set)
        plt.draw()
        plt.show()

    def onclick(self, event):

        if event.inaxes == self.ax:

            zoom = 1/4
            if event.button in ('down', 3):

                zoom = 1/zoom

            self.mand.zoom_at(event.xdata, event.ydata, zoom)
            self.mand.update_set()

            self.graph.set_data(self.mand.set)
            self.graph.set_extent(self.mand.coord)
            plt.draw()
            plt.show()


if __name__ == "__main__":
    Mandelbrot().explore()
