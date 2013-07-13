import sys
import os
import random
import time
import itertools
import pygame
from pygame.locals import *
from pygame import Color
import levels
import nav_maps
import vehicles
import buildings

pygame.init()

DISPLAYSURF = pygame.display.set_mode((960, 704))
SURF = DISPLAYSURF.convert_alpha()
pygame.display.set_caption("Crosstown Traffic")
FPS = 30
fpsClock = pygame.time.Clock()
SCREENWIDTH = 960	
SCREENHEIGHT = 704		

class Player(object):
	def __init__(self):
		self.cruisers_available = 2
		self.firetrucks_available = 2
		self.buses_available = 2

class Map(object):
	def __init__(self, level):
		self.city_map_array = level.city_map_array
		self.score = 0							
		self.streets = []
		self.intersections = []
		self.parks = []
		self.businesses = []
		self.highrises = []
		self.sparks = []
		self.flames = []
		self.kids = []
		leftx = 32
		topy = 32
		for row in self.city_map_array:
			for char in row:
				if char == "I":
					entity = buildings.Intersection(leftx, topy, "vert")
					self.intersections.append(entity)
				elif char == "F":
					entity = buildings.Firehouse(leftx, topy)
					self.firehouse = entity
				elif char == "P":
					entity = buildings.PoliceStation(leftx, topy)
					self.police_station = entity
				elif char == "D":
					entity = buildings.MaintenanceShed(leftx, topy)
					self.maintenance_shed = entity
				elif char == "K":
					entity = buildings.Park(leftx, topy)
					self.parks.append(entity)
				elif char == "G":
					entity = buildings.GasStation(leftx, topy)
					self.businesses.append(entity)
				elif char == "S":
					entity = buildings.School(leftx, topy)
					self.school = entity
				elif char == "R":
					entity = buildings.Highrise(leftx, topy)
					self.highrises.append(entity)
				elif char == "Y":
					entity = buildings.Factory(leftx, topy)
					self.businesses.append(entity)
				elif char == "X":
					entity = buildings.BoxStore(leftx, topy)
					self.businesses.append(entity)
				elif char == "C":
					entity = buildings.GroceryStore(leftx, topy)
					self.businesses.append(entity)
				elif char == "M":
					entity = buildings.StripMall(leftx, topy)
					self.businesses.append(entity)
				elif char == "V":
					entity = buildings.Street(leftx, topy, "vert")
					self.streets.append(entity)
				elif char == "H":
					entity = buildings.Street(leftx, topy, "horiz")
					self.streets.append(entity)
				if entity.rect.height > 64:
					entity.rect.top -= entity.rect.height - 64
				leftx += 64
			topy += 64
			leftx = 32
		self.destinations = []
		for i in range(1, 7):
			dest = buildings.Venue("down", (128 * i, 16))
			dest2 = buildings.Venue("up", (128 * i, 624))
			self.destinations.append(dest)
			self.destinations.append(dest2)
		for i in range(1, 5):
			dest = buildings.Venue("right", (16, 128 * i))
			dest2 = buildings.Venue("left", (880, 128 * i))		
			self.destinations.append(dest)
			self.destinations.append(dest2)
			
	
def add_car(city_map, cars, car_types=[vehicles.SportsCar, vehicles.ProduceTruck, vehicles.Clunker,
			vehicles.Bikers, vehicles.DeliveryTruck, vehicles.Sedan, vehicles.HackerVan, vehicles.RepairVan]):
	current_type = random.choice(car_types)
	if current_type == vehicles.SportsCar:
		car = vehicles.SportsCar(random.choice(city_map.highrises), random.choice(city_map.businesses))
		cars.append(car)
	elif current_type == vehicles.ProduceTruck:
		car = vehicles.ProduceTruck(random.choice(city_map.destinations), random.choice(city_map.businesses))
		cars.append(car)
	elif current_type == vehicles.DeliveryTruck:
		car = vehicles.DeliveryTruck(random.choice(city_map.destinations), random.choice(city_map.businesses))
		cars.append(car)
	elif current_type == vehicles.Sedan:
		car = vehicles.Sedan(random.choice(city_map.highrises), random.choice(city_map.businesses))
		cars.append(car)
	elif current_type == vehicles.HackerVan:
		car = vehicles.HackerVan(random.choice(city_map.destinations), random.choice(city_map.businesses))
		cars.append(car)
	elif current_type == vehicles.Clunker:
		car = vehicles.Clunker(random.choice(city_map.highrises), random.choice(city_map.businesses))
		cars.append(car)
	elif current_type == vehicles.Bikers:
		car = vehicles.Bikers(random.choice(city_map.highrises), random.choice(city_map.businesses))
		cars.append(car)



	
