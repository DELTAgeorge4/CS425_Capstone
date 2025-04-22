const data = {
    nodes: [
      { id: "Alice", group: 1 },
      { id: "Bob", group: 1 },
      { id: "Carol", group: 2 },
      { id: "Dave", group: 2 }
    ],
    links: [
      { source: "Alice", target: "Bob", value: 1 },
      { source: "Alice", target: "Carol", value: 2 },
      { source: "Bob", target: "Dave", value: 1 }
    ]
  };

fetch('/network-topology')
  .then(response => response.json())
  .then(data => {
    console.log(data);
    let nodes = data.nodes;
    let links = data.links;
    drawChart({links, nodes});
  }
  )
  .catch(error => {
    console.error('Error fetching data:', error);
  });
  function drawChart({ nodes, links }) {
    const width = 1200;
    const height = 600;
  
    const color = d3.scaleOrdinal()
      .domain(["router", "switche", "server", "endpoint"])
      .range(d3.schemeCategory10);
  
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links)
        .id(d => d.id)
        .distance(150))  // ⬅️ spacing between connected nodes
      .force("charge", d3.forceManyBody()
        .strength(-1000)) // ⬅️ how strongly nodes repel each other
      .force("center", d3.forceCenter(width / 4, height / 2))
      .on("tick", ticked);
  
    const svg = d3.select("#chart").append("svg")
      .attr("width", width)
      .attr("height", height)
      .call(
        d3.zoom()
          .scaleExtent([0.5, 5]) // min and max zoom levels
          .on("zoom", (event) => {
            container.attr("transform", event.transform);
          })
      );
  
    const container = svg.append("g"); // this <g> will hold all elements
  
    const link = container.append("g")
      .attr("stroke", "#aaa")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke-width", 1.5);
  
    const node = container.append("g")
      .attr("stroke", "#fff")
      .attr("stroke-width", 1.5)
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", 12) // ⬅️ radius of the nodes
      .attr("fill", d => color(d.node_type))
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));
  
    // Add labels (hostnames)
    const label = container.append("g")
      .selectAll("text")
      .data(nodes)
      .join("text")
      .text(d => d.hostname)
      .attr("font-size", 10)
      .attr("text-anchor", "middle")
      .attr("dy", "-0.9em")
      .style("user-select", "none")  // Prevent selection/copy
      .style("-webkit-user-select", "none") // Safari
      .style("-moz-user-select", "none")    // Firefox
      .style("-ms-user-select", "none")       // IE/Edge
      .style("pointer-events", "none");      // ⬅️ Disables pointer events on labels
  
    function ticked() {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);
  
      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
  
      label
        .attr("x", d => d.x)
        .attr("y", d => d.y);
    }
  
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
  }
m  

