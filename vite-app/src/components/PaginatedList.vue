<template>
  <div class="row m-0">
    <div class="col-sm-12">
      <div class="white padding20 resBox collection">
        <template v-if="type == 'MetaKG'">
          <template
            v-for="(item, index) in arrayResults"
            :key="item.association.smartapi.id + index"
          >
            <MetaKGResult :item="item"></MetaKGResult>
          </template>
        </template>
      </div>
      <div>
        <select class="browser-default" v-model="perPage" @change="calculatePages" id="perPage">
          <option value="" disabled selected>Shown Per Page</option>
          <option value="10">10 per page</option>
          <option value="25">25 per page</option>
          <option value="100">100 per page</option>
        </select>
        <ul class="pagination">
          <li :class="{ disabled: page <= 1 }">
            <a @click.prevent="prevPage()"> <i class="material-icons">chevron_left</i></a>
          </li>
          <template v-if="groupPages">
            <li v-show="!startCapLimitReached">
              <a class="page-link p-1" @click.prevent="previousGroup()">Previous 20</a>
            </li>
          </template>
          <template v-for="n in pages" :key="n">
            <li
              v-if="n >= startCap && n <= endCap"
              :class="{ active: page == n, blue: page == n, 'white-text': page == n }"
            >
              <a
                href="javascript:void(0)"
                class="page-link p-1"
                @click.prevent="page = n"
                v-text="n"
              ></a>
            </li>
          </template>
          <template v-if="groupPages">
            <li v-show="!endCapLimitReached">
              <a class="page-link p-1" @click.prevent="nextGroup()">next 20</a>
            </li>
          </template>
          <li :class="{ disabled: page >= pages }">
            <a @click.prevent="nextPage()"> <i class="material-icons">chevron_right</i></a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import MetaKGResult from './MetaKGResult.vue'

export default {
  name: 'PaginatedList',
  components: {
    MetaKGResult
  },
  data: function () {
    return {
      expandArray: false,
      perPage: 10,
      page: 1,
      pages: 1,
      startCap: 0,
      endCap: 20,
      groupPages: false,
      pageLimit: 20,
      startCapLimitReached: true,
      endCapLimitReached: false
    }
  },
  props: {
    content: {
      type: Array,
      required: true
    },
    type: {
      type: String,
      required: true
    }
  },
  methods: {
    calculatePages: function () {
      var self = this
      self.pages = Math.ceil(self.content.length / self.perPage)

      if (self.pages > self.pageLimit) {
        self.groupPages = true
      }
    },
    previousGroup: function () {
      var self = this

      if (!self.startCapLimitReached) {
        if (self.startCap - 20 > 0) {
          self.page = self.startCap - 20
          self.startCap = self.startCap - 20
          self.endCap = self.endCap - 20
          self.endCapLimitReached = false
        } else {
          self.page = 1
          self.startCap = 0
          self.endCap = 20
          self.startCapLimitReached = true
          self.endCapLimitReached = false
        }
      }
    },
    nextGroup: function () {
      var self = this

      if (!self.endCapLimitReached) {
        if (self.endCap + 20 < self.pages) {
          self.page = self.startCap + 20
          self.startCap = self.startCap + 20
          self.endCap = self.endCap + 20
          self.startCapLimitReached = false
        } else {
          self.page = self.startCap + 20
          self.startCap = self.startCap + 20
          self.endCap = self.pages
          self.endCapLimitReached = true
          self.startCapLimitReached = false
        }
      }
    },
    prevPage: function () {
      var self = this
      if (self.page > 1) self.page -= 1
    },
    nextPage: function () {
      var self = this
      if (self.page < self.pages) self.page += 1
    }
  },
  computed: {
    arrayResults: function () {
      var start = (this.page - 1) * this.perPage,
        end = start + this.perPage
      return this.content && this.content.slice(start, end)
    }
  },
  mounted: function () {
    this.calculatePages()
  },
  watch: {
    content: {
      handler() {
        this.calculatePages()
      },
      deep: true
    }
  }
}
</script>

<style></style>
