from copy import deepcopy
import functools
from operator import ne
import time
import heapq
import itertools
import pygame

class PriorityQueue:
    pq = []
    entry_finder = {}
    REMOVED = '<removed-task>'
    counter = itertools.count()

    def __repr__(self) -> str:
        return str(self.pq) + str(self.entry_finder)

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


class MovableObject(pygame.sprite.Sprite):
    def __init__(self, pos: tuple = (0,0)) -> None:
        self.speed = 1
        self.position = pos
        self.position_frac = .0
        self.direction = (1,0)
        self.next_direction = (0,0)

    def move(self):
        x = self.position[0]+self.speed*self.direction[0]
        y = self.position[1]+self.speed*self.direction[1]
        self.position = (int(x), int(y))
        self.position_frac = x % 1 + y % 1


class Pacman(MovableObject):
    def __init__(self, pos: tuple = (0, 0)) -> None:
        super().__init__(pos)
        self.image = pygame.image.load("pacman.png")

class Map:
    map: list[list] = None
    parse = {'+': 0, '-': 1, 0: '+', 1: ' ', '*': '*'}
    paths = dict()

    def __init__(self) -> None:
        self.map = self.read_map()
        self.calculate_paths()

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

    def calculate_paths(self) -> None:
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                if cell == 1:
                    self.paths[(x,y)] = self.dijkstra((x, y))
    
    def get_neighbours(self, x, y):
        moves = [(1,0), (0,1), (-1,0), (0,-1)]
        return [(x+a, y+b) for a, b in moves if 0 <= x+a < len(self.map[0]) and 0 <= y+b < len(self.map) and self.map[y+b][x+a] == 1]
    
    def dijkstra(self, src: tuple):
        not_visited = PriorityQueue()
        dist = dict()
        prev = dict()
        dist[src] = 0

        # init pq, not_visisted, dist and prev
        for y, row in enumerate(self.map):
            for x, cell in enumerate(row):
                if cell == 1:
                    if (x, y) != src:
                        dist[(x,y)] = 1000000
                        prev[(x,y)] = None
                    not_visited.add_task((x,y), dist[(x,y)])
        
        # finding shortest paths
        next = not_visited.pop_task()
        while next:
            for neighbour in self.get_neighbours(next[0], next[1]):
                alt_dist = dist[next] + 1
                if alt_dist < dist[neighbour]:
                    dist[neighbour] = alt_dist
                    prev[neighbour] = next
                    not_visited.add_task(neighbour, alt_dist)
            next = not_visited.pop_task()
        
        return prev
    
    @functools.lru_cache(maxsize=10000)
    def get_path(self, src: tuple, dest: tuple):
        path = []
        prev = self.paths[src]
        while True:
            path.append(dest)
            if not prev.get(dest):
                break
            dest = prev[dest]
        path.reverse()
        return path

class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 1920/2, 1080/2
 
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        
    def on_loop(self):
        pass
    
    def on_render(self):
        pass
    
    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
 
if __name__ == "__main__":
    m = Map()
    path = m.get_path((2,1), (20,10))
    m.print_path(path)
    #game = App()
    #game.on_execute()