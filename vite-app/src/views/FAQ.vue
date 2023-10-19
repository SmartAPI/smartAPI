<template>
  <main id="faq-app" class="white w-100 padding20">
    <MetaHead title="SmartAPI | FAQ"></MetaHead>
    <div class="container-fluid center">
      <div class="white blue-text">
        <img
          alt="faq"
          src="@/assets/img/faq.svg"
          width="200"
          class="responsive-img"
          style="max-width: 300px"
        />
        <h1 class="bold">FAQ</h1>
      </div>
    </div>
    <div class="container center" style="margin-bottom: 10vh">
      <template v-for="section in faq" :key="section.sectionName">
        <h4 class="grey-text" v-text="section.sectionName"></h4>
        <ul class="collapsible">
          <template v-for="item in section.questions" :key="item.anchor">
            <li :id="item.anchor">
              <div class="collapsible-header blue-text bold">
                <i class="fa fa-comment" aria-hidden="true"></i>
                <a :href="'#' + item.anchor" v-text="item.question"></a>&nbsp;
              </div>
              <div
                class="collapsible-body blue-grey-text flow-text left-align"
                style="padding-top: 3px"
              >
                <div class="right-align">
                  <CopyButton
                    copy_msg="URL copied"
                    :copy="'http://smart-api.info/faq#' + item.anchor"
                  >
                    <template v-slot:title> Copy FAQ Link </template>
                  </CopyButton>
                </div>
                <div v-html="item.answer"></div>
              </div>
            </li>
          </template>
        </ul>
      </template>
    </div>
  </main>
</template>

<script>
import { mapGetters } from 'vuex'
import { Collapsible } from 'materialize-css'

export default {
  name: 'FAQ',
  methods: {
    readURL() {
      let hash = window.location.hash
      if (hash) {
        document.querySelector('.collapsible-header').classList.remove('active')
        document.querySelector(hash).classList.add('active')
        document.querySelector(hash).scrollIntoView()
      }
    },
    notify() {
      this.$toast.success(`Link Copied`)
    }
  },
  mounted: function () {
    this.readURL()
    var elems = document.querySelectorAll('.collapsible')
    Collapsible.init(elems)
  },
  computed: {
    location: () => {
      return window.location
    },
    ...mapGetters(['faq'])
  }
}
</script>

<style scoped>
code {
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
  font-size: 85%;
  margin: 0;
  padding: 0.2em 0.4em;
}
</style>
