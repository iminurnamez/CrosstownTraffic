import sys
import os
import random
import time
import pygame
from pygame.locals import *
from pygame import Color
import nav_maps

pygame.init()

DISPLAYSURF = pygame.display.set_mode((896, 640))
SURF = DISPLAYSURF.convert_alpha()
pygame.display.set_caption("Crosstown Traffic")
FPS = 30
fpsClock = pygame.time.Clock()
SCREENWIDTH = 896
SCREENHEIGHT = 640

class Building(object):
	def __init__(self, leftx, topy):
		image_names = ["building.png", "building2.png", "park.png", "baseballfield.png"]
		self.image = pygame.image.load(os.path.join("Art", random.choice(image_names))).convert()
		self.rect = self.image.get_rect(topleft=(leftx, topy))
		
class Venue(object):
	def __init__(self, start_direct, center_point):
		self.image = pygame.image.load(os.path.join("Art", "lot" + start_direct + ".png")).convert()
		self.rect = self.image.get_rect(center=center_point)
		self.start_direct = start_direct
		
class Street(object):
	def __init__(self, leftx, topy, orientation):
		self.image = pygame.image.load(os.path.join("Art", orientation + "road.png")).convert()
		self.rect = self.image.get_rect(topleft =(leftx, topy))
		
class Intersection(object):
	def __init__(self, leftx, topy, orientation):
		self.orientation = orientation
		self.image = pygame.image.load(os.path.join("Art", orientation + "light.png")).convert()
		self.rect = self.image.get_rect(topleft =(leftx, topy))
		self.little_rect = self.rect.inflate(-62, -62)
		
	def react_to_click(self):
		if self.orientation in ["broken", "horiz"]:
			self.orientation = "vert"
		else:
			self.orientation = "horiz"
		self.image = pygame.image.load(os.path.join("Art", self.orientation + "light.png")).convert()
				
class Map(object):
	def __init__(self):
		self.map_array =["BVBVBVBVBVBVB",
						 "HIHIHIHIHIHIH",
						 "BVBVBVBVBVBVB",
						 "HIHIHIHIHIHIH",
						 "BVBVBVBVBVBVB",
						 "HIHIHIHIHIHIH",
						 "BVBVBVBVBVBVB",
						 "HIHIHIHIHIHIH",
						 "BVBVBVBVBVBVB"]
		
		self.entities = []
		self.intersections = []
		leftx = 32
		topy = 32
		for row in self.map_array:
			for char in row:
				if char == "I":
					entity = Intersection(leftx, topy, "vert")
					self.intersections.append(entity)
				else:
					if char == "B":
						entity = Building(leftx, topy)
						self.entities.append(entity)
					elif char == "V":
						entity = Street(leftx, topy, "vert")
						self.entities.append(entity)
					elif char == "H":
						entity = Street(leftx, topy, "horiz")
						self.entities.append(entity)
					
				leftx += 64
			topy += 64
			leftx = 32
		self.destinations = []
		for i in range(1, 7):
			dest = Venue("down", (128 * i, 16))
			dest2 = Venue("up", (128 * i, 624))
			self.destinations.append(dest)
			self.destinations.append(dest2)
		for i in range(1, 5):
			dest = Venue("right", (16, 128 * i))
			dest2 = Venue("left", (880, 128 * i))		
			self.destinations.append(dest)
			self.destinations.append(dest2)
			
class Car(object):
	def setup(self, origin, destination):
		self.stopped = False
		self.origin = origin
		self.destination = destination
		self.direction = origin.start_direct
		self.make_surface(self.origin.rect.centerx, self.origin.rect.bottom)
		self.make_bumper(2)
		self.line_active = False
		
	def make_surface(self, midx, bottomy):	
		self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
		self.rect = self.image.get_rect(midbottom=(midx, bottomy))
		self.surface = pygame.Surface((self.rect.width, self.rect.height))
		self.surface.set_colorkey((0, 0, 0))
		self.surface.blit(self.image, (0, 0))
		
	def make_bumper(self, bumper_size):
		bumper_map = {"up": (self.rect.centerx, self.rect.top),
					"down": (self.rect.centerx - bumper_size, self.rect.bottom - bumper_size),
					"left": (self.rect.left, self.rect.centery - bumper_size),
					"right": (self.rect.right - bumper_size, self.rect.centery)}
		return pygame.Rect(bumper_map[self.direction], (bumper_size, bumper_size))
	
	def check_for_goal(self, cars):
		if self.rect.colliderect(self.destination.rect):
			cars.remove(self)
	
	def find_goal(self, midx, midy):
		self.goal_orientation = "" 
		if self.destination.rect.centery > midy:
			self.goal_orientation = "down"
		elif self.destination.rect.centery < midy:
			self.goal_orientation = "up"
		if self.destination.rect.centerx > midx:
			self.goal_orientation += "right"
		elif self.destination.rect.centerx < midx:
			self.goal_orientation += "left"
		
	def navigate_intersection(self, intersection):
		heading = self.direction
		self.find_goal(intersection.rect.centerx, intersection.rect.centery)
		navigation_map = nav_maps.choose_nav_map(self)
				
		self.stopped = False 
		if intersection.orientation == "broken" and self.name == "hackervan":
			intersection.react_to_click()
			if navigation_map[self.direction][self.goal_orientation][intersection.orientation] == "stopped":
				intersection.react_to_click()
			self.move()
			intersection.orientation = "broken"
			intersection.image = pygame.image.load(os.path.join("Art", "brokenlight.png")).convert()
		elif intersection.orientation == "broken" and not self.name == "hackervan":
			self.stopped = True
		else:				
			if navigation_map[self.direction][self.goal_orientation][intersection.orientation] == "stopped":
				if self.name == "hackervan":
					intersection.react_to_click()
					self.direction = navigation_map[self.direction][self.goal_orientation][intersection.orientation]
				else:
					self.stopped = True
			else:
				self.direction = navigation_map[self.direction][self.goal_orientation][intersection.orientation]		
			if heading != self.direction:
				self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
				self.rect = self.image.get_rect(center=intersection.rect.center)
				self.surface.blit(self.image, (0, 0))
			if self.name == "hackervan":
				intersection.orientation = "broken"
				intersection.image = pygame.image.load(os.path.join("Art", "brokenlight.png")).convert()
				self.move()
				
					
	def move(self):
		if self.stopped:
			pass
		elif self.direction == "up":
			self.rect.centery -= self.speed
		elif self.direction == "down":
			self.rect.centery += self.speed
		elif self.direction == "left":
			self.rect.centerx -= self.speed
		elif self.direction == "right":
			self.rect.centerx += self.speed
		
class DeliveryTruck(Car):
	def __init__(self, origin, destination):
		self.color = "blue"
		self.name = "truck"
		self.speed = 1
		self.setup(origin, destination)
		
class FireTruck(Car):
	def __init__(self, origin, destination):
		self.color = "red"
		self.name = "firetruck"
		self.speed = 2
		self.setup(origin, destination)
		
class Cruiser(Car):
	def __init__(self, origin, destination):
		self.color = "white"
		self.name = "cruiser"
		self.speed = 3
		self.setup(origin, destination)
		
class SportsCar(Car):
	def __init__(self, origin, destination):
		self.color = "yellow"
		self.name = "sportscar"
		self.speed = 4
		self.setup(origin, destination)

class ProduceTruck(Car):
	def __init__(self, origin, destination):
		self.color = "green"
		self.name = "producetruck"
		self.speed = 1
		self.setup(origin, destination)

class HackerVan(Car):
	def __init__(self, origin, destination):
		self.color = "lightgray"
		self.name = "hackervan"
		self.speed = 2
		self.setup(origin, destination)
		
class RepairVan(Car):
	def __init__(self, origin, destination):
		self.color = "lightgray"
		self.name = "repairvan"
		self.speed = 2
		self.setup(origin, destination)
		
class Sedan(Car):
	def __init__(self, origin, destination):
		self.color = "pink"
		self.name = "sedan"
		self.speed = 2
		self.setup(origin, destination)
		
def level_loop(surface):		
	car_types = [SportsCar, ProduceTruck, DeliveryTruck, FireTruck, Cruiser, Sedan, HackerVan, RepairVan]
	#car_types = [HackerVan] # for testing, there are bugs in the van
	map = Map()
	round_count = 1
	cars = []
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			#elif event.type == KEYDOWN:				# for testing
			#	if event.key == K_SPACE:				# equal to clicking every light at once
			#		for intersection in map.intersections:
			#			intersection.react_to_click()
			elif event.type == MOUSEBUTTONDOWN:
				mousex, mousey = event.pos
				for intersection in map.intersections:
					if intersection.rect.collidepoint(mousex, mousey):
						intersection.react_to_click()
				for car in cars:
					if car.rect.collidepoint(mousex, mousey):
						car.line_active = not car.line_active
						
		if round_count % (FPS * 5) == 0:
			#for intersection in map.intersections:			# for testing
			#			intersection.react_to_click()		# lights cycle automatically
			car_origin = random.choice(map.destinations)
			car_dest = random.choice(map.destinations)
			while car_origin == car_dest:
				car_dest = random.choice(map.destinations)
			cars.append(random.choice(car_types)(car_origin, car_dest))
			
		for car in cars:
			car.check_for_goal(cars)
			car.bumper_rect = car.make_bumper(2)
			for intersection in map.intersections:
				if car.bumper_rect.colliderect(intersection.little_rect):
					car.navigate_intersection(intersection)
					break
			car.move()
		
		DISPLAYSURF.fill(Color("darkgreen"))
		for intersection in map.intersections:
			surface.blit(intersection.image, intersection.rect)
		for entity in map.entities:
			surface.blit(entity.image, entity.rect)
		for destination in map.destinations:
			surface.blit(destination.image, destination.rect)
		for car in cars:
			surface.blit(car.surface, car.rect)
			pygame.draw.line(surface, Color(car.color), car.bumper_rect.center, car.destination.rect.center, 2)
				
		pygame.display.update()
		fpsClock.tick(FPS)
		round_count += 1
level_loop(DISPLAYSURF)	