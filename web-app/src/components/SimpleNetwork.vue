<template>
  <div class="metakg-cy" :id="'sn' + badgeID"></div>
</template>

<script>
import cytoscape from 'cytoscape';

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
    draw() {
      this.cy = cytoscape({
        container: document.getElementById('sn' + this.badgeID),
        elements: [...this.edges, ...this.nodes],
        hideEdgesOnViewport: true,
        style: [
          {
            selector: 'node',
            style: {
              'background-color': 'data(color)',
              'z-index': 1000,
              width: 'data(weight)',
              height: 'data(weight)'
            }
          },
          {
            selector: 'edge',
            style: {
              'curve-style': 'bezier',
              'haystack-radius': 0,
              'target-arrow-shape': 'triangle',
              'target-arrow-color': 'limegreen',
              'z-index': 1
            }
          }
        ]
      });
      this.cy
        .layout({
          name: 'concentric',
          avoidOverlap: true,
          avoidOverlapPadding: 200,
          minNodeSpacing: 100
        })
        .run();

      this.cy.userZoomingEnabled(false);
    }
  },
  mounted: function () {
    this.draw();
  }
};
</script>
