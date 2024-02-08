<template>
  <div class="metakg-cy" :id="'sn' + badgeID"></div>
</template>

<script>
import cytoscape from 'cytoscape';
import tippy from 'tippy.js';

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
      let self = this;
      this.cy = cytoscape({
        container: document.getElementById('sn' + this.badgeID),
        elements: [...this.edges, ...this.nodes],
        hideEdgesOnViewport: true,
        style: [
          {
            selector: 'node',
            style: {
              content: 'data(name)',
              'text-wrap': 'wrap',
              'text-valign': 'center',
              'text-halign': 'center',
              'font-size': '2em',
              color: 'white',
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

      function readableName(text) {
        const result = text.replace(/([A-Z])/g, '\n $1');
        return result.charAt(0).toUpperCase() + result.slice(1);
      }

      function makePopper(ele) {
        let ref = ele.popperRef();
        ele.tippy = tippy(document.createElement('div'), {
          getReferenceClientRect: ref.getBoundingClientRect,
          placement: 'top',
          trigger: 'mouseenter', // mandatory
          arrow: true,
          interactive: true,
          allowHTML: true,
          theme: 'light',
          appendTo: document.body, // or append dummyDomEle to document.body
          onShow: function (instance) {
            instance.setContent(
              '<div class="white-text" style="padding:3px 5px;background:' +
                ele.data('color') +
                '">' +
                readableName(ele.id()) +
                '</div>'
            );
          },
          onUntrigger: function (instance) {
            instance.show();
          }
        });
      }

      this.cy.ready(function () {
        self.cy.elements().forEach(function (ele) {
          if (ele.isNode()) {
            makePopper(ele);
          }
        });
      });

      this.cy.userZoomingEnabled(false);

      this.cy.elements().unbind('mouseover');
      this.cy.elements().bind('mouseover', (event) => event.target?.tippy?.show());

      this.cy.elements().unbind('mouseout');
      this.cy.elements().bind('mouseout', (event) => event.target?.tippy?.hide());

      this.cy
        .layout({
          name: 'concentric',
          avoidOverlap: true,
          avoidOverlapPadding: 200,
          minNodeSpacing: 100
        })
        .run();
    }
  },
  mounted: function () {
    this.draw();
  }
};
</script>
