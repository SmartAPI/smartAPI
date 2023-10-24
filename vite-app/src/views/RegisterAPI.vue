<template>
  <main id="registerAPI" class="blue-grey darken-3 row m-0">
    <MetaHead title="SmartAPI | Register Your API"></MetaHead>
    <div
      v-if="loggedIn"
      class="section no-pad-bot single_section col l12 s12"
      style="margin-bottom: 10% !important; margin-top: 5%"
    >
      <div
        id="submitBox"
        class="container center-align white z-depth-5 light-blue lighten-4"
        style="border-radius: 10px"
      >
        <div class="cloudsBack padding20">
          <Owl></Owl>
          <h3 class="center blue-grey-text flow-text">Register your API metadata</h3>
        </div>
        <form @submit.prevent="handleSubmit()" class="white">
          <input
            placeholder="Enter the URL to your raw API Metadata here"
            class="browser-default margin20 validate register_input"
            style="
              width: 80%;
              outline: none;
              padding: 10px;
              border-radius: 20px;
              border: var(--blue-medium) 2px solid;
            "
            v-model="url"
            name="url"
            type="url"
          />
          <div class="padding20">
            <div>
              <input type="checkbox" id="test1" v-model="dry_run" />
              <label for="test1">Dry Run</label>
            </div>
            <label for="dry_run">Click for dry run only. API won't actually saved.</label>
          </div>
          <button
            :class="[ready ? '' : 'hide']"
            :disabled="!ready"
            class="btn waves-effect waves-light blue accent-2"
            id="submit"
            type="submit"
          >
            Submit
          </button>
          <p class="center blue-text">
            If you hosted your data on GitHub make sure to use the raw data link!
          </p>
          <img
            width="40%"
            class="hide-on-small-only"
            alt="copy the raw data link"
            src="@/assets/img/raw.gif"
          />
          <h4 class="blue-grey-text">Need Help?</h4>
          <p class="blue-grey-text center">
            Use our guide to help you through the process of adding an API.
            <br /><br />
            <router-link to="/guide" class="btn blue">GUIDE</router-link>
          </p>
          <div class="padding20 grey darken-3 white-text">
            Swagger V2 can be submitted, however it will not experience full functionality on
            SmartAPI and BioThings Explorer.
            <br />
            <a
              target="_blank"
              href="https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md"
              >Learn More about OpenAPI V3 Specification
              <i class="fa fa-external-link-square" aria-hidden="true"></i
            ></a>
            <br />
            <router-link to="/guide"
              ><i class="fa fa-info-circle" aria-hidden="true"></i> Upgrade your
              Metadata</router-link
            >
          </div>
        </form>
      </div>
    </div>
    <div
      v-if="!loggedIn"
      class="padding20 card-panel white d-flex justify-content-center align-items-center"
      style="min-height: 80vh"
    >
      <div class="center-align">
        <h5>
          <img width="250" alt="stop" src="@/assets/img/api-stop.svg" />
        </h5>
        <h5 class="text_h3 blue-grey-text-text">You Must Be Logged In To Register an API</h5>
        <a href="/oauth" class="btn green"> Login </a>
      </div>
    </div>
  </main>
</template>

<script>
import axios from 'axios';
import Owl from '../components/Owl3D.vue';
import { mapGetters } from 'vuex';
import dryrun_pic from '@/assets/img/api-dryrun.svg';
import success_pic from '@/assets/img/api-sucess.svg';
import overwrite_pic from '@/assets/img/api-overwrite.svg';
import fail_pic from '@/assets/img/api-fail.svg';

export default {
  name: 'RegisterAPI',
  data: function () {
    return {
      url: '',
      dry_run: false,
      suggestedURL: ''
    };
  },
  components: {
    Owl
  },
  computed: {
    ready: function () {
      return this.url ? true : false;
    },
    ...mapGetters(['loggedIn'])
  },
  watch: {
    url: function (value) {
      if (value.includes('blob') || value.includes('github.com')) {
        this.suggestedURL = value
          .replace('blob/', '')
          .replace('github.com', 'raw.githubusercontent.com')
          .replace('www.github.com', 'raw.githubusercontent.com');

        this.$swal({
          title: 'Link Converted',
          animation: false,
          html:
            '<p>We noticed that was not a raw data link. We have converted it to: </p> ' +
            '<p><a target="_blank" href="' +
            this.suggestedURL +
            '">' +
            this.suggestedURL +
            '</a></p>' +
            '<p>Proceed with this link?</p>',
          showCancelButton: true,
          confirmButtonText: 'Yes, use this link!'
        }).then((result) => {
          if (result.value) {
            this.url = this.suggestedURL;
            this.$toast.success('Link Updated!');
            this.$swal.close();
          }
        });
      }
    }
  },
  methods: {
    handleSubmit: function () {
      let self = this;
      if (self.ready) {
        let data = {
          url: self.url
        };
        if (self.dry_run) {
          data['dryrun'] = true;
        }
        let url = this.$apiUrl + '/metadata';
        axios
          .post(url, data)
          .then((res) => {
            console.log('registering', res.data);
            if (res.data.success) {
              if (
                Object.prototype.hasOwnProperty.call(res.data, 'details') &&
                res.data.details.includes('[Dryrun]')
              ) {
                this.$swal({
                  imageUrl: dryrun_pic,
                  imageWidth: 300,
                  imageAlt: 'Dry Run',
                  title: res.data.details,
                  html: "Because this is a dry run your data has <b>not</b> been saved. If you want to register your API, uncheck 'dry run' and try again."
                });
              } else if (Object.prototype.hasOwnProperty.call(res.data, '_id')) {
                this.$swal({
                  imageUrl: success_pic,
                  imageWidth: 300,
                  title: 'Great! You are done!',
                  html:
                    "You can view your API documentation <b><a href='/registry?q=" +
                    res.data._id +
                    "'>HERE</a></b>"
                });
              }
            }
          })
          .catch((err) => {
            if (
              Object.prototype.hasOwnProperty.call(err, 'response') &&
              Object.prototype.hasOwnProperty.call(err.response, 'data')
            ) {
              console.log('[Error]:', err.response);
              if (
                Object.prototype.hasOwnProperty.call(err.response.data, 'error') &&
                err.response.data.error == 'Conflict'
              ) {
                this.$swal({
                  title: 'Wait a second...',
                  html: '<h3>Looks like this API already exists</h3><p>If you are the owner of this API you can refresh it via the <a href="/dashboard">user dashboard</a></p>',
                  imageUrl: overwrite_pic,
                  imageWidth: 300,
                  confirmButtonText: 'OK'
                });
              } else if (
                Object.prototype.hasOwnProperty.call(err.response.data, 'details') &&
                err.response.data.details == 'API exists'
              ) {
                this.$swal({
                  title: 'Wait a second...',
                  html: '<h3>Looks like this API already exists</h3><p>If you are the owner of this API you can refresh it via the <a href="/dashboard">user dashboard</a></p>',
                  imageUrl: fail_pic,
                  imageWidth: 300,
                  confirmButtonText: 'OK'
                });
              } else if (
                Object.prototype.hasOwnProperty.call(err.response.data, 'details') &&
                err.response.data.details.includes('Validation Error')
              ) {
                this.$swal({
                  title: "Oh no, there's a problem!",
                  imageUrl: fail_pic,
                  imageWidth: 300,
                  confirmButtonText: 'OK',
                  html:
                    `<h5>Here's what we found:</h5>
                        <div class="padding20 orange lighten-5 codeBox"><code>` +
                      err.response.data.details || err.response.data + `</code></div>`,
                  footer: `<p><b class="red-text">Need help?</b> Take a look at OpenAPI specification examples <a href="https://github.com/NCATSTranslator/translator_extensions" target="_blank" rel="nonreferrer">here</a>.</p>`
                });
              } else {
                this.$swal({
                  title: "Oops, there's an issue!",
                  imageUrl: fail_pic,
                  imageWidth: 300,
                  confirmButtonText: 'OK',
                  html:
                    `<h5>Here's what we found:</h5>
                        <div class="padding20 orange lighten-5 codeBox"><code>` +
                    err.response.data.error +
                    `</code></div>`,
                  footer: `<p><b class="red-text">Need help?</b> Learn more about and look at examples of SmartAPI extensions <a href="https://github.com/NCATSTranslator/translator_extensions" target="_blank" rel="nonreferrer">here</a>.</p>`
                });
              }
            }
          });
      }
    }
  }
};
</script>