def level_loop(surface, level):		
	pygame.mixer.set_num_channels(16)
	pygame.mixer.music.load(os.path.join("Sounds", "background.wav"))
	pygame.mixer.music.play(-1)
	player = Player()
	current_building = "police_station"
	city_map = Map(level)
	round_count = 1
	cars = []
	add_car(city_map, cars)
	score = 0
	while True:
		#start = time.time()
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN:				# for testing
				if event.key == K_SPACE:				# equal to clicking every light at once
					for intersection in city_map.intersections:
						intersection.react_to_click()
			elif event.type == MOUSEBUTTONDOWN:
				mousex, mousey = event.pos
				for intersection in city_map.intersections:
					if intersection.rect.collidepoint(mousex, mousey):
						intersection.react_to_click()
				if city_map.firehouse.rect.collidepoint(mousex, mousey):
					current_building = "firehouse"
				if city_map.police_station.rect.collidepoint(mousex, mousey):
					current_building = "police station"
				if city_map.school.rect.collidepoint(mousex, mousey):
					current_building = "school"
				for car in cars:
					if current_building == "police station"  and player.cruisers_available > 0:
						if car.name == "hackervan" and car.rect.collidepoint(mousex, mousey):
							cop = vehicles.Cruiser(city_map.police_station, car)
							cars.append(cop)
							player.cruisers_available -= 1
				if current_building == "firehouse" and player.firetrucks_available > 0:
					for fire in city_map.flames:
						if fire.rect.collidepoint(mousex, mousey):
							responder = vehicles.FireTruck(city_map.firehouse, fire)
							cars.append(responder)
							player.firetrucks_available -= 1
				if current_building == "school" and player.buses_available > 0:
					for kid in city_map.kids:
						if kid.rect.collidepoint(mousex, mousey):
							bus = vehicles.SchoolBus(city_map.school, kid)
							cars.append(bus)
							player.buses_available -= 1

		if round_count % (FPS * level.frequency) == 0:
			add_car(city_map, cars)
		if round_count % (FPS * 6) == 0: 				# for testing	
			for intersection in city_map.intersections: #
				intersection.react_to_click()		# lights cycle automatically
		for car in cars:
			car.check_for_goal(cars, city_map, player)
			car.bumper_rect = car.make_bumper(2)
			for intersection in city_map.intersections:
				if car.bumper_rect.colliderect(intersection.little_rect):
					car.navigate_intersection(intersection, city_map)
					break
			car.move()
			
		DISPLAYSURF.fill(Color("darkseagreen"))
		for street in city_map.streets:
			surface.blit(street.image, street.rect)
		for intersection in city_map.intersections:
			surface.blit(intersection.bground_image, intersection.rect)
		for destination in city_map.destinations:
			surface.blit(destination.image, destination.rect)
		for car in cars:
			surface.blit(car.surface, car.rect)
			pygame.draw.line(surface, Color(car.color), car.bumper_rect.center, car.destination.rect.center, 1)
			#pygame.draw.rect(surface, Color(car.color), car.make_check_rect()) # for testing
			#pygame.draw.rect(surface, Color("white"), car.bumper_rect) # for testing
			#if car.name == "cruiser":
			#	siren_surf = pygame.Surface((256, 256))
			#	siren_surf.fill(Color("black"))
			#	siren_surf.set_colorkey((0, 0, 0))
			#	pygame.draw.circle(siren_surf, Color("blue"), (128, 128), 128)
			#	siren_surf.set_alpha(128)
			#	siren_rect = pygame.Rect(car.rect.centerx - 128, car.rect.centery - 128, siren_surf.get_width(), siren_surf.get_height())
			#	surface.blit(siren_surf, siren_rect)
			if car.name == "firetruck" and car.watering:
				car.water(surface, city_map)
			car.loop_count += 1	
		for spark in city_map.sparks:
			spark.update(city_map)
			if round_count % 3 == 0 or round_count % 2 == 0:
				surface.blit(spark.surface, spark.rect)
		
		for highrise in city_map.highrises:	
			if random.randint(1, 5000) < 3 and not highrise.on_fire:
				highrise.on_fire = True
				fire = buildings.Flames(highrise)
				city_map.flames.append(fire)
			surface.blit(highrise.surface, highrise.rect)
			if random.randint(1, 5000) < 3 and not highrise.has_kids:
				highrise.has_kids = True
				schoolkids = buildings.Kids(highrise)
				city_map.kids.append(schoolkids)
		for park in city_map.parks:
			surface.blit(park.surface, park.rect)
		for business in city_map.businesses:
			surface.blit(business.surface, business.rect)
		surface.blit(city_map.firehouse.surface, city_map.firehouse.rect)
		surface.blit(city_map.police_station.surface, city_map.police_station.rect)
		surface.blit(city_map.school.surface, city_map.school.rect)
		for intersection in city_map.intersections:
			surface.blit(intersection.surface, intersection.rect)
		for fire in city_map.flames:
			fire.update(round_count)
			surface.blit(fire.surface, fire.rect)
		for kid in city_map.kids:
			kid.update(round_count)
			surface.blit(kid.surface, kid.rect)
		pygame.display.update()
		fpsClock.tick(FPS)
		round_count += 1
		#print time.time() - start
		
level_loop(DISPLAYSURF, levels.Level1)	