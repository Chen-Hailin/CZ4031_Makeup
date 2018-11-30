import pdb
import json
import re
import sys
import traceback


class qep_node(object):
	tree_index = 0
	root = None
	highest_cost = {'Node':None, 'Cost':0}

	@staticmethod
	def reset_qep_tree():
		qep_node.tree_index = 0
		qep_node.root = None
		qep_node.highest_cost = {'Node':None, 'Cost':0}

	def __init__(self, d):
		qep_node.tree_index += 1
		setattr(self, 'id', qep_node.tree_index)
		for a, b in d.items():
			a = a.replace(' ', '_')  # replace space in key to _
			if (a == 'Plans'):  # rename sub tree plans to children to match intuition
				a = 'children'
			if isinstance(b, (list, tuple)):
				setattr(self, a, [qep_node(x) if isinstance(x, dict) else x for x in b])
			else:
				setattr(self, a, qep_node(b) if isinstance(b, dict) else b)
		# if root
		if self.id == 1:
			qep_node.root = self
			self.post_process()

	def post_process(self):
		self._post_process()
		qep_node.highest_cost['Node'].highest_cost = 'Highest Cost!'


	# getter method to call child nodes, return [] if no child
	def get_children(self):
		if hasattr(self, 'children'):
			if type(self.children) != type([]):  # only one child, make return iterable
				return [self.children]
			return self.children
		else:
			return []

	# add values including: Actual_Duration(diff in Actual Total Time), Cost(diff in Total Cost)
	def _post_process(self):
		aggregates = {
					  'Cost': sum([child.Total_Cost for child in self.get_children()])}
		#self.Actual_Duration = max(self.Actual_Total_Time - aggregates['Actual_Duration'], 0)
		self.Cost = max(self.Total_Cost - aggregates['Cost'], 0)
		self.highest_cost = ''
		if self.Cost > qep_node.highest_cost['Cost']:
			qep_node.highest_cost['Node'] = self
			qep_node.highest_cost['Cost'] = self.Cost
		if "Output" not in self.__dict__.keys():
			self.Output = []
		self.Cost_Percentage = float(self.Cost) / qep_node.root.Total_Cost
		#self.Duration_Percentage = float(self.Actual_Duration) / self.Actual_Total_Time
		for child in self.get_children():
			child._post_process()

	def get_node_by_id(self, _id):
		if self.id == _id:
			return self
		else:
			result = None
			for child in self.get_children():
				temp = child.get_node_by_id(_id)
				if temp != None:
					result = temp
			return result

	# test method to traverse the tree and print each node's id, pre-order
	def traverse_print_id(self):
		print(str(self.id) + ', ')
		for child in self.get_children():
			child.traverse_print_id()

	# return a list of Node_{id} for treant.js
	def traverse_treant_id(self, NODE):
		id_list = []
		id_list += [NODE + str(self.id)]
		for child in self.get_children():
			id_list.extend(child.traverse_treant_id(NODE))
		return id_list

	def convert_to_treant_config(self, parent_id=None, id_to_color=None, containerID=''):
		NODE = 'Node_'
		if containerID != '':
			NODE = containerID + NODE
		# convert the tree to js str config for Treant.js
		if parent_id is None:  # root node
			js_str = '''var {}config = {{
		container: "#custom-colored",

		nodeAlign: "BOTTOM",
		
		connectors: {{
			type: 'step'
		}},
		node: {{
			HTMLclass: 'nodeExample1'
		}}
					}},\n'''.format(containerID)
			if containerID != '':
				js_str = js_str.replace('custom-colored', containerID)
			parent_str = ''
		else:
			js_str = ''
			parent_str = "parent: {},".format(NODE + str(parent_id))
		try:
			color = 'white'
			if id_to_color and id_to_color.get(self.id):
				color = id_to_color.get(self.id)
			if len(self.get_children()) == 0: # leaf node
				output_str = 'Output: ' + ', '.join([re.sub(r".*\.", "", o) for o in self.Output])
			else:
				output_str = ''
			
			tables = ''
			if 'Scan' in self.Node_Type: # scan node
				tables = 'Tables: ' + self.Relation_Name

			join_cond = ''
			if 'Hash Join' in self.Node_Type: # join node
				join_cond = 'Join: ' + self.Hash_Cond
			elif 'Merge Join' in self.Node_Type: # join node
				join_cond = 'Join: ' + self.Merge_Cond


			js_str += '''{}{} = {{
						{}
						HTMLclass: '{}',
						HTMLid: '{}',
						text: {{
							name: "Node Type: {}",
							Cost: "Cost: {:.1e}",
							Cost_Percentage: "Cost Percentage: {:.0%}",
							Tables: "{}",
							Join: "{}",
							Output: "{}",
							highest_cost: "{}"
						}}
					}},\n'''.format(NODE, self.id, parent_str, color, containerID+'_id_'+str(self.id), self.Node_Type, self.Cost, 
									self.Cost_Percentage, tables, join_cond, output_str, self.highest_cost)
		except Exception as e:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_exception(exc_type, exc_value, exc_traceback)
			print(str(e))
			pdb.set_trace()
		for child in self.get_children():
			js_str += child.convert_to_treant_config(self.id, id_to_color, containerID=containerID)

		if parent_id is None:  # root node
			all_ids = self.traverse_treant_id(NODE)
			all_ids_str = ', '.join(all_ids)
			js_str += '{}chart_config = [{}config, {}];\n'.format(containerID, containerID, all_ids_str)

		# highlight node with highest cost
		#js_str += ''' markers = document.getElementsByClassName('node-highest_cost');
		#			  for(var j = 0; j < markers.length; j ++) {
		#				    markers[j].style.color = 'red';
		#			  }
		#			'''
		return js_str

	def search_unique_id(self):
		if self.Node_Type == 'Unique':
			return self.id
		else:
			for c in self.get_children():
				r = c.search_unique_id()
				if r > -1:
					return r
		return -1

	def search_output_id(self, attr):
		ids = []
		for c in self.get_children():
			r = c.search_output_id(attr)
			if len(r) > 0:
				ids.extend(r)
		if len(self.get_children()) == 0: # leaf node
			if "Output" in self.__dict__.keys():
				if type(self.Output) == type([]):
					if any([attr.lower() == re.sub(r".*\.", "", o.lower()) for o in self.Output]):
						return [self.id]
				elif type(self.Output) == type(''):
					if attr.lower() == re.sub(r".*\.", "", self.Output):
						return [self.id]
		return ids


	def search_join_id(self, join_relation):
		if "Join_Type" in self.__dict__.keys():
			if self.Node_Type == 'Hash Join':
				cond_str = self.Hash_Cond
				if join_relation.condition_left_attr in cond_str and join_relation.condition_right_attr in cond_str:
					return self.id
		for c in self.get_children():
			r = c.search_join_id(join_relation)
			if r > -1:
				return r
		return -1

	def search_cond(self, cond_str):
		if 'Scan' in self.Node_Type and "Filter" in self.__dict__.keys():
			processed_filter = re.sub('\)?::text', '', self.Filter)
			if cond_str in processed_filter:
				return self.id
		for c in self.get_children():
			r = c.search_cond(cond_str)
			if r > -1:
				return r
		return -1

	def _find_NL_cond(self, not_root=True):
		# find "index scan" in descendants
		cond = []
		if self.Node_Type == 'Index Scan':
			cond.append(self.Index_Cond)
		if not_root and "Join" in self.Node_Type or 'Nested Loop' == self.Node_Type: # reach another level of join node, stop
			return cond
		for c in self.get_children():
			r = c._find_NL_cond()
			cond.extend(r)
		return cond

	def search_join_nodes(self):
		nodes = []
		# for NL/Merge/Hash Join, add [join condition, its id]
		if self.Node_Type == 'Merge Join':
			nodes.append([self.Merge_Cond, self.id, self.Node_Type])
		
		elif self.Node_Type == 'Hash Join':
			nodes.append([self.Hash_Cond, self.id, self.Node_Type])

		elif 'Nested Loop' == self.Node_Type:
			NL_cond = self._find_NL_cond(False)
			if len(NL_cond) > 0:
				nodes.append([', '.join(NL_cond), self.id, self.Node_Type])

		for c in self.get_children():
			cns = c.search_join_nodes()
			nodes.extend(cns)
		return nodes

	def search_scan_nodes(self):
		nodes = []
		if 'Scan' in self.Node_Type: # scan node
			nodes.append([self.Relation_Name, self.id, self.Node_Type])

		for c in self.get_children():
			cns = c.search_scan_nodes()
			nodes.extend(cns)
		
		return nodes

	def search_types(self):
		types = []
		types.append([self.id, self.Node_Type])

		for c in self.get_children():
			cns = c.search_types()
			types.extend(cns)
		
		return types

	def assign_color_types(self, new_types, color):
		qep_to_col = {}
		if self.Node_Type in new_types:
			qep_to_col[self.id] = color
		for c in self.get_children():
			_qep_col = c.assign_color_types(new_types, color)
			qep_to_col.update(_qep_col)
		return qep_to_col


def parse_qep(json_file='sample_qep_big.json'):
	'''
	Args
		json_file: file path to json of qep (here I take sample on http://tatiyants.com/pev/#/plans/new)
	Return:
		qep_object: a root qep_node object
	'''
	json_str = open(json_file, 'r').readlines()  # read in qep json
	json_str = [re.sub(r'^ *', '', re.sub(r' *[+]?\n', '', jstr)) for jstr in
				json_str]  # eliminate space and \n at last and preceeding space
	json_str = ''.join(json_str)
	assert type(json_str) == type(''), 'json_str should be a string here'
	json_obj = json.loads(json_str)
	if type(json_obj) == type([]):
		json_obj = json_obj[0]
	qep_node.reset_qep_tree()
	qep_object = qep_node(json_obj['Plan'])
	# qep_object.post_process()
	return qep_object


def parse_qep_str(json_str):
	'''
	Args
		json_file: file path to json of qep (here I take sample on http://tatiyants.com/pev/#/plans/new)
	Return:
		qep_object: a root qep_node object
	'''
	assert type(json_str) == type(''), 'json_str should be a string here'
	json_obj = json.loads(json_str)
	if type(json_obj) == type([]):
		json_obj = json_obj[0]
	qep_node.reset_qep_tree()
	qep_object = qep_node(json_obj['Plan'])
	# qep_object.post_process()
	return qep_object


if __name__ == '__main__':
	qep_object = parse_qep('test_qep.json')
	pdb.set_trace()
	print(str(qep_object.convert_to_treant_config()))
