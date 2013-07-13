import os
import random
import itertools
import pygame
from pygame import Color

class Building(object):	
	def make_image(self, leftx, topy):
		self.image = pygame.image.load(os.path.join("Art", self.image_name)).convert()
		self.rect = self.image.get_rect(topleft=(leftx, topy))
		self.surface = pygame.Surface((self.rect.width, self.rect.height))
		self.surface.set_colorkey((0, 0, 0))
		self.surface.blit(self.image, (0, 0))
	
	def get_start_direct(self):
		if self.rect.centerx >= 736:
			self.xoffset = -64
		else:
			self.xoffset = 64
		if self.rect.centery < 128:
			self.start_direct = "down"
		else:
			self.start_direct = "up"
class Park(Building):
	image_names = ["plaza.png", "park.png", "baseballfield.png", "soccerfield.png"]
	def __init__(self, leftx, topy):
		self.image_name = random.choice(self.image_names)
		self.make_image(leftx, topy)
		self.get_start_direct()

class Firehouse(Building):
	def __init__(self, leftx, topy):
		self.image_name = "firehouse.png"
		self.make_image(leftx, topy)
		self.get_start_direct()
		
class PoliceStation(Building):
	def __init__(self, leftx, topy):
		self.image_name = "police_station.png"
		self.make_image(leftx, topy)
		self.get_start_direct()

class School(Building):
	def __init__(self, leftx, topy):
		self.image_name = "school.png"
		self.make_image(leftx, topy)
		self.get_start_direct()
		
class Highrise(Building):
	image_names = [ "blue_highrise.png", "brick_highrise.png", "yellow_highrise.png"]
	def __init__(self, leftx, topy):
		self.image_name = random.choice(self.image_names)
		self.make_image(leftx, topy)
		self.get_start_direct()
		self.on_fire = False
		self.has_kids = False
		
class BoxStore(Building):
	def __init__(self, leftx, topy):
		self.image_name = "box_store.png"
		self.make_image(leftx, topy)
		self.get_start_direct()

class GroceryStore(Building):
	def __init__(self, leftx, topy):
		self.image_name = "grocery_store.png"
		self.make_image(leftx, topy)
		self.get_start_direct()
		
		
class GasStation(Building):
	def __init__(self, leftx, topy):
		self.image_name = "gasstation.png"
		self.make_image(leftx, topy)
		self.get_start_direct()
		
class Factory(Building):
	def __init__(self, leftx, topy):
		self.image_name = "factory.png"
		self.make_image(leftx, topy)
		self.get_start_direct()
	
class StripMall(Building):
	def __init__(self, leftx, topy):
		self.image_name = "stripmall.png"
		self.make_image(leftx, topy)
		self.get_start_direct()
	
class Venue(Building):
	def __init__(self, start_direct, center_point):
		self.image = pygame.image.load(os.path.join("Art", "lot" + start_direct + ".png")).convert()
		self.rect = self.image.get_rect(center=center_point)
		self.start_direct = start_direct
		self.xoffset = 0
		
		
class Street(object):
	def __init__(self, leftx, topy, orientation):
		self.image = pygame.image.load(os.path.join("Art", orientation + "road.png")).convert()
		self.rect = self.image.get_rect(topleft =(leftx, topy))
		
		
class Intersection(object):
	def __init__(self, leftx, topy, orientation):
		self.orientation = orientation
		self.bground_image = pygame.image.load(os.path.join("Art", "blank_intersection.png")).convert()
		self.image = pygame.image.load(os.path.join("Art", orientation + "light.png")).convert()
		self.rect = self.image.get_rect(topleft =(leftx, topy))
		self.surface = pygame.Surface((self.rect.width, self.rect.height))
		self.surface.set_colorkey((0, 0, 0))
		self.surface.blit(self.image, (0, 0))
		self.little_rect = self.rect.inflate(-62, -62)
		self.spark_count = 0
	
	def update_image(self):
		self.image = self.image = pygame.image.load(os.path.join("Art", self.orientation + "light.png")).convert()
		self.surface.blit(self.image, (0, 0))
	
	def react_to_click(self):
		if self.orientation in ["broken", "horiz"]:
			self.orientation = "vert"
		else:
			self.orientation = "horiz"
		self.update_image()
	
class Effect(object):
	pass

class Kids(Effect):
	def __init__(self, building):
		self.images = itertools.cycle(["kids1.png", "kids2.png", "kids3.png", "kids4.png"])
		self.image = pygame.image.load(os.path.join("Art", next(self.images))).convert()
		self.location = building
		self.rect  = self.image.get_rect(bottomleft=building.rect.bottomleft)
		self.surface = pygame.Surface((self.rect.width, self.rect.height))
		self.surface.set_colorkey((0, 0, 0))
		self.surface.blit(self.image, (0, 0))
		
		
	def update(self, round_count):
		if round_count % 5 == 0:
			self.image = pygame.image.load(os.path.join("Art", next(self.images))).convert()
		self.surface.blit(self.image, (0, 0))
		
class Spark(Effect):
	def __init__(self, center_point, city_map):
		self.image = pygame.image.load(os.path.join("Art", "spark.png")).convert()
		self.rect  = self.image.get_rect(center=(center_point))
		self.surface = pygame.Surface((self.rect.width, self.rect.height))
		self.surface.set_colorkey((0, 0, 0))
		self.surface.blit(self.image, (0, 0))
		self.timer = 60
		city_map.sparks.append(self)
	
	def update(self, city_map):
		self.timer -= 1
		if self.timer < 1:
			city_map.sparks.remove(self)
		
class Flames(Effect):
	def __init__(self, building):
		self.images = itertools.cycle(["flames1.png", "flames2.png", "flames3.png", "flames4.png"])
		self.image = pygame.image.load(os.path.join("Art", next(self.images))).convert()
		self.location = building
		self.rect = building.rect
		self.surface = pygame.Surface((self.rect.width, self.rect.height))
		self.surface.set_colorkey((0, 0, 0))
		self.surface.blit(self.image, (0, 0))
		
		
	def update(self, round_count):
		if round_count % 5 == 0:
			self.image = pygame.image.load(os.path.join("Art", next(self.images))).convert()
		self.surface.blit(self.image, (0, 0))