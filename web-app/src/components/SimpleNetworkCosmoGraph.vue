<template>
  <canvas class="metakg-cosmo" :id="'sn' + badgeID" />
</template>

<script>
import { Cosmograph } from '@cosmograph/cosmograph';

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
      console.log('Cosmo');

      const nodes = [
        { id: '1', color: '#88C6FF' },
        { id: '2', color: '#FF99D2' },
        { id: '3', color: [227, 17, 108, 1] } // Faster than providing a hex value
      ];

      const links = [
        { source: '1', target: '2' },
        { source: '1', target: '3' },
        { source: '2', target: '3' }
      ];
      const canvas = document.createElement('canvas');
      document.body.appendChild(canvas);
      const config = {
        nodeColor: (d) => d.color,
        nodeSize: 20,
        linkWidth: 2
      };

      // Create a Cosmograph instance with the canvas element
      const cosmograph = new Cosmograph(canvas, config);

      // Set the data
      cosmograph.setData(nodes, links);
      console.log(cosmograph);
    }
  },
  mounted: function () {
    this.drawSigma();
  }
};
</script>

<style scoped>
.metakg-cosmo {
  width: 300px;
  height: 300px;
  border: solid yellow 2px;
}
</style>
