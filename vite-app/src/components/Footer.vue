<template>
  <footer id="contact" class="page-footer grey darken-4">
    <div class="container">
      <div class="row">
        <div class="footerLogos">
          <div>
            <a href="http://wulab.io/" rel="noreferrer" target="_blank">
              <img src="@/assets/img/wulab.png" width="100%" alt="WuLab" />
            </a>
          </div>
          <div>
            <a href="http://sulab.org/" rel="noreferrer" target="_blank">
              <img src="@/assets/img/sulab.png" width="100%" alt="WuLab" />
            </a>
          </div>
          <div>
            <a href="https://www.scripps.edu/" rel="noreferrer" target="_blank">
              <img src="@/assets/img/scripps.png" width="100%" alt="SR" />
            </a>
          </div>
          <div>
            <a
              href="https://www.maastrichtuniversity.nl/research/institute-data-science#"
              rel="noreferrer"
              target="_blank"
            >
              <img src="@/assets/img/mu-white.png" width="100%" alt="MU" />
            </a>
          </div>
          <div>
            <a href="https://ncats.nih.gov/translator" rel="noreferrer" target="_blank">
              <img src="@/assets/img/TranslatorLogo.jpg" width="100%" alt="Translator" />
            </a>
          </div>
          <div style="border-left: 2px solid #328cc4; padding-left: 10px">
            <h6>
              <small>Supported with funding from</small>
            </h6>
            <div>
              <a href="https://ncats.nih.gov/" rel="noreferrer" target="_blank">
                <img src="@/assets/img/ncats.png" width="100%" alt="ncats" />
              </a>
            </div>
          </div>
        </div>
        <div class="col s6 m4">
          <h5 class="blue-text logoFont">SmartAPI</h5>
          <ul>
            <li>
              <router-link to="/" class="footerLink">Home</router-link>
            </li>
            <li>
              <router-link to="/about" class="footerLink">About</router-link>
            </li>
            <li>
              <router-link to="/privacy" class="footerLink">Privacy</router-link>
            </li>
            <li>
              <router-link to="/documentation" class="footerLink">Documentation</router-link>
            </li>
            <li>
              <router-link to="/branding" class="footerLink">Branding</router-link>
            </li>
          </ul>
        </div>
        <div class="col s6 m4">
          <h5 class="white-text">API Management</h5>
          <ul>
            <li>
              <router-link to="/add-api" class="footerLink">Add an API</router-link>
            </li>
            <li>
              <router-link to="/registry" class="footerLink">Registry</router-link>
            </li>
            <li>
              <router-link to="/editor" class="footerLink">Editor</router-link>
            </li>
            <li>
              <router-link to="/guide" class="footerLink">Guide</router-link>
            </li>
            <li>
              <router-link to="/faq" class="footerLink">FAQ</router-link>
            </li>
          </ul>
        </div>
        <div class="col s6 m4">
          <h5 class="white-text">Connect</h5>
          <ul>
            <li>
              <a class="footerLink" target="_blank" href="https://github.com/smartapi">
                <i class="small fa fa-github-alt"></i> Github
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <div class="footer-copyright">
      <div class="container blue-grey-text">
        <hr />
        <p class="center-align">
          Copyright &copy; <span id="year"></span>.
          <a target="_blank" class="blue-grey-text" href="http://smart-api.info"
            >SmartAPI consortium</a
          >. All content available via
          <a target="_blank" rel="license" href="http://creativecommons.org/licenses/by/4.0/"
            >&nbsp;
            <img width="60" src="../assets/img/by.svg" alt="ccby" />
          </a>
        </p>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer',
  mounted: () => {
    var currentTime = new Date()
    var year = currentTime.getFullYear()
    var myelement = document.getElementById('year')
    myelement.innerHTML = year
  }
}
</script>

<style lang="css" scoped>
.footerLogos {
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  flex-wrap: wrap;
}
.footerLogos div {
  flex-basis: 15%;
  min-width: 125px;
  max-width: 125px;
}
</style>
