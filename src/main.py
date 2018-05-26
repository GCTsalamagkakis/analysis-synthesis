####################################################################################
# Analysis and Synthesis of sequential circuits by G. C. Tsalamagkakis & K. Mantos #
# Compatible in python 3.x							   							   												 #
####################################################################################

import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from anytree import *
from KMapSolver import *

class Main(QMainWindow):
	map_data = [[]]
	all_vars = ''
	KMapSolver = None

	def __init__(self):
		super().__init__()
		self.initUI()

	def closeEvent(self, event):
		sys.exit()

	def initUI(self):
		self.createButton('Analysis', 600, 350, 0, 0, self.AnalysisMain)
		self.createButton('Synthesis', 600, 350, 600, 0, self.SynthesisMain)
		self.setFixedSize(1200, 350)
		self.setWindowTitle('Sequential circuit synthesis and analysis')
		self.show()

	def createButton(self, name, width, height, x, y, functionName):
		btn = QPushButton(name, self)
		btn.setStyleSheet('QPushButton {color: red;}')
		btn.setFont(QFont('SansSerif', 14))
		btn.clicked.connect(functionName)
		btn.resize(width, height)
		btn.move(x, y)

	def AnalysisMain(self):
		options = QFileDialog.Options()
		file, _ = QFileDialog.getOpenFileNames(None, "Select a JSON file", "", "JSON Files (*.json)", options=options)
		try:
			data = json.load(open(file[0]))
			equations = []
			totalOutputs = 0
			totalInputs = 0
			# Parse gates / json file
			for i in data:
				flag = False
				if data[i]["isGate"]:
					for output in data[i]["outputs"]:
						if len(data[output["id"]]["outputs"]) == 0:
							flag = True
							break
				if flag or "flipflop" in data[i]["type"]:
					root = Node(data[i]["type"])
					if "flipflop" in data[i]["type"]:
						root = self.CalculateGate(data, i, root)
					else:
						self.CalculateGate(data, i, root)
					if root is not None:
						equation = ""
						equation += self.CalculateEquation(equation, root)
						if "flipflop" in data[i]["type"]:
							equation = data[i]["type"] + " = " + equation
						else:
							equation = data[data[i]["outputs"][0]["id"]]["type"] + " = " + equation
						equations.append(equation)
				else:
					if len(data[i]["outputs"]) == 0:
						totalOutputs += 1
					if len(data[i]["inputs"]) == 0:
						totalInputs += 1
				if "flipflop" in data[i]["type"]:
					totalInputs += 1
					totalOutputs += 1
			# Create equations window
			self.equationsUI = QTableWidget()
			self.equationsUI.setEditTriggers(QTableWidget.NoEditTriggers)
			self.equationsUI.horizontalHeader().hide()
			self.equationsUI.verticalHeader().hide()
			self.equationsUI.setWindowTitle('Equations')
			self.equationsUI.setRowCount(len(equations))
			self.equationsUI.setColumnCount(1)
			self.equationsUI.move(0,app.desktop().screenGeometry().height()/4)
			for i, eq in enumerate(equations):
				self.equationsUI.setItem(i, 0, QTableWidgetItem(eq.replace(" and "," * ").replace(" or "," + ").replace(" nand ",' \u22BC ').replace(" xor ",' \u2295 ').replace(" nor "," \u22BD ")))
			self.equationsUI.setFont(QFont("SansSerif", 14))
			self.equationsUI.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
			self.equationsUI.resizeColumnsToContents()
			self.equationsUI.show()
			# Create state table window
			self.stateTable = QTableWidget()
			self.stateTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
			self.stateTable.setEditTriggers(QTableWidget.NoEditTriggers)
			self.stateTable.horizontalHeader().hide()
			self.stateTable.verticalHeader().hide()
			self.stateTable.setWindowTitle('State table')
			self.stateTable.setRowCount(2+2**totalInputs)
			self.stateTable.setColumnCount(totalInputs + totalOutputs)
			self.stateTable.move(self.equationsUI.size().width()+app.desktop().screenGeometry().width()/100, app.desktop().screenGeometry().height()/4)
			self.stateTable.setItem(0, 0, QTableWidgetItem("Inputs"))
			if totalInputs > 1:
				self.stateTable.setSpan(0, 0, 1, totalInputs)
			self.stateTable.setItem(0, totalInputs, QTableWidgetItem("Outputs"))
			if totalOutputs > 1:
				self.stateTable.setSpan(0, totalInputs, 1, totalOutputs)
			counter1 = counter2 = 0
			place = {}
			flipflopNames = []
			signalNamesInputs = []
			signalNamesOutputs = []
			for value in data:
				if not data[value]["isGate"]:
					if len(data[value]["inputs"]) == 0:
						signalNamesInputs.append(data[value]["type"])
					if len(data[value]["outputs"]) == 0:
						self.stateTable.setItem(1, totalInputs+counter1, QTableWidgetItem(data[value]["type"]))
						place[data[value]["type"]] = totalInputs + counter1
						signalNamesOutputs.append(data[value]["type"])
						counter1 += 1
					else:
						if "flipflop" in data[value]["type"]:
							self.stateTable.setItem(1, totalInputs+counter1, QTableWidgetItem(data[value]["type"]+"+1"))
							place[data[value]["type"]+"+1"] = totalInputs + counter1
							flipflopNames.append(data[value]["type"])
							counter1 += 1
						self.stateTable.setItem(1, counter2, QTableWidgetItem(data[value]["type"]))
						place[data[value]["type"]] = counter2
						counter2 += 1
			counter1 = 0
			for value in flipflopNames:
				self.stateTable.setItem(1, counter1, QTableWidgetItem(value))
				counter1 += 1
			for value in signalNamesInputs:
				self.stateTable.setItem(1, counter1, QTableWidgetItem(value))
				counter1 += 1
			for value in flipflopNames:
				self.stateTable.setItem(1, counter1, QTableWidgetItem(value+"+1"))
				counter1 += 1
			for value in signalNamesOutputs:
				self.stateTable.setItem(1, counter1, QTableWidgetItem(value))
				counter1 += 1
			for i in range(2**totalInputs):
				for j in range(totalInputs):
					self.stateTable.setItem(2+i, j, QTableWidgetItem(format(i, '0' + str(totalInputs) + 'b')[j:j+1]))
			for i in range(2**totalInputs):
				for j in range(totalInputs, totalInputs+totalOutputs):
					outputsTable = equations[j-totalInputs].split(" = ")[1]
					for k in range(totalInputs):
						outputsTable = outputsTable.replace("xor","^").replace("nand", "not and").replace("nor", "not or").replace(self.stateTable.item(1,k).text(),self.stateTable.item(2+i,k).text())
					if "flipflop" in equations[j-totalInputs].split(" = ")[0]:
						self.stateTable.setItem(2+i, place[equations[j-totalInputs].split(" = ")[0]+"+1"], QTableWidgetItem(str(int(eval(outputsTable)))))
					else:
						self.stateTable.setItem(2+i, place[equations[j-totalInputs].split(" = ")[0]], QTableWidgetItem(str(int(eval(outputsTable)))))
			self.stateTable.show()
			# Create state diagram window
			self.stateDiagram = QTableWidget()
			self.stateDiagram.setEditTriggers(QTableWidget.NoEditTriggers)
			self.stateDiagram.horizontalHeader().hide()
			self.stateDiagram.verticalHeader().hide()
			self.stateDiagram.setWindowTitle('State diagram')
			self.stateDiagram.setRowCount(2**totalInputs)
			self.stateDiagram.setColumnCount(1)
			self.stateDiagram.move(self.equationsUI.size().width()+self.stateTable.size().width()+2*app.desktop().screenGeometry().width()/100, app.desktop().screenGeometry().height()/4)
			for i in range(2**totalInputs):
				flipflopNamesInputsTemp = ""
				for j in range(len(flipflopNames)):
					flipflopNamesInputsTemp += self.stateTable.item(i+2, j).text()
				flipflopNamesOutputsTemp = ""
				for j in range(len(flipflopNames)):
					flipflopNamesOutputsTemp += self.stateTable.item(i+2, j+totalInputs).text()
				signalNamesInputsTemp = ""
				for j in range(len(signalNamesInputs)):
					signalNamesInputsTemp += self.stateTable.item(i+2, j+len(flipflopNames)).text()
				signalNamesOutputsTemp = ""
				for j in range(len(signalNamesOutputs)):
					signalNamesOutputsTemp += self.stateTable.item(i+2, j+len(flipflopNames)+totalInputs).text()
				self.stateDiagram.setItem(i, 0, QTableWidgetItem(flipflopNamesInputsTemp + " --> " + flipflopNamesOutputsTemp + " (" + signalNamesInputsTemp + "/" + signalNamesOutputsTemp + ")"))
			self.stateDiagram.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
			self.stateDiagram.resizeColumnsToContents()
			self.stateDiagram.show()
		except Exception as e:
			pass

	def CalculateEquation(self, equation, parent):
		# Calculate equation in readable form, recursively
		equation += "("
		for position, child in enumerate(parent.children):
			if len(child.children) > 0:
				if "not" in parent.name:
					equation += parent.name+self.CalculateEquation(equation, child)+")"
				else:
					equation = self.CalculateEquation(equation, child)
				if position != len(parent.children)-1:
					equation += " " + parent.name + " "
			else:
				if position == len(parent.children)-1:
					if "not" in parent.name:
						equation += parent.name+"("+child.name+")"
					else:
						equation += child.name
				else:
					equation += child.name + " " + parent.name + " "
		equation += ")"
		return equation

	def CalculateGate(self, data, parentID, parentObject):
		# Create equation using tree structure before calculating
		parentFlipFlop = False
		returnNewParent = False
		if "flipflop" in data[parentID]["type"]:
			parentFlipFlop = True
		for pos, input in enumerate(data[parentID]["inputs"]):
			if data[input["id"]]["isGate"]:
				parentObjectChild = Node(data[input["id"]]["type"], parent=parentObject)
				if parentFlipFlop:
					parentObjectChild.parent = None
					returnNewParent = True
					parentFlipFlop = False
				self.CalculateGate(data, input["id"], parentObjectChild)
			else:
				child = Node(data[input["id"]]["type"], parent=parentObject)
		if returnNewParent:
			return parentObjectChild

	def SynthesisMain(self):
		options = QFileDialog.Options()
		files, _ = QFileDialog.getOpenFileNames(None, "Select a TEXT file", "", "TEXT Files (*.txt)", options=options)
		try:
			with open(files[0]) as file:
				# Parse states from txt file
				lines = file.read().splitlines()
				totalInputs = len(lines[0].split(" ")[0]) + len(lines[0].split(" ")[3].split("/")[0])-1
				totalOutputs = len(lines[0].split(" ")[2]) + len(lines[0].split(" ")[3].split("/")[1])-1
				totalFlipFlops = len(lines[0].split(" ")[0])
				totalSignalsInputs = totalInputs - totalFlipFlops
				totalSignalsOutputs = totalOutputs - totalFlipFlops
				# Create state table window
				self.stateTable = QTableWidget()
				self.stateTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
				self.stateTable.setEditTriggers(QTableWidget.NoEditTriggers)
				self.stateTable.horizontalHeader().hide()
				self.stateTable.verticalHeader().hide()
				self.stateTable.setWindowTitle('State table')
				self.stateTable.setRowCount(2+2**totalInputs)
				self.stateTable.setColumnCount(totalInputs + totalOutputs)
				self.stateTable.move(0, app.desktop().screenGeometry().height()/4)
				self.stateTable.setItem(0, 0, QTableWidgetItem("Inputs"))
				if totalInputs > 1:
					self.stateTable.setSpan(0, 0, 1, totalInputs)
				self.stateTable.setItem(0, totalInputs, QTableWidgetItem("Outputs"))
				if totalOutputs > 1:
					self.stateTable.setSpan(0, totalInputs, 1, totalOutputs)
				for i in range(totalFlipFlops):
					self.stateTable.setItem(1, i, QTableWidgetItem(str(i+1)+"flipflop"))
					self.stateTable.setItem(1, totalInputs+i, QTableWidgetItem(str(i+1)+"flipflop+1"))
				for i in range(totalSignalsInputs):
					self.stateTable.setItem(1, totalFlipFlops+i, QTableWidgetItem(str(i+1)+"signalInput"))
				for i in range(totalSignalsOutputs):
					self.stateTable.setItem(1, totalInputs+totalFlipFlops+i, QTableWidgetItem(str(i+1)+"signalOutput"))
				for i in range(len(lines)):
					for j in range(totalFlipFlops):
						self.stateTable.setItem(2+i, j, QTableWidgetItem(lines[i].split(" ")[0][j]))
						self.stateTable.setItem(2+i, totalInputs+j, QTableWidgetItem(lines[i].split(" ")[2][j]))
					for j in range(totalSignalsInputs):
						self.stateTable.setItem(2+i, totalFlipFlops+j, QTableWidgetItem(lines[i].split(" ")[3].split("/")[0][j+1]))
					for j in range(totalSignalsOutputs):
						self.stateTable.setItem(2+i, totalInputs+totalFlipFlops+j, QTableWidgetItem(lines[i].split(" ")[3].split("/")[1][j]))
				self.stateTable.show()
				# Create excitation table window
				self.excitationΤable = QTableWidget()
				self.excitationΤable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
				self.excitationΤable.setEditTriggers(QTableWidget.NoEditTriggers)
				self.excitationΤable.horizontalHeader().hide()
				self.excitationΤable.verticalHeader().hide()
				self.excitationΤable.setWindowTitle('Excitation table')
				self.excitationΤable.setRowCount(2+2**totalInputs)
				self.excitationΤable.setColumnCount(totalInputs+totalOutputs+totalFlipFlops)
				self.excitationΤable.move(self.stateTable.size().width()+app.desktop().screenGeometry().width()/100, app.desktop().screenGeometry().height()/4)
				self.excitationΤable.setItem(0, 0, QTableWidgetItem("Inputs"))
				if totalInputs > 1:
					self.excitationΤable.setSpan(0, 0, 1, totalInputs)
				self.excitationΤable.setItem(0, totalInputs, QTableWidgetItem("Outputs"))
				if totalOutputs > 1:
					self.excitationΤable.setSpan(0, totalInputs, 1, totalOutputs)
				self.excitationΤable.setItem(0, totalInputs+totalOutputs, QTableWidgetItem("FlipFlop Inputs"))
				self.excitationΤable.setSpan(0, totalInputs+totalOutputs, 1, totalFlipFlops*2)
				for i in range(totalFlipFlops):
					self.excitationΤable.setItem(1, i, QTableWidgetItem(str(i+1)+"flipflop"))
					self.excitationΤable.setItem(1, totalInputs+i, QTableWidgetItem(str(i+1)+"flipflop+1"))
				for i in range(totalSignalsInputs):
					self.excitationΤable.setItem(1, totalFlipFlops+i, QTableWidgetItem(str(i+1)+"signalInput"))
				for i in range(totalSignalsOutputs):
					self.excitationΤable.setItem(1, totalInputs+totalFlipFlops+i, QTableWidgetItem(str(i+1)+"signalOutput"))
				for i in range(totalFlipFlops):
					self.excitationΤable.setItem(1, totalInputs+totalOutputs+i, QTableWidgetItem("D"+str(i+1)+"flipflop"))
				for i in range(len(lines)):
					for j in range(totalFlipFlops):
						self.excitationΤable.setItem(2+i, j, QTableWidgetItem(lines[i].split(" ")[0][j]))
						self.excitationΤable.setItem(2+i, totalInputs+j, QTableWidgetItem(lines[i].split(" ")[2][j]))
						self.excitationΤable.setItem(2+i, totalInputs+totalOutputs+j, QTableWidgetItem(lines[i].split(" ")[2][j]))
					for j in range(totalSignalsInputs):
						self.excitationΤable.setItem(2+i, totalFlipFlops+j, QTableWidgetItem(lines[i].split(" ")[3].split("/")[0][j+1]))
					for j in range(totalSignalsOutputs):
						self.excitationΤable.setItem(2+i, totalInputs+totalFlipFlops+j, QTableWidgetItem(lines[i].split(" ")[3].split("/")[1][j]))
				self.excitationΤable.show()
				# Create equations window
				self.equationsUI = QTableWidget()
				self.equationsUI.setEditTriggers(QTableWidget.NoEditTriggers)
				self.equationsUI.horizontalHeader().hide()
				self.equationsUI.verticalHeader().hide()
				self.equationsUI.setWindowTitle('Equations')
				self.equationsUI.setRowCount(totalOutputs)
				self.equationsUI.setColumnCount(1)
				self.equationsUI.move(0, app.desktop().screenGeometry().height()/15)
				equations = []
				# Handle equation depending on variables number
				for i in range(totalFlipFlops):
					if totalFlipFlops+totalSignalsInputs == 2:
						self.KMapSolver = KMapSolver2
						self.map_data = [[]]
						self.map_data[0] = [int(self.excitationΤable.item(2, totalInputs+i).text()), int(self.excitationΤable.item(3, totalInputs+i).text())]
						self.map_data.append([int(self.excitationΤable.item(4, totalInputs+i).text()), int(self.excitationΤable.item(5, totalInputs+i).text())])
					elif totalFlipFlops+totalSignalsInputs == 3:
						self.KMapSolver = KMapSolver3
						self.map_data = [[]]
						self.map_data[0] = [int(self.excitationΤable.item(2, totalInputs+i).text()), int(self.excitationΤable.item(3, totalInputs+i).text()), int(self.excitationΤable.item(4, totalInputs+i).text()), int(self.excitationΤable.item(5, totalInputs+i).text())]
						self.map_data.append([int(self.excitationΤable.item(6, totalInputs+i).text()), int(self.excitationΤable.item(7, totalInputs+i).text()), int(self.excitationΤable.item(8, totalInputs+i).text()), int(self.excitationΤable.item(9, totalInputs+i).text())])
					elif totalFlipFlops+totalSignalsInputs == 4:
						self.KMapSolver = KMapSolver4
						self.map_data = [[]]
						self.map_data[0] = [int(self.excitationΤable.item(2, totalInputs+i).text()), int(self.excitationΤable.item(3, totalInputs+i).text()), int(self.excitationΤable.item(4, totalInputs+i).text()), int(self.excitationΤable.item(5, totalInputs+i).text())]
						self.map_data.append([int(self.excitationΤable.item(6, totalInputs+i).text()), int(self.excitationΤable.item(7, totalInputs+i).text()), int(self.excitationΤable.item(8, totalInputs+i).text()), int(self.excitationΤable.item(9, totalInputs+i).text())])
						self.map_data.append([int(self.excitationΤable.item(10, totalInputs+i).text()), int(self.excitationΤable.item(11, totalInputs+i).text()), int(self.excitationΤable.item(12, totalInputs+i).text()), int(self.excitationΤable.item(13, totalInputs+i).text())])
						self.map_data.append([int(self.excitationΤable.item(14, totalInputs+i).text()), int(self.excitationΤable.item(15, totalInputs+i).text()), int(self.excitationΤable.item(16, totalInputs+i).text()), int(self.excitationΤable.item(17, totalInputs+i).text())])
					self.all_vars = self.excitationΤable.item(1, totalInputs+i).text()
					result = self.all_vars + " = " + self.calc_result()
					equations.append(result)
					self.equationsUI.setItem(i, 0, QTableWidgetItem(result))
				for i in range(totalSignalsOutputs):
					if totalFlipFlops+totalSignalsInputs == 2:
						self.KMapSolver = KMapSolver2
						self.map_data = [[]]
						self.map_data[0] = [int(self.excitationΤable.item(2, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(3, totalInputs+totalFlipFlops+i).text())]
						self.map_data.append([int(self.excitationΤable.item(4, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(5, totalInputs+totalFlipFlops+i).text())])
					elif totalFlipFlops+totalSignalsInputs == 3:
						self.KMapSolver = KMapSolver3
						self.map_data = [[]]
						self.map_data[0] = [int(self.excitationΤable.item(2, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(3, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(4, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(5, totalInputs+totalFlipFlops+i).text())]
						self.map_data.append([int(self.excitationΤable.item(6, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(7, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(8, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(9, totalInputs+totalFlipFlops+i).text())])
					elif totalFlipFlops+totalSignalsInputs == 4:
						self.KMapSolver = KMapSolver4
						self.map_data = [[]]
						self.map_data[0] = [int(self.excitationΤable.item(2, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(3, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(4, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(5, totalInputs+totalFlipFlops+i).text())]
						self.map_data.append([int(self.excitationΤable.item(6, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(7, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(8, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(9, totalInputs+totalFlipFlops+i).text())])
						self.map_data.append([int(self.excitationΤable.item(10, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(11, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(12, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(13, totalInputs+totalFlipFlops+i).text())])
						self.map_data.append([int(self.excitationΤable.item(14, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(15, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(16, totalInputs+totalFlipFlops+i).text()), int(self.excitationΤable.item(17, totalInputs+totalFlipFlops+i).text())])
					self.all_vars = self.excitationΤable.item(1, totalInputs+totalFlipFlops+i).text()
					result = self.all_vars + " = " + self.calc_result()
					equations.append(result)
					self.equationsUI.setItem(totalFlipFlops+i, 0, QTableWidgetItem(result))
				self.equationsUI.setFont(QFont("SansSerif", 14))
				self.equationsUI.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
				self.equationsUI.resizeColumnsToContents()
				self.equationsUI.show()
				# Create circuit window
				self.circuit = QTableWidget()
				self.circuit.setEditTriggers(QTableWidget.NoEditTriggers)
				self.circuit.horizontalHeader().setDefaultSectionSize(150)
				self.circuit.verticalHeader().setDefaultSectionSize(150)
				self.circuit.resize(160,500)
				self.circuit.setWindowTitle('Circuit')
				self.circuit.setRowCount(totalOutputs)
				self.circuit.setColumnCount(1)
				self.circuit.move(self.equationsUI.size().width()+app.desktop().screenGeometry().width()/100, app.desktop().screenGeometry().height()/15)
				for k, equation in enumerate(equations):
					# Printing circuit as tree
					root = Node(equation.split(" = ")[0])
					eq = equation.split(" = ")[1]
					mainGates = eq.split(" + ")
					if len(mainGates) > 1:
						varOR = Node("or", parent=root)
						for gate in mainGates:
							Node(gate, parent=varOR)
					else:
						Node(mainGates[0], parent=root)
					eq2 = ""
					for pre, _, node in RenderTree(root, style=DoubleStyle):
						eq2 += "%s%s\n" % (pre, node.name)
					self.circuit.setItem(k, 0, QTableWidgetItem(eq2))
				self.circuit.show()
		except Exception as e:
			pass

	def calc_result(self):
		# Give result to karnaugh map (for synthesis)
		k = self.KMapSolver(self.map_data)
		k.solve()
		return k.get_result()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = Main()
	sys.exit(app.exec_())
