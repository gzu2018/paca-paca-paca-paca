
class DefaultAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  # dictionary of two items (enemy1 & enemy 2) which each contain a list of tuples (corrdinates)
  enemyPositions = {}
  turnCount = 0 

  def updateEnemyPositions(self):
    """"""
    DefaultAgent.turnCount += 1
    currentObservation = self.getCurrentObservation()
    for index, history in DefaultAgent.enemyPositions.items():
      x, y = currentObservation.getAgentPosition(index)
      px, py = history[-1]
      possible = myLegalMoves(px, py, currentObservation)
      minspot = (px, py)
      mindist = 9999
      for spot in possible:
        dist = self.getMazeDistance((x, y), spot)
        if dist < mindist and not currentObservation.hasWall(x, y):
          mindist = dist
          minspot = spot
      history.append(minspot)
    
  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)
    self.start = gameState.getAgentPosition(self.index)

    '''
    Your initialization code goes here, if you need any.
    '''
    self.pelletCount = 0
    for opponent in self.getOpponents(gameState):
      DefaultAgent.enemyPositions[opponent] = [gameState.getInitialAgentPosition(opponent)]

  def getClosestEnemy(self, pos, gameState):
    minEnemy = None
    mindist = 9999
    for index in DefaultAgent.enemyPositions.keys():
      lastLoc = DefaultAgent.enemyPositions[index][-1]
      enemydist = self.getMazeDistance(pos, lastLoc)
      if enemydist < mindist:
        minEnemy = index
        mindist = enemydist
    return (minEnemy, mindist)
      
  def getSafestFood(self, gameState):
    pq = PriorityQueue()
    foods = self.getFood(gameState)
    me = gameState.getAgentPosition(self.index)
    for x in range(0, foods.width):
      for y in range(0, foods.height):
        if not foods[x][y]:
          continue
        _, ghostdist = self.getClosestEnemy((x, y), gameState)
        medist = self.getMazeDistance((x, y), me)
        priority = 10000
        if ghostdist != 0:
          priority = (medist + (1.0 / ghostdist) * 1)
        pq.push((x, y), priority)
    return pq.pop()
        
  def getSafestHome(self, gameState):
    column = gameState.getWalls().width / 2 - 1
    height = gameState.getWalls().height
    pq = PriorityQueue()
    me = gameState.getAgentPosition(self.index)
    for y in range(0, height):
      if not gameState.hasWall(column, y):
        priority = 10000
        _, ghostdist = self.getClosestEnemy((column, y), gameState)
        medist = self.getMazeDistance((column, y), me)
        priority = 10000
        if medist != 0:
          priority = -(ghostdist + (1.0 / medist))
        pq.push((column, y), priority)
    return pq.pop()
        
  def aStarSearch(self, food, gameState, heuristic=manhattanDistance):
    """Search the node that has the lowest combined cost and heuristic first."""
    pq = PriorityQueue() # Priority Queue
    expanded = [] # list of explored nodes
    me = gameState.getAgentPosition(self.index)
    startState = (me, [])
    pq.push(startState, heuristic(startState[0], food)) # stores states as tuple of (state, direction), initial node based on heuristic
    while not pq.isEmpty():
      state, directions = pq.pop() # gets state and direction
      if state[0] == food[0] and state[1] == food[1]: # returns direction if goal state
        return directions
      else:
        if state not in expanded: # checks if state has been expanded 
          expanded.append(state) # adds state to expanded list
          tmp = myLegalMovesWithDirection(state, gameState) 
          for item in tmp: # push all non expanded nodes into priority queue
            if item[0] not in expanded:
              pq.push((item[0], directions + [item[1]]), heuristic(item[0], food))
    return [] #return empty if no goal node found

  def inHome(self, position, gameState):
    x, _ = position;
    if self.red:
      return x <= (gameState.getWalls().width / 2) - 1
    else:
      return x >= (gameState.getWalls().width / 2) - 1
  
  def chooseAction(self, gameState):
    # if (DefaultAgent.turnCount % 2) == 0:
    self.updateEnemyPositions()
    # else:
      # DefaultAgent.turnCount += 1
    me = gameState.getAgentPosition(self.index)
    if self.inHome(me, gameState):
      self.pelletCount = 0
    _, ghostdist = self.getClosestEnemy(me, gameState)
    # main decisions
    if not self.inHome(me, gameState) and ghostdist < 3:
      # run awway from a nearby ghost
      mindist = 9999
      moves = gameState.getLegalActions(self.index)
      bestAction = moves[0]
      for move in moves:
        np = nextPosition(me, move)
        if gameState.hasWall(np[0], np[1]):
          continue
        _, gdist = self.getClosestEnemy(np, gameState)
        if gdist < mindist:
          mindist = gdist
          bestAction = move
      return bestAction
    elif self.pelletCount >= 2:
      # go home
      bestHome = self.getSafestHome(gameState)
      actions = self.aStarSearch(bestHome, gameState)
      action = actions[0]
      return action
    else:
      # go find food
      bestFood = self.getSafestFood(gameState)
      actions = self.aStarSearch(bestFood, gameState)
      action = actions[0]
      nx, ny = nextPosition(me, action)
      if self.getFood(gameState)[nx][ny]:
        self.pelletCount += 1
      return actions[0]
  
###################
## Attack Agent  ##
###################
class AttackAgent(DefaultAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def __init__(self, index, timeForComputing = .1):
    super().__init__(self, index, timeForComputing)
    self.pelletCount = 0

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)

###################
## Defend Agent  ##
###################
class DefendAgent(DefaultAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)



  
def myLegalMoves(x, y, gameState):
  actions = [(x+1, y), (x-1, y), (x,y+1), (x, y-1), (x,y)]
  for index in range(len(actions) - 1, -1, -1):
    a, b = actions[index]
    if gameState.hasWall(a, b):
      actions.remove((a,b))
  return actions

def myLegalMovesWithDirection(coord, gameState):
  x, y = coord
  actions = []
  width = gameState.getWalls().width
  height = gameState.getWalls().height
  if x+1 < width and not gameState.hasWall(x+1, y):
    actions.append(((x+1, y),Directions.EAST))
  if x-1 >= 0 and not gameState.hasWall(x-1, y):
    actions.append(((x-1, y), Directions.WEST))
  if y+1 < height and not gameState.hasWall(x, y+1):
    actions.append(((x, y+1), Directions.NORTH))
  if y-1 >= 0 and not gameState.hasWall(x, y-1):
    actions.append(((x, y-1), Directions.SOUTH))
  return actions

def nextPosition(pos, action):
  x, y = pos
  if action == Directions.NORTH:
    return (x, y+1)
  elif action == Directions.EAST:
    return (x+1, y)
  elif action == Directions.SOUTH:
    return (x, y-1)
  elif action == Directions.WEST:
    return (x+1, y)
  else:
    return (x, y)
