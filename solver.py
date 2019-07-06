import networkx as nx
import queue as Q
import random

def solve(client):
	client.end()
	client.start()

	#variables
	all_students = list(range(1, client.students + 1))
	non_home = list(range(1, client.home)) + list(range(client.home + 1, client.v + 1))
	home = client.home
	remoted_from = []

	#find shortest paths
	all_shortest_paths = nx.shortest_path(client.G, target=home, weight='weight')
	all_shortest_path_length = nx.shortest_path_length(client.G, target=home, weight='weight')

	#scout every vertex, every student
	student_correct = [0]*client.students #for updating priorities
	student_reports = {}


	all_reports = Q.PriorityQueue()
	for vertex in non_home:
		reports = client.scout(vertex, all_students)

		student_reports[vertex] = reports #for updating priorities

		all_reports.put((-sum(reports.values()), all_shortest_path_length[vertex], vertex))

	#remote on vertices with yes reports in order of # yes
	print('remoting on yes reports')
	i = 0

	num_bots = 0 #for updating priorities

	while (i < len(non_home)) and (sum(client.bot_count) < client.bots):
		num_yes, dist, most_reported = all_reports.get()
		if -num_yes/client.students < .45:
			break
		sp = all_shortest_paths[most_reported]
		client.remote(most_reported, sp[1])
		remoted_from.append(most_reported)

		'''
		#increase/decrease priority each time depending on student correctness
		report = student_reports[most_reported]
		if num_bots < sum(client.bot_count):
			for index in range(len(report)):
				if report[index+1]:
					student_correct[index] -= .1
				else:
					student_correct[index] += .1
		else:
			for index in range(len(report)):
				if not report[index+1]:
					student_correct[index] -= .1
				else:
					student_correct[index] += .1

		size = all_reports.qsize()
		for _ in range(size):
			num_yes, dist, most_reported = all_reports.get()
			report = student_reports[most_reported]
			
			for index in range(len(student_correct)):
				if report[index+1]:
					num_yes += student_correct[index]
				else:
					num_yes -= student_correct[index]
			all_reports.put((num_yes, dist, most_reported))


		num_bots = sum(client.bot_count) #testing'''

		i+=1


	'''
	#sort vertices by furthest away
	furthest = Q.PriorityQueue()
	for k in all_shortest_paths.keys():
		furthest.put((-all_shortest_path_length[k], k))'''

	
	#sort vertices by closest 
	closest = Q.PriorityQueue()
	for k in all_shortest_paths.keys():
		closest.put((all_shortest_path_length[k], k))


	'''
	#remote on each known bot location once to find any unkowns there
	#print('checking known locations for extra bots')
	locations = list(set(client.bot_locations))
	if sum(client.bot_count) < client.bots:
		for vertex in locations:
	    	if vertex is not home:
	    		client.remote(vertex, all_shortest_paths[vertex][1])
	    		remoted_from.append(vertex)'''


	
	#find rest of bots, starting from closest vertices away from home
	print('finding rest of the bots')
	while (sum(client.bot_count) < client.bots) and (len(remoted_from) < len(non_home)):
		#_, vertex = furthest.get()
		_, vertex = closest.get()
		if (vertex not in remoted_from) and (vertex != home):
			client.remote(vertex, all_shortest_paths[vertex][1])
			remoted_from.append(vertex)

	#return all bots home along shortest paths
	print('returning any remaining bots home')
	while list(set(client.bot_locations)) != [home]:
		locations = list(set(client.bot_locations))
		furthest_bots = locations[0]
		max_dist = 0
		for i in locations:
			if all_shortest_path_length[i] > max_dist:
				max_dist = all_shortest_path_length[i]
				furthest_bots = i
		
		client.remote(furthest_bots, all_shortest_paths[furthest_bots][1])
		remoted_from.append(furthest_bots)


	client.end()
