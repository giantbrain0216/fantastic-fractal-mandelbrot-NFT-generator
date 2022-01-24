from mandelbrot import Mandelbrot
import timeit

mand = Mandelbrot(maxiter=5000, rgb_thetas=[.11, .02, .92], stripe_s=2, xpixels=100)
# Point to zoom at
x_real = (-1.748764513-1.748764512)/2
x_imag = (-0.0000000174-0.0000000173)/2
start = timeit.default_timer()
mand.animate(x_real, x_imag, 'mandelbrot.gif', 100)
stop = timeit.default_timer()
# print(x_real, x_imag)

print(stop-start)
