import os
import random
import pygame
from pygame import Color
import nav_maps
import buildings

class Car(object):
	def setup(self, origin, destination):
		self.stopped = False
		self.origin = origin
		self.destination = destination
		self.direction = origin.start_direct
		self.make_surface(self.origin.rect.left + self.origin.xoffset, self.origin.rect.bottom)
		self.bumper_rect = self.make_bumper(2)
		self.check_rect = self.make_check_rect()
		self.line_active = False
		self.arrived = False
		self.distance = abs(origin.rect.centerx - destination.rect.centerx) +\
						abs(origin.rect.centery - destination.rect.centery)
		self.optimum = int(self.distance / self.speed) * 2
		self.loop_count = 0
		print self.optimum
		
	def make_surface(self, leftx, bottomy):	
		self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
		self.rect = self.image.get_rect(bottomleft=(leftx, bottomy))
		self.surface = pygame.Surface((self.rect.width, self.rect.height))
		self.surface.set_colorkey((0, 0, 0))
		self.surface.blit(self.image, (0, 0))

	def make_bumper(self, bumper_size):
		bumper_map = {"up": (self.rect.centerx, self.rect.top),
					"down": (self.rect.centerx - bumper_size, self.rect.bottom - bumper_size),
					"left": (self.rect.left, self.rect.centery - bumper_size),
					"right": (self.rect.right - bumper_size, self.rect.centery)}
		return pygame.Rect(bumper_map[self.direction], (bumper_size, bumper_size))
	
	def make_check_rect(self, size=5):
		check_rect_map = {"up": [(self.rect.left - 10, self.rect.centery - size /2), (self.rect.width + (size * 2) + 10, size)],
					"down": [(self.rect.left - 10, self.rect.centery - size/2), (self.rect.width + (size * 2) + 10, size)],
 					"left": [(self.rect.centerx - size/2, self.rect.top - 15), (size, self.rect.height + (size * 2) + 10)],
					"right": [(self.rect.centerx - size/2, self.rect.top - 15), (size, self.rect.height + (size * 2) + 10)]} 
		return pygame.Rect(check_rect_map[self.direction][0], check_rect_map[self.direction][1])
		
	def arrive(self, city_map, player):
		self.arrived = True	
		self.destination = self.origin
		# give score/money to player
		 
	def check_for_goal(self, cars, city_map, player):
		if self.make_check_rect().colliderect(self.destination.rect):  
			if self.destination == self.origin and not self.arrived:
				pass
			elif self.destination == self.origin and self.arrived:
				city_map.score += int(self.optimum * self.loop_count/self.optimum * self.point_value)
				print "score: " + str(city_map.score)
				cars.remove(self)
			else:
				self.arrive(city_map, player)
				self.destination = self.origin
		if self.name in ["hackervan", "truck", "producetruck"]:
			for dest in city_map.destinations:
				if self.make_check_rect().colliderect(dest.rect) and dest not in [self.destination, self.origin]: 
					reverse_directions = {"up": "down",
										"down": "up",
										"left": "right",
										"right": "left"}
					self.direction = reverse_directions[self.direction]
					self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
					self.surface.blit(self.image, (0, 0))
		else:
			for dest in city_map.destinations:
				if self.make_check_rect().colliderect(dest.rect) and dest != self.destination:
					reverse_directions = {"up": "down",
										"down": "up",
										"left": "right",
										"right": "left"}
					self.direction = reverse_directions[self.direction]
					self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
					self.surface.blit(self.image, (0, 0))
		
			
	
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
		
	def navigate_intersection(self, intersection, city_map):
		if intersection.orientation == "broken":
			self.stopped = True
		else:
			heading = self.direction
			self.find_goal(intersection.rect.centerx, intersection.rect.centery)
			navigation_map = nav_maps.choose_nav_map(self)
					
			self.stopped = False 
			
			if navigation_map[self.direction][self.goal_orientation][intersection.orientation] == "stopped":
				self.stopped = True
			else:
				self.direction = navigation_map[self.direction][self.goal_orientation][intersection.orientation]		
			if heading != self.direction:
				self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
				self.rect = self.image.get_rect(center=intersection.rect.center)
				self.surface.blit(self.image, (0, 0))
			
					
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
		self.point_value = 100
		self.color = "blue"
		self.name = "truck"
		self.speed = 1
		self.setup(origin, destination)
		self.arrived = False
		self.truck_sound = pygame.mixer.Sound(os.path.join("Sounds", "truck.wav"))
		truck_sound_channel = pygame.mixer.find_channel()
		truck_sound_channel.queue(self.truck_sound)
		self.truck_sound.play()
		
class FireTruck(Car):
	def __init__(self, origin, destination):
		self.point_value = 500
		self.color = "red"
		self.name = "firetruck"
		self.speed = 2
		self.setup(origin, destination)
		self.arrived = False
		self.watering = False
		self.counter = 0
		self.firetruck_sound = pygame.mixer.Sound(os.path.join("Sounds", "firetruck_sound.wav"))
		firetruck_sound_channel = pygame.mixer.find_channel()
		firetruck_sound_channel.queue(self.firetruck_sound)
		self.firetruck_sound.play()
		
	def check_for_goal(self, cars, city_map, player):
		if self.make_check_rect().colliderect(self.destination.rect):
			if self.destination in city_map.flames and not self.watering:
				self.watering = True
				self.stopped = True		
				self.counter = 90
			elif self.watering:
				pass
			else:
				self.arrive(city_map, player)
				player.firetrucks_available += 1
				cars.remove(self)
	
	def water(self, surface, city_map):
		if self.counter > 1:
			pygame.draw.line(surface, Color("lightblue"), self.bumper_rect.center, self.destination.rect.center, 5)
			self.counter -= 1
		else:
			for fire in city_map.flames:
				if fire.rect == self.destination.rect:
					fire.location.on_fire = False
					city_map.flames.remove(fire)
			self.destination = self.origin
			self.destination = self.origin
			self.find_goal(self.rect.centerx, self.rect.centery)
			self.stopped = False
			self.watering = False
			
class Cruiser(Car):
	def __init__(self, origin, destination):
		self.point_value = 300
		self.color = "white"
		self.name = "cruiser"
		self.speed = 3
		self.setup(origin, destination)
		self.arrived = False
		self.police_siren = pygame.mixer.Sound(os.path.join("Sounds", "police_siren.wav"))
		police_siren_channel = pygame.mixer.find_channel()
		police_siren_channel.queue(self.police_siren)
		self.police_siren.play()
	
	def check_for_goal(self, cars, city_map, player):
		if self.make_check_rect().colliderect(self.destination.rect):
			if self.destination in cars:
				cars.remove(self.destination)
				print "Nabbed a saboteur"
				self.destination = self.origin
				self.find_goal(self.rect.centerx, self.rect.centery)
			else:
				self.arrive(city_map, player)
				player.cruisers_available += 1
				cars.remove(self)
		for dest in city_map.destinations:
			for dest in city_map.destinations:
				if self.make_check_rect().colliderect(dest.rect) and dest != self.destination:
					reverse_directions = {"up": "down",
										"down": "up",
										"left": "right",
										"right": "left"}
					self.direction = reverse_directions[self.direction]
					self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
					self.surface.blit(self.image, (0, 0))
					
	def navigate_intersection(self, intersection, city_map):
		heading = self.direction
		self.find_goal(intersection.rect.centerx, intersection.rect.centery)
		navigation_map = nav_maps.choose_nav_map(self)
		light_state = intersection.orientation
		found_broken = False
		if intersection.orientation == "broken":
			found_broken = True
			intersection.react_to_click()
		if navigation_map[self.direction][self.goal_orientation][intersection.orientation] == "stopped":
			intersection.react_to_click()
		self.direction = navigation_map[self.direction][self.goal_orientation][intersection.orientation]
		if heading != self.direction:
			self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
			self.rect = self.image.get_rect(center=intersection.rect.center)
			self.surface.blit(self.image, (0, 0))
		if found_broken:
			intersection.orientation = "broken"
			intersection.update_image()
			
