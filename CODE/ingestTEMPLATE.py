import shelve

# From Quizes
#       D1: Shipment of gold damaged in fire.
#       D2: Delivery of silver arrived in a silver truck.
#       D3: Shipment of gold arrived in a truck.
#       D4: Truck arrived damaged.

#index = [
#        { "term": "a", "tfs": [1,1,1,0] },
#        { "term": "damaged", "tfs": [1,0,0,1] },
#        { "term": "delivery", "tfs": [0,1,0,0] },
#        { "term": "fire", "tfs": [1,0,0,0] },
#        { "term": "arrived", "tfs": [0,1,1,1] },
#        { "term": "gold", "tfs": [1,0,1,0] },
#        { "term": "in", "tfs": [1,1,1,0] },
#        { "term": "of", "tfs": [1,1,1,0] },
#        { "term": "shipment", "tfs": [1,0,1,0] },
#        { "term": "silver", "tfs": [0,2,0,0] },
#        { "term": "truck", "tfs": [0,1,1,1] }
#]
index = [
        { "a": [1,1,1,0] },
        { "damaged": [1,0,0,1] },
        { "delivery": [0,1,0,0] },
        { "fire": [1,0,0,0] },
        { "arrived": [0,1,1,1] },
        { "gold": [1,0,1,0] },
        { "in": [1,1,1,0] },
        { "of": [1,1,1,0] },
        { "shipment": [1,0,1,0] },
        { "silver": [0,2,0,0] },
        { "truck": [0,1,1,1] }
]

#doc_key = [
#        { "name": "D1", "path":"loc1" },
#        { "name": "D2", "path":"loc2" },
#        { "name": "D3", "path":"loc3" },
#        { "name": "D4", "path":"loc4" }
#]
doc_key = [
        { "D1": ["id1", "loc1"] },
        { "D2": ["id2", "loc2"] },
        { "D3": ["id3", "loc3"] },
        { "D4": ["id4", "loc4"] }
]

d = shelve.open('OUTPUT/ingestOutput')
d['index'] = index
d['doc_key'] = doc_key
d.close()

