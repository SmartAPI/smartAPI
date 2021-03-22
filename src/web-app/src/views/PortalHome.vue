<template>
  <div>
      <h1 class="grey-text center-align">SmartAPI Portals</h1>
      <div class="d-flex justify-content-center align-items-center container">
        <template v-for="portal in portals" :key="portal.title">
            <Card 
            :title="portal.title"
            :description="portal.description"
            :link="portal.link"
            :image="portal.image">
            </Card>
        </template>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import Card from '../components/Card.vue';

export default {
    name: 'PortalHome',
    components:{
        Card
    },
    computed:{
        ...mapGetters([
            'portals',
        ])
    },
}
</script>