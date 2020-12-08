import pandas as pd
import numpy as np
import gurobipy as gu

class InitialPatternsGenerator:
	def __init__(self, nbItems):
		columns = ['PatternCost', 'PatternFill']
		patterns = pd.DataFrame(index=range(nbItems), columns=columns)
		self.patternDF = patterns
		self.nbItems = nbItems

	def generateBasicInitialPatterns(self):
		self.patternDF['PatternCost'] = 1
		self.patternDF['PatternFill'] = [np.where(self.patternDF.index==j, 1, 0) for j in range(self.nbItems)]
		return self.patternDF


class MasterProblem:
	def __init__(self, patternDF, inputDF):
		self.patternCost = patternDF['PatternCost'].values
		self.pattern = patternDF['PatternFill'].values
		self.amount = inputDF['Amount'].values
		self.model = gu.model('MasterProblem')
		self.patternsIndex = patternDF.index.values

	def buildModel(self):
		self.generateVariables()
		self.generateConstraints()
		self.generateObjective()
		self.model.update()

	def generateVariables(self):
		self.patternUseVar = self.model.addVars(self.patternsIndex, lb=0, ub=sum(self.amount), vtype=gu.GRB.INTEGER, name='PatternUseVar')

	def generateConstraints(self):
		for i in range(len(self.patternsIndex)):
			self.model.addConstr(gu.quicksum(self.pattern[p][i] * self.patternUseVar[p] for p in self.patternsIndex) >= self.amount[i], 'C'+str(i))

	def generateObjective(self):
		self.model.setObjective(gu.quicksum(self.patternUseVar[p] * self.patternCost[p] for p in self.patternsIndex), sense=gu.MINIMIZE)

	def addColumn(self, objective, newPattern):	
		ctName = ('PatternUseVar[%s]' %len(self.model.getVars()))
		newColumn = gu.Column(newPattern, self.model.getConstrs())
		self.model.addVar(vtype = gu.GRB.INTEGER, lb=0, obj=objective, column=newColumn, name=ctName)
		self.model.update()

	def solveModel(self, timeLimit=None, GAP='EPSILON'):
		self.model.setParam('TimeLimit', timeLimit)
		self.model.setParam('MIPGap', 'EPSILON')
		self.model.optimize()


class SubProblem:
	def __init__(self, inputDF, rollWidth, duals):
		self.patternCost = patternDF['PatternCost'].values
		self.pattern = patternDF['PatternFill'].values
		self.amount = inputDF['Amount'].values
		self.pieceSize = inputDF['Size'].values
		self.rollWidth = rollWidth
		self.duals = duals
		self.model = gu.model('SubProblem')
		self.piecesIndex = inputDF.index.values

	def buildModel(self):
		self.generateVariables()
		self.generateConstraints()
		self.generateObjective()
		self.model.update()

	def generateVariables(self):
		self.patternUseVar = self.model.addVars(self.patternsIndex, lb=0, ub=sum(self.amount), vtype=gu.GRB.INTEGER, name='PatternUseVar')

	def generateConstraints(self):
		for i in range(len(self.patternsIndex)):
			self.model.addConstr(gu.quicksum(self.pattern[p][i] * self.patternUseVar[p] for p in self.patternsIndex) >= self.amount[i], 'C'+str(i))

	def generateObjective(self):
		self.model.setObjective(gu.quicksum(self.patternUseVar[p] * self.patternCost[p] for p in self.patternsIndex), sense=gu.MINIMIZE)

	def getNewPattern(self):
		return self.model.gettAtr('X', self.model.getVars())

# Generate Initial Patterns
patternGenerator = InitialPatternsGenerator(len(inputDF))
patternDF = patternGenerator.generateBasicInitialPatterns()

# Build Master Problem with initial columns
master = MasterProblem(patternDF, inputDF)
master.buildModel()

modelImprovable = True

while modelImprovable:
	# Solved relaxed Master
	master.solveRelaxedModel()
	duals = master.getDuals()
	# Build SubProblem
	subproblem = SubProblem(inputDF, rollWidth, duals)
	subproblem.buildModel()
	subproblem.solveModel(120, 0.05)
	# Check if new pattern improves solution
	modelImprovable = (subproblem.getObjectiveValue() - 1) > 0
	# Add new generated pattern to master and iterate





