const urlParams = new URLSearchParams(window.location.search);
const topic = urlParams.get('topic');
let nodes = [];
let links = [];

fetch(`/api/node-data/${topic}`)
    .then(response => response.json())
    .then(nodeData => {
        // For demonstration, we'll use the sample data
        const data = nodeData;

        nodes = data.nodes;
        links = data.links;

        renderForceGraph(nodes, links);
    })
    .catch(error => console.error('Error loading node data:', error));

function renderForceGraph(nodes, links) {
    const width = window.innerWidth;
    const height = window.innerHeight;

    const svg = d3.select("#graphCanvas")
        .attr("width", width)
        .attr("height", height);

    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(150)) // Increased distance from 100 to 150
        .force("charge", d3.forceManyBody().strength(-500)) // Increased strength from -300 to -500
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("collide", d3.forceCollide().radius(d => d.group === 1 ? 50 : 40).strength(0.7)) // Increased radius
        .force("x", d3.forceX(width / 2).strength(0.05)) // Reduced strength from 0.1 to 0.05
        .force("y", d3.forceY(height / 2).strength(0.05)) // Reduced strength from 0.1 to 0.05
        .alphaDecay(0.01)
        .velocityDecay(0.3);

    const link = svg.append("g")
        .selectAll("line")
        .data(links)
        .join("line")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .attr("stroke-width", d => d.source.group === 1 && d.target.group === 1 ? 2 : 1);

    const node = svg.append("g")
        .selectAll("g")
        .data(nodes)
        .join("g")
        .call(drag(simulation));

    node.append("circle")
        .attr("r", d => d.group === 1 ? 30 : 20)
        .attr("fill", d => d.group === 1 ? "#ffd700" : "#add8e6");

    node.append("text")
        .text(d => d.id)
        .attr("x", 0)
        .attr("y", d => d.group === 1 ? 40 : 30)
        .attr("text-anchor", "middle");

    node.on("click", handleNodeClick);

    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("transform", d => `translate(${d.x},${d.y})`);
    });

    function drag(simulation) {
        function dragstarted(event) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        return d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);
    }

    function handleNodeClick(event, d) {
        const chatPanel = document.getElementById('chat-panel');
        chatPanel.classList.add('open');
        const chatOutput = document.getElementById('chat-output');
        chatOutput.innerHTML += '<p>topic selected: ' + d.id + '</p>';

        fetch('/api/node-click', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: d.id,
                mainTopic: urlParams.get('topic')
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                } else {
                    console.log('Node click processed successfully:', data);
                }
            })
            .catch(error => console.error('Error:', error));
    }

    window.addEventListener('resize', () => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        svg.attr("width", width).attr("height", height);
        simulation.force("center", d3.forceCenter(width / 2, height / 2));
        simulation.force("x", d3.forceX(width / 2).strength(0.1));
        simulation.force("y", d3.forceY(height / 2).strength(0.1));
        simulation.alpha(1).restart();
    });
}