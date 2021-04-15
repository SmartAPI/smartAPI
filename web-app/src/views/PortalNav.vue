<template>
  <div class="grey lighten-3">
      <MetaHead
        :title="selected ? 'SmartAPI | '+selected.toUpperCase() : 'SmartAPI | Portals'"
        ></MetaHead>
      <div style="min-height: 90vh">
            <div class="col s12 padding20 navbar-fixed">
                <router-link  class="blue-text" to="/portal">Portals</router-link>
                <router-link v-if="selected" :to="'/portal/'+selected" class="blue-text"> &gt; {{selected}}</router-link>
            </div>
            <router-view></router-view>
      </div>
  </div>
</template>

<script>

export default {
    name: 'PortalNav',
    computed:{
        selected:function(){
            return this.$route.params.name
        }
    }
}
</script>

<style lang="css">
    .caps{
        text-transform: uppercase;
    }
    .breadcrumb:before{
        color: grey;
    }
</style>