<template>
  <div class="grey lighten-3" style="min-height: 90vh">
    <MetaHead title="SmartAPI | Portals"></MetaHead>
    <div class="center-align">
      <img width="100" alt="SmartAPI" src="@/assets/img/api-welcome.svg" />
    </div>
    <h1 class="grey-text center-align m-0 p-1">SmartAPI Portals</h1>
    <div class="d-flex justify-content-center align-items-center container">
      <template v-for="portal in portals" :key="portal.title">
        <Card
          :title="portal.title"
          :description="portal.description"
          :link="portal.link"
          :image="portal.image"
        >
        </Card>
      </template>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import Card from '../components/Card.vue'

export default {
  name: 'PortalHome',
  components: {
    Card
  },
  computed: {
    ...mapGetters(['portals'])
  }
}
</script>
