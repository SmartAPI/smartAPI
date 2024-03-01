<template>
  <div>
    <div :id="'cosmo' + badgeID" class="cosmo"></div>
    <div class="switch m-1">
      <label>
        <b :class="{ 'cyan-text': !curvedLinks }">Straight</b>
        <input type="checkbox" v-model="curvedLinks" />
        <span class="lever"></span>
        <b :class="{ 'cyan-text': curvedLinks }">Curved</b>
      </label>
    </div>
  </div>
</template>

<script>
import { Cosmograph } from '@cosmograph/cosmograph';

export default {
  name: 'SimpleNetwork',
  data: function () {
    return {
      badgeID: Math.floor(Math.random() * 90000) + 10000,
      curvedLinks: false,
      cosmograph: null
    };
  },
  props: ['nodes', 'edges'],
  computed: {
    color: function () {
      return this.$store.getters.getEntityColor(this.object);
    }
  },
  watch: {
    curvedLinks: function () {
      if (this.cosmograph) {
        this.cosmograph.remove();
        this.drawCosmo();
      } else {
        this.drawCosmo();
      }
    }
  },
  methods: {
    drawCosmo() {
      const canvas = document.getElementById('cosmo' + this.badgeID);
      const config = {
        nodeColor: (n) => n.color,
        nodeSize: (n, i) => (n.weight / 50 < 10 ? 10 : n.weight / 50),
        linkWidth: 2,
        onClick: (n) => {
          if (this.cosmograph && n?.id) {
            this.cosmograph.selectNode({ id: n.id }, true);
          } else {
            this.cosmograph?.unselectNodes();
          }
        },
        fitViewOnInit: false,
        curvedLinks: this.curvedLinks,
        initialZoomLevel: 6,
        disableSimulation: true,
        hoveredNodeLabelColor: 'white',
        showDynamicLabels: false,
        scaleNodesOnZoom: false,
        linkArrows: true,
        linkWidth: this.nodes.length < 20 ? 2 : 0.5,
        linkArrowsSizeScale: this.nodes.length < 20 ? 2 : 1,
        linkVisibilityDistance: [400, 1000]
      };

      // Create a Cosmograph instance with the canvas element
      this.cosmograph = new Cosmograph(canvas, config);

      // Set the data
      this.cosmograph.setData(this.nodes, this.edges);
    }
  },
  mounted: function () {
    this.drawCosmo();
  }
};
</script>

<style scoped>
.cosmo {
  width: 300px;
  height: 300px;
  border: solid rgb(42, 42, 42) 2px;
}
</style>
