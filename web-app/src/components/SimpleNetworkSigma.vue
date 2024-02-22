<template>
  <div class="metakg-cy" :id="'sn' + badgeID"></div>
</template>

<script>
import Graph from 'graphology';
import Sigma from 'sigma';
import { circlepack } from 'graphology-layout';

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
    drawSigma() {
      const container = document.getElementById('sn' + this.badgeID);

      const graph = new Graph({
        type: 'directed',
        multi: true,
        allowSelfLoops: true
      });

      this.nodes.forEach((n) => {
        graph.addNode(n.data.id, {
          size: n.data.weight / 40 < 6 ? 6 : n.data.weight / 40,
          label: n.data.id,
          color: n.data.color
        });
      });

      this.edges.forEach((e) => {
        graph.addEdge(e.data.source, e.data.target, {
          size: 0.1,
          label: `${e.data.source} > ${e.data.target}`
        });
      });

      circlepack.assign(graph, { scale: 2 });

      const settings = {
        minArrowSize: 20,
        defaultEdgeType: 'arrow',
        arrowSizeRatio: 10,
        defaultEdgeLabelColor: '#FFFFFF',
        defaultEdgeHoverColor: 'yellow',
        edgeHoverColor: 'default',
        defaultEdgeColor: '#616161',
        defaultNodeColor: '#007FFF',
        defaultLabelColor: '#FFFFFF',
        edgeLabelSize: 'proportional',
        defaultEdgeLabelSize: 20,
        minEdgeSize: 0.1,
        maxEdgeSize: 1,
        edgeColor: 'default',
        doubleClickEnabled: false,
        enableEdgeHovering: true,
        enableHovering: false,
        drawEdges: true
      };

      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const renderer = new Sigma(graph, container, settings);

      // renderer.on("enterEdge", ({ edge }) => {
      //   console.log('edge', edge)
      //   renderer.refresh();
      // });
    }
  },
  mounted: function () {
    this.drawSigma();
  }
};
</script>
