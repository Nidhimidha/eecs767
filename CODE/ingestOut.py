# From Quizes
# 	D1: Shipment of gold damaged in fire.
#	D2: Delivery of silver arrived in a silver truck.
#	D3: Shipment of gold arrived in a truck.
#	D4: Truck arrived damaged.
index = [
	{ "term": "a", "tfs": [0,1,1,0] },
	{ "term": "arrived", "tfs": [0,1,1,1] },
	{ "term": "damaged", "tfs": [1,0,0,1] },
	{ "term": "delivery", "tfs": [0,1,0,0] },
	{ "term": "fire", "tfs": [1,0,0,0] },
	{ "term": "gold", "tfs": [1,0,1,0] },
	{ "term": "in", "tfs": [1,1,1,0] },
	{ "term": "of", "tfs": [1,1,1,0] },
	{ "term": "shipment", "tfs": [1,0,1,0] },
	{ "term": "silver", "tfs": [0,2,0,0] },
	{ "term": "truck", "tfs": [0,1,1,1] }
]

doc_key = [
	{ "name": "D1", "path":"loc1" },
	{ "name": "D2", "path":"loc2" },
	{ "name": "D3", "path":"loc3" },
	{ "name": "D4", "path":"loc4" }
]
