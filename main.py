from copy import deepcopy
import functools
import time
import heapq
import itertools
from turtle import position

class PriorityQueue:
    pq = []
    entry_finder = {}
    REMOVED = '<removed-task>'
    counter = itertools.count()

    def add_task(self, task, priority=0):
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = [priority, count, task]
        self.entry_finder[task] = entry
        heapq.heappush(self.pq, entry)

    def remove_task(self, task):
        entry = self.entry_finder.pop(task)
        entry[-1] = self.REMOVED

    def pop_task(self):
        while self.pq:
            priority, count, task = heapq.heappop(self.pq)
            if task is not self.REMOVED:
                del self.entry_finder[task]
                return task
        return None

class Map:
    map: list[list] = None
    parse = {'+': 0, '-': 1, 0: '+', 1: ' ', '*': '*'}

    def __init__(self) -> None:
        self.map = self.read_map()

    def read_map(self) -> list:
        return [[self.parse[x] for x in l.strip()] for l in open("map.txt").readlines()]

    def __repr__(self) -> str:
        s = ''
        for y in self.map:
            for x in y:
                s += self.parse[x]
            s += "\n"
        return s

    def print_path(self, path) -> None:
        map_copy = deepcopy(self.map)
        for p in path:
            map_copy[p[1]][p[0]] = '*'
        s = ''
        for y in map_copy:
            for x in y:
                s += self.parse[x]
            s += "\n"
        
        print(s)
    
    @functools.lru_cache(maxsize=10000)
    def dijkstra(self, src: tuple, dest: tuple):
        
        def get_neighbours(x, y):
            moves = [(1,0), (0,1), (-1,0), (0,-1)]
            return [(x+a, y+b) for a, b in moves if 0 <= x+a < len(self.map[0]) and 0 <= y+b < len(self.map) and self.map[y+b][x+a] == 1]
            
        pq = PriorityQueue()
        dist = dict()
        prev = dict()
        not_visited = set()
        
        dist[src] = 0

        # init pq, not_visisted, dist and prev
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                if cell == 1:
                    if (x, y) != src:
                        dist[(x,y)] = 1000000
                        prev[(x,y)] = None
                    pq.add_task((x,y), dist[(x,y)]) # add to pq
                    not_visited.add((x,y))

        # finding shortest paths
        next = pq.pop_task()
        while next:
            not_visited.remove(next)
            for neighbour in get_neighbours(next[0], next[1]):
                if neighbour in not_visited:
                    alt_dist = dist[next] + 1
                    if alt_dist < dist[neighbour]:
                        pq.remove_task(neighbour)
                        dist[neighbour] = alt_dist
                        prev[neighbour] = next
                        pq.add_task(neighbour, alt_dist)
            next = pq.pop_task()

        # getting shortest path
        path = []
        while True:
            path.append(dest)
            if not prev.get(dest):
                break
            dest = prev[dest]
        path.reverse()
        return path


if __name__ == "__main__":
    m = Map()
    print(m)
    t = time.time()
    path = m.dijkstra((2,1), (20,10))
    print(path, "\nin: ", time.time()-t)
    m.print_path(path)