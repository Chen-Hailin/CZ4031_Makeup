var newqepconfig = {
		container: "#newqep",

		nodeAlign: "BOTTOM",
		
		connectors: {
			type: 'step'
		},
		node: {
			HTMLclass: 'nodeExample1'
		}
					},
newqepNode_1 = {
						
						HTMLclass: 'white',
						HTMLid: 'newqep_id_1',
						text: {
							name: "Node Type: Aggregate",
							Cost: "Cost: 4.2e+04",
							Cost_Percentage: "Cost Percentage: 4%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: ""
						}
					},
newqepNode_2 = {
						parent: newqepNode_1,
						HTMLclass: 'white',
						HTMLid: 'newqep_id_2',
						text: {
							name: "Node Type: Gather Merge",
							Cost: "Cost: 2.5e+05",
							Cost_Percentage: "Cost Percentage: 21%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: ""
						}
					},
newqepNode_3 = {
						parent: newqepNode_2,
						HTMLclass: 'white',
						HTMLid: 'newqep_id_3',
						text: {
							name: "Node Type: Aggregate",
							Cost: "Cost: 1.9e+04",
							Cost_Percentage: "Cost Percentage: 2%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: ""
						}
					},
newqepNode_4 = {
						parent: newqepNode_3,
						HTMLclass: 'white',
						HTMLid: 'newqep_id_4',
						text: {
							name: "Node Type: Sort",
							Cost: "Cost: 2.1e+05",
							Cost_Percentage: "Cost Percentage: 18%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: ""
						}
					},
newqepNode_5 = {
						parent: newqepNode_4,
						HTMLclass: 'white',
						HTMLid: 'newqep_id_5',
						text: {
							name: "Node Type: Nested Loop",
							Cost: "Cost: 6.2e+05",
							Cost_Percentage: "Cost Percentage: 53%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: "Highest Cost!"
						}
					},
newqepNode_6 = {
						parent: newqepNode_5,
						HTMLclass: 'white',
						HTMLid: 'newqep_id_6',
						text: {
							name: "Node Type: Seq Scan",
							Cost: "Cost: 2.6e+04",
							Cost_Percentage: "Cost Percentage: 2%",
							Tables: "Tables: authorpublication",
							Join: "",
							Output: "Output: author_id, pub_id",
							highest_cost: ""
						}
					},
newqepNode_7 = {
						parent: newqepNode_5,
						HTMLclass: 'green',
						HTMLid: 'newqep_id_7',
						text: {
							name: "Node Type: Index Scan",
							Cost: "Cost: 4.8e-01",
							Cost_Percentage: "Cost Percentage: 0%",
							Tables: "Tables: publications",
							Join: "",
							Output: "Output: pub_id, pub_type, pub_key, title, year, month, cross_ref, origin, origin_name",
							highest_cost: ""
						}
					},
newqepchart_config = [newqepconfig, newqepNode_1, newqepNode_2, newqepNode_3, newqepNode_4, newqepNode_5, newqepNode_6, newqepNode_7];
var oldqepconfig = {
		container: "#oldqep",

		nodeAlign: "BOTTOM",
		
		connectors: {
			type: 'step'
		},
		node: {
			HTMLclass: 'nodeExample1'
		}
					},
oldqepNode_1 = {
						
						HTMLclass: 'white',
						HTMLid: 'oldqep_id_1',
						text: {
							name: "Node Type: Aggregate",
							Cost: "Cost: 4.2e+04",
							Cost_Percentage: "Cost Percentage: 4%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: ""
						}
					},
oldqepNode_2 = {
						parent: oldqepNode_1,
						HTMLclass: 'white',
						HTMLid: 'oldqep_id_2',
						text: {
							name: "Node Type: Gather Merge",
							Cost: "Cost: 2.5e+05",
							Cost_Percentage: "Cost Percentage: 21%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: ""
						}
					},
oldqepNode_3 = {
						parent: oldqepNode_2,
						HTMLclass: 'white',
						HTMLid: 'oldqep_id_3',
						text: {
							name: "Node Type: Aggregate",
							Cost: "Cost: 1.9e+04",
							Cost_Percentage: "Cost Percentage: 2%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: ""
						}
					},
oldqepNode_4 = {
						parent: oldqepNode_3,
						HTMLclass: 'white',
						HTMLid: 'oldqep_id_4',
						text: {
							name: "Node Type: Sort",
							Cost: "Cost: 2.1e+05",
							Cost_Percentage: "Cost Percentage: 18%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: ""
						}
					},
oldqepNode_5 = {
						parent: oldqepNode_4,
						HTMLclass: 'white',
						HTMLid: 'oldqep_id_5',
						text: {
							name: "Node Type: Nested Loop",
							Cost: "Cost: 6.1e+05",
							Cost_Percentage: "Cost Percentage: 53%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: "Highest Cost!"
						}
					},
oldqepNode_6 = {
						parent: oldqepNode_5,
						HTMLclass: 'purple',
						HTMLid: 'oldqep_id_6',
						text: {
							name: "Node Type: Seq Scan",
							Cost: "Cost: 2.6e+04",
							Cost_Percentage: "Cost Percentage: 2%",
							Tables: "Tables: authorpublication",
							Join: "",
							Output: "Output: author_id, pub_id",
							highest_cost: ""
						}
					},
oldqepNode_7 = {
						parent: oldqepNode_5,
						HTMLclass: 'white',
						HTMLid: 'oldqep_id_7',
						text: {
							name: "Node Type: Index Scan",
							Cost: "Cost: 4.8e-01",
							Cost_Percentage: "Cost Percentage: 0%",
							Tables: "Tables: publications",
							Join: "",
							Output: "Output: pub_id, pub_type, pub_key, title, year, month, cross_ref, origin, origin_name",
							highest_cost: ""
						}
					},
oldqepchart_config = [oldqepconfig, oldqepNode_1, oldqepNode_2, oldqepNode_3, oldqepNode_4, oldqepNode_5, oldqepNode_6, oldqepNode_7];
