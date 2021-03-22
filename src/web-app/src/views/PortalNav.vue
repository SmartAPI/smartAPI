<template>
  <div class="white">
      <div style="min-height: 90vh">
            <nav>
                <div class="nav-wrapper blue-grey">
                <ul>
                    <li><router-link to="/portal">Portals Home</router-link></li>
                </ul>
                </div>
            </nav>
            <router-view></router-view>
      </div>
  </div>
</template>

<script>

export default {
    name: 'PortalNav'
}
</script>