<template>
  <div class="metakg-cy" :id="'sn' + badgeID"></div>
</template>

<script>
import Graph from "graphology";
import Sigma from "sigma";
import {circlepack} from 'graphology-layout';

export default {
  name: 'SimpleNetwork',
  data: function () {
    return {
      badgeID: Math.floor(Math.random() * 90000) + 10000,
      cy: null
    };
  },
  props: ['nodes', 'edges'],
  computed: {
    color: function () {
      return this.$store.getters.getEntityColor(this.object);
    }
  },
  methods: {
    drawSigma(){

      const container = document.getElementById("sn" + this.badgeID);

      const graph = new Graph({
          "type": "directed",
          "multi": true,
          "allowSelfLoops": true,
          "zoomingRatio": 1
        });

      this.nodes.forEach(n => {
        graph.addNode(n.data.id, {size: n.data.weight/40 < 6 ? 6 : n.data.weight/40, label: n.data.id, color: n.data.color });
      })

      this.edges.forEach(e => {
        graph.addEdge(e.data.source, e.data.target, {size: 0.1, type: 'arrow'});
      })

      circlepack.assign(graph, {scale: 2});

      const settings = {
          minArrowSize: 100,
          defaultEdgeType: "curvedArrow",
          arrowSizeRatio: 10,
          defaultEdgeLabelColor: "#FFFFFF",
          defaultEdgeHoverColor: "default",
          edgeHoverColor: 'default',
          defaultEdgeColor: "#959595",
          defaultNodeColor: "#007FFF",
          defaultLabelColor: "white",
          edgeColor:'default',
          enableEdgeHovering: true,
          enableHovering: true,
          drawEdges: false,
      }

      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const renderer = new Sigma(graph, container, settings);
    }
  },
  mounted: function () {
    this.drawSigma();
  }
};
</script>
