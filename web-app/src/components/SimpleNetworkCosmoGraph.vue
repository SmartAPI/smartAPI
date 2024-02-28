<template>
  <div :id="'cosmo' + badgeID" class="cosmo">

  </div>
</template>

<script>
import { Cosmograph } from '@cosmograph/cosmograph'

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
      let cosmograph = null;
      const canvas = document.getElementById('cosmo' + this.badgeID)
      const config = {
        nodeColor: n => n.color,
        nodeSize: (n, i) => n.weight/50 < 10 ? 10 : n.weight/50,
        linkWidth: 2,
        onClick: (n) =>{
          if (cosmograph && n?.id) {
            cosmograph.selectNode({id: n.id}, true)
          }else{
            cosmograph?.unselectNodes();
          }
        },
        curvedLinks: true,
        initialZoomLevel: 3,
        disableSimulation: true,
        hoveredNodeLabelColor: 'white',
        showDynamicLabels: false,
        scaleNodesOnZoom: false,
        linkWidth: .5,
        linkArrowsSizeScale: 1,
        linkVisibilityDistance: [400, 1000]

      }

        // Create a Cosmograph instance with the canvas element
        cosmograph = new Cosmograph(canvas, config)

        // Set the data
        cosmograph.setData(this.nodes, this.edges)
    }
  },
  mounted: function () {
    this.drawSigma();
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