class Ambulance(Car):
	def __init__(self, origin, destination):
		self.point_value = 200
		self.color = "yellow"
		self.name = "ambulance"
		self.speed = 3
		self.setup(origin, destination)
		self.arrived = False
		self.ambulance_siren = pygame.mixer.Sound(os.path.join("Sounds", "ambulance_siren.wav"))
		ambulance_siren_channel = pygame.mixer.find_channel()
		ambulance_siren_channel.queue(self.ambulance_siren)
		self.ambulance_siren.play()
		
	def navigate_intersection(self, intersection, city_map):
		heading = self.direction
		self.find_goal(intersection.rect.centerx, intersection.rect.centery)
		navigation_map = nav_maps.choose_nav_map(self)
		light_state = intersection.orientation
		found_broken = False
		if intersection.orientation == "broken":
			found_broken = True
			intersection.react_to_click()
		if navigation_map[self.direction][self.goal_orientation][intersection.orientation] == "stopped":
			intersection.react_to_click()
		self.direction = navigation_map[self.direction][self.goal_orientation][intersection.orientation]
		if heading != self.direction:
			self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
			self.rect = self.image.get_rect(center=intersection.rect.center)
			self.surface.blit(self.image, (0, 0))
		intersection.orientation = light_state
		if found_broken:
			intersection.orientation = "broken"	
		
class SchoolBus(Car):
	def __init__(self, origin, destination):
		self.point_value = 200
		self.color = "yellow"
		self.name = "schoolbus"
		self.speed = 2
		self.setup(origin, destination)
		self.arrived = False
		self.kids_sound = pygame.mixer.Sound(os.path.join("Sounds", "kids.wav"))
		kids_sound_channel = pygame.mixer.find_channel()
		kids_sound_channel.queue(self.kids_sound)
		self.kids_sound.play()
	
	def arrive(self, city_map, player):
		self.arrived = True	
		self.destination = self.origin
		
	def check_for_goal(self, cars, city_map, player):
		if self.make_check_rect().colliderect(self.destination.rect):
			if self.destination in city_map.kids:
				self.destination.location.has_kids = False
				city_map.kids.remove(self.destination)
				self.destination = self.origin
				self.find_goal(self.rect.centerx, self.rect.centery)
			else:
				self.arrive(city_map, player)
				player.buses_available += 1
				cars.remove(self)
				
				
class SportsCar(Car):
	def __init__(self, origin, destination):
		self.point_value = 200
		self.color = "yellow"
		self.name = "sportscar"
		self.speed = 4
		self.setup(origin, destination)
		self.arrived = False
		self.sportscar_sound = pygame.mixer.Sound(os.path.join("Sounds", "sportscar_sound.wav"))
		sportscar_sound_channel = pygame.mixer.find_channel()
		sportscar_sound_channel.queue(self.sportscar_sound)
		self.sportscar_sound.play()
		
class ProduceTruck(Car):
	def __init__(self, origin, destination):
		self.point_value = 75
		self.color = "green"
		self.name = "producetruck"
		self.speed = 1
		self.setup(origin, destination)
		self.arrived = False
		self.produce_truck_sound = pygame.mixer.Sound(os.path.join("Sounds", "produce_truck.wav"))
		produce_truck_sound_channel = pygame.mixer.find_channel()
		produce_truck_sound_channel.queue(self.produce_truck_sound)
		self.produce_truck_sound.play()


