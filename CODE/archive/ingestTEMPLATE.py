import shelve
#
# From Quizes
#       D1: Shipment of gold damaged in fire.
#       D2: Delivery of silver arrived in a silver truck.
#       D3: Shipment of gold arrived in a truck.
#       D4: Truck arrived damaged.

# index = [
#       { Term1: [tf1, tf2, ..., tfn] },
#       { Term2: [tf1, tf2, ..., tfn] },
#       ...,
#       { Termm: [tf1, tf2, ..., tfn] }
# ]
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

# doc_key = [
#       { DocName1: [DocID1, DocLocation1] },
#       { DocName2: [DocID2, DocLocation2] },
#       ...,
#       { DocNamen: [DocIDn, DocLocationn] }
# ]
doc_key = [
        { "D1": ["id1", "loc1"] },
        { "D2": ["id2", "loc2"] },
        { "D3": ["id3", "loc3"] },
        { "D4": ["id4", "loc4"] }
]

# proximity = {
#       Term1: [ [DocID, Prox], [DocID, Prox], ..., [DocID, Prox] ],
#       Term2: [ [DocID, Prox], [DocID, Prox], ..., [DocID, Prox] ],
#       ...,
#       Termm: [ [DocID, Prox], [DocID, Prox], ..., [DocID, Prox] ]
# }
proximity = {
        "a": [ ["D2", 6], ["D3", 6] ],
        "damaged": [ ["D1", 4], ["D4", 3] ],
        "delivery": [ ["D2", 1] ],
        "fire": [ ["D1", 6] ],
        "arrived": [ ["D2", 4], ["D3", 4], ["D4", 2] ],
        "gold": [ ["D1", 3], ["D3", 3] ],
        "in": [ ["D1", 5], ["D2", 5], ["D3", 5] ],
        "of": [ ["D1", 2], ["D2", 2], ["D3", 2] ],
        "shipment": [ ["D1", 1], ["D3", 1] ],
        "silver": [ ["D2", 3], ["D2", 6] ],
        "truck": [ ["D2", 8], ["D3", 7], ["D4", 1] ]
}

d = shelve.open('OUTPUT/ingestOutput')
d['index'] = index
d['doc_key'] = doc_key
d['proximity'] = proximity
d.close()
