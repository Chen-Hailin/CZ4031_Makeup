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
						
						HTMLclass: 'green',
						HTMLid: 'newqep_id_1',
						text: {
							name: "Node Type: Gather",
							Cost: "Cost: 2.6e+05",
							Cost_Percentage: "Cost Percentage: 29%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: ""
						}
					},
newqepNode_2 = {
						parent: newqepNode_1,
						HTMLclass: 'green',
						HTMLid: 'newqep_id_2',
						text: {
							name: "Node Type: Nested Loop",
							Cost: "Cost: 6.2e+05",
							Cost_Percentage: "Cost Percentage: 68%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: "Highest Cost!"
						}
					},
newqepNode_3 = {
						parent: newqepNode_2,
						HTMLclass: 'green',
						HTMLid: 'newqep_id_3',
						text: {
							name: "Node Type: Seq Scan",
							Cost: "Cost: 2.6e+04",
							Cost_Percentage: "Cost Percentage: 3%",
							Tables: "Tables: authorpublication",
							Join: "",
							Output: "Output: author_id, pub_id",
							highest_cost: ""
						}
					},
newqepNode_4 = {
						parent: newqepNode_2,
						HTMLclass: 'green',
						HTMLid: 'newqep_id_4',
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
newqepchart_config = [newqepconfig, newqepNode_1, newqepNode_2, newqepNode_3, newqepNode_4];
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
						
						HTMLclass: 'purple',
						HTMLid: 'oldqep_id_1',
						text: {
							name: "Node Type: Hash Join",
							Cost: "Cost: 6.8e+04",
							Cost_Percentage: "Cost Percentage: 46%",
							Tables: "",
							Join: "Join: (authorpublication.pub_id = publications.pub_id)",
							Output: "",
							highest_cost: "Highest Cost!"
						}
					},
oldqepNode_2 = {
						parent: oldqepNode_1,
						HTMLclass: 'white',
						HTMLid: 'oldqep_id_2',
						text: {
							name: "Node Type: Seq Scan",
							Cost: "Cost: 4.4e+04",
							Cost_Percentage: "Cost Percentage: 30%",
							Tables: "Tables: authorpublication",
							Join: "",
							Output: "Output: pub_id",
							highest_cost: ""
						}
					},
oldqepNode_3 = {
						parent: oldqepNode_1,
						HTMLclass: 'purple',
						HTMLid: 'oldqep_id_3',
						text: {
							name: "Node Type: Hash",
							Cost: "Cost: 0.0e+00",
							Cost_Percentage: "Cost Percentage: 0%",
							Tables: "",
							Join: "",
							Output: "",
							highest_cost: ""
						}
					},
oldqepNode_4 = {
						parent: oldqepNode_3,
						HTMLclass: 'purple',
						HTMLid: 'oldqep_id_4',
						text: {
							name: "Node Type: Seq Scan",
							Cost: "Cost: 3.7e+04",
							Cost_Percentage: "Cost Percentage: 25%",
							Tables: "Tables: publications",
							Join: "",
							Output: "Output: title, year, pub_id",
							highest_cost: ""
						}
					},
oldqepchart_config = [oldqepconfig, oldqepNode_1, oldqepNode_2, oldqepNode_3, oldqepNode_4];