class HackerVan(Car):
	def __init__(self, origin, destination):
		self.point_value = 0
		self.color = "lightgray"
		self.name = "hackervan"
		self.speed = 2
		self.setup(origin, destination)
		self.arrived = False
		self.sedan_sound = pygame.mixer.Sound(os.path.join("Sounds", "sedan_sound1.wav"))
		sedan_sound_channel = pygame.mixer.find_channel()
		sedan_sound_channel.queue(self.sedan_sound)
		self.sedan_sound.play()
	
	def check_for_goal(self, cars, city_map, player):
		if self.make_check_rect().colliderect(self.destination.rect):  
			if self.destination == self.origin and not self.arrived:
				pass
			else:
				self.arrive(city_map, player)
				
		for dest in city_map.destinations:
			if self.make_check_rect().colliderect(dest.rect) and dest != self.origin:
				reverse_directions = {"up": "down",
									"down": "up",
									"left": "right",
									"right": "left"}
				self.direction = reverse_directions[self.direction]
				self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
				self.surface.blit(self.image, (0, 0))
	
	def navigate_intersection(self, intersection, city_map):
		heading = self.direction
		self.find_goal(intersection.rect.centerx, intersection.rect.centery)
		navigation_map = nav_maps.choose_nav_map(self)
		
		if intersection.orientation == "broken":
			intersection.react_to_click()
		if navigation_map[self.direction][self.goal_orientation][intersection.orientation] == "stopped":
			intersection.react_to_click()
		self.direction = navigation_map[self.direction][self.goal_orientation][intersection.orientation]
		
		
		intersection.orientation = "broken"
		intersection.update_image()
		spark = buildings.Spark(intersection.rect.center, city_map)
		if heading != self.direction:
			self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
			self.rect = self.image.get_rect(center=intersection.rect.center)
			self.surface.blit(self.image, (0, 0))
	
	def arrive(self, city_map, player):
		self.arrived = True	
		self.destination = random.choice(city_map.businesses)
		
	
class RepairVan(Car):
	def __init__(self, origin, destination):
		self.point_value = 75
		self.color = "lightgray"
		self.name = "repairvan"
		self.speed = 2
		self.setup(origin, destination)
		self.arrived = False
		self.sedan_sound = pygame.mixer.Sound(os.path.join("Sounds", "sedan_sound1.wav"))
		sedan_sound_channel = pygame.mixer.find_channel()
		sedan_sound_channel.queue(self.sedan_sound)
		self.sedan_sound.play()
		
	def navigate_intersection(self, intersection, city_map):
		heading = self.direction
		self.find_goal(intersection.rect.centerx, intersection.rect.centery)
		navigation_map = nav_maps.choose_nav_map(self)
		
		if intersection.orientation == "broken":
			intersection.react_to_click()
		if navigation_map[self.direction][self.goal_orientation][intersection.orientation] == "stopped":
			intersection.react_to_click()
		self.direction = navigation_map[self.direction][self.goal_orientation][intersection.orientation]
		if heading != self.direction:
			self.image = pygame.image.load(os.path.join("Art", self.name + self.direction + ".png")).convert()
			self.rect = self.image.get_rect(center=intersection.rect.center)
			self.surface.blit(self.image, (0, 0))

class Bikers(Car):
	def __init__(self, origin, destination):
		self.point_value = 200
		self.color = "gray10"
		self.name = "bikers"
		self.speed = 2
		self.setup(origin, destination)
		self.arrived = False
		self.bikers_sound = pygame.mixer.Sound(os.path.join("Sounds", "bikers.wav"))
		bikers_sound_channel = pygame.mixer.find_channel()
		bikers_sound_channel.queue(self.bikers_sound)
		self.bikers_sound.play()
			
			
class Sedan(Car):
	def __init__(self, origin, destination):
		self.point_value = 100
		self.color = "pink"
		self.name = "sedan"
		self.speed = 2
		self.setup(origin, destination)
		self.arrived = False
		self.sedan_sound = pygame.mixer.Sound(os.path.join("Sounds", "sedan_sound1.wav"))
		sedan_sound_channel = pygame.mixer.find_channel()
		sedan_sound_channel.queue(self.sedan_sound)
		self.sedan_sound.play()

class Clunker(Car):
	def __init__(self, origin, destination):
		self.point_value = 50
		self.color = "brown"
		self.name = "clunker"
		self.speed = 1
		self.setup(origin, destination)
		self.arrived = False
		self.clunker_sound = pygame.mixer.Sound(os.path.join("Sounds", "clunker_sound.wav"))
		clunker_sound_channel = pygame.mixer.find_channel()
		clunker_sound_channel.queue(self.clunker_sound)
		self.clunker_sound.play()