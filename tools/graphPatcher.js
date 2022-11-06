//This simple script adds back in nodes or edges that may have accidentally been deleted from the graph.
//Load the graph file.
const fs = require('fs');
const autoGraph = JSON.parse(fs.readFileSync('./london_underground_data-auto.json', 'utf8'));
let userGraph = JSON.parse(fs.readFileSync('./london_underground_data-cleaned.json', 'utf8'));

for (const audoNode of autoGraph.nodes)
{
    //If the autoNode has no edges, skip it.
    if (audoNode.adjacencyList.length == 0)
        continue;

    //If the userGraph is missing the node, add it.
    if (!userGraph.nodes.find(x => x.id == audoNode.id))
    {
        console.log("Adding node " + audoNode.id);
        userGraph.nodes.push(audoNode);
    }

    //If the userNode does not have the same edges, add the missing ones.
    const userNode = userGraph.nodes.find(x => x.id == audoNode.id);
    for (const autoEdge of audoNode.adjacencyList)
    {
        if (!userNode.adjacencyList.find(x => x.neighbouringNodeID == autoEdge.neighbouringNodeID))
        {
            console.log("Adding edge from " + userNode.id + " to " + autoEdge.neighbouringNodeID);
            userNode.adjacencyList.push(autoEdge);
        }
    }
}

//Save the patched graph to a file.
fs.writeFileSync('./london_underground_data-patched.json', JSON.stringify(userGraph));
