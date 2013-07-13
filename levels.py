class Level(object):
	def __init__(self, frequency, city_map_array):
		self.frequency = frequency # num of seconds between new traffic
		self.city_map_array = city_map_array
		
		
Level1 = Level(8, ["KVMVRVSVXVRVC",
				   "HIHIHIHIHIHIH",
				   "RVKVRVGVYVRVK",
				   "HIHIHIHIHIHIH",
				   "KVCVFVRVKVRVX",
				   "HIHIHIHIHIHIH",
				   "MVGVXVPVRVKVK",
				   "HIHIHIHIHIHIH",
				   "KVYVKVRVKVMVG"])