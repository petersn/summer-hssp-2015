#! /usr/bin/python

# Set screen width and height.
W = H = 512

import numpy
import pygame
from pygame.locals import *
pygame.init()
screen = pygame.display.set_mode((W*2, H), FULLSCREEN)
clock = pygame.time.Clock()

time_domain = pygame.Surface((W, H))
time_domain.fill((0, 0, 0))

freq_domain = pygame.Surface((W, H))
freq_domain.fill((0, 0, 0))

holding = set()

mouse_x = mouse_y = 0
normalized_mode = False
vertical_mode = False
brush_size = 2

starting_image = 0
starting_cut = 0

print """
Controls:
	mouse left  -- Draw in time domain.
	mouse right -- Erase in time domain.
	c           -- Clear time domain.
	n           -- Toggle automatic normalization.
	ctrl+q      -- Grab snapshot.
	q           -- Shrink snapshot.
	g           -- Grow time domain.
	b           -- Blur out the image.
	s           -- Toggle brush size.
	v           -- Toggle vertical drawing mode.
	left shift  -- Multiply normalization by 10 for rendering.
	right shift -- Same as left shift (holding both multiplies by 100).
"""

while True:
	prev_x, prev_y = mouse_x, mouse_y
	mouse_x, mouse_y = pygame.mouse.get_pos()
	for event in pygame.event.get():
		if (event.type == QUIT) or (event.type == KEYDOWN and event.key == 27):
			pygame.quit()
			raise SystemExit
		if event.type == KEYDOWN:
			holding.add(event.key)
		if event.type == KEYUP:
			if event.key in holding:
				holding.remove(event.key)
		if event.type == MOUSEBUTTONDOWN:
			ind = ("m", event.button)
			holding.add(ind)
		if event.type == MOUSEBUTTONUP:
			ind = ("m", event.button)
			if ind in holding:
				holding.remove(ind)
		if event.type == KEYDOWN:
			if event.key == ord("c"):
				# Clear
				time_domain.fill((0, 0, 0))
			if event.key == ord("n"):
				# Change normalization mode
				normalized_mode = not normalized_mode
			if event.key == ord("q"):
				if K_LCTRL in holding:
					# Capture a starting image.
					starting_image = time_domain.copy()
					starting_cut = 0
			if event.key == ord("g"):
				# Grow.
				temp = time_domain.copy()
				temp.set_alpha(10)
				for x in xrange(-4, 5):
					time_domain.blit(temp, (x, 0), special_flags=BLEND_RGBA_ADD)
					time_domain.blit(temp, (0, x), special_flags=BLEND_RGBA_ADD)
			if event.key == ord("b"):
				# Blend.
				temp = time_domain.copy()
				temp.set_alpha(50)
				for x in xrange(-4, 5):
					temp.blit(temp, (x, 0))
					temp.blit(temp, (0, x))
				temp.set_alpha(255)
				time_domain.blit(temp, (0, 0))
			if event.key == ord("s"):
				brush_size = 15 - brush_size
			if event.key == ord("v"):
				vertical_mode = not vertical_mode

	def draw_in_color(c, w):
		pygame.draw.line(time_domain, c, (prev_x, prev_y), (mouse_x, mouse_y), w)

	if vertical_mode:
		prev_x = mouse_x
		prev_y = H/4
		mouse_y = (3*H)/4
	if ("m", 1) in holding:
		draw_in_color((255, 255, 255), brush_size)
	if ("m", 3) in holding:
		draw_in_color((0, 0, 0), 25)

	if ord("q") in holding:
		# Shrink
		starting_cut += 1
		if starting_cut > W/2-10:
			starting_cut = W/2-10
		scaled = pygame.transform.smoothscale(starting_image, (W-starting_cut*2, H-starting_cut*2))
		time_domain.fill((0, 0, 0))
		time_domain.blit(scaled, (starting_cut, starting_cut))

	time_array = pygame.surfarray.array2d(time_domain)
	# Actually do the Fourier transform!
	freq = abs(numpy.fft.fft2(time_array))
	# Handle normalization.
	if normalized_mode:
		freq *= 5000/numpy.amax(freq)
	else:
		freq /= 5e6
	if K_LSHIFT in holding:
		freq *= 10
	if K_RSHIFT in holding:
		freq *= 10
	numpy.clip(freq, 0, 256**2)
	freq = freq.astype(int)
	freq = numpy.roll(freq, W/2, axis=0)
	freq = numpy.roll(freq, H/2, axis=1)
	pygame.surfarray.blit_array(freq_domain, freq)

	screen.blit(time_domain, (0, 0))
	pygame.draw.rect(screen, (255, 0, 0), ((0, 0), (W, H)), 1)
	screen.blit(freq_domain, (W, 0))
	pygame.draw.rect(screen, (255, 0, 0), ((W, 0), (W, H)), 1)

	# Flip buffers.
	pygame.display.update()
	clock.tick(30)

