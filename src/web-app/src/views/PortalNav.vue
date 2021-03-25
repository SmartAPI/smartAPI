<template>
  <div class="white">
      <MetaHead
        :title="selected ? 'SmartAPI | '+selected.toUpperCase() : 'SmartAPI | Portals'"
        ></MetaHead>
      <div style="min-height: 90vh">
            <nav>
                <div class="nav-wrapper purple white-text">
                <ul>
                    <li><router-link to="/portal">Portals Home</router-link></li>
                </ul>
                <router-link v-if="selected" :to="'/portal/'+selected" class="brand-logo center caps tracking-in-expand">{{selected}}</router-link>
                </div>
            </nav>
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
</style>