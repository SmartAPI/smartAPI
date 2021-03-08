<template>
    <footer id="contact" class="page-footer grey darken-4">
        <div class="container">
            <div class="row">
                <div class="footerLogos">
                    <div>
                        <a href="http://wulab.io/" rel="noreferrer" target="_blank">
                            <Image img_width="100%" img_name='wulab.png' alt="wulab"></Image>
                        </a>
                    </div>
                    <div >
                        <a href="http://sulab.org/" rel="noreferrer" target="_blank">
                            <Image img_width="100%" img_name='sulab.png' alt="sulab"></Image>
                        </a>
                    </div>
                    <div >
                        <a href="https://www.scripps.edu/" rel="noreferrer" target="_blank">
                            <Image img_width="100%" img_name='scripps.png' alt="scripps"></Image>
                        </a>
                    </div>
                    <div >
                        <a href="https://www.maastrichtuniversity.nl/research/institute-data-science#" rel="noreferrer" target="_blank">
                            <Image img_width="100%" img_name='mu-white.png' alt="mu"></Image>
                        </a>
                    </div>
                    <div>
                        <a href="https://ncats.nih.gov/translator" rel="noreferrer" target="_blank">
                            <Image img_width="100%" img_name='TranslatorLogo.jpg' alt="translator"></Image>
                        </a>
                    </div>
                    <div style="border-left: 2px solid #328cc4; padding-left: 10px;">
                        <h6>
                            <small>Supported with funding from</small>
                        </h6>
                        <div>
                            <a href="https://ncats.nih.gov/" rel="noreferrer" target="_blank">
                                <Image img_width="100%" img_name='ncats.png' alt="ncats"></Image>
                            </a>
                        </div>
                    </div>
                </div>
                <div class="col s6 m4">
                    <h5 class="blue-text logoFont">SmartAPI Info</h5>
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
                            <a class="footerLink" href="/documentation"><i class="material-icons">subdirectory_arrow_right</i> Documentation</a>
                        </li>
                        <li>
                            <router-link to="/branding" class="footerLink">Branding</router-link>
                        </li>
                    </ul>
                </div>
                <div class="col s6 m4">
                    <h5 class="white-text">SmartAPI Info</h5>
                    <ul>
                        <li>
                            <router-link to="/add-api" class="footerLink">Add an API</router-link>
                        </li>
                        <li>
                            <a class="footerLink" href="/registry"><i class="material-icons">subdirectory_arrow_right</i> Registry</a>
                        </li>
                        <li>
                            <router-link to="/editor" class="footerLink">Editor</router-link>
                        </li>
                        <li>
                            <a class="footerLink" href="/guide"><i class="material-icons">subdirectory_arrow_right</i> Guide</a>
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
                <hr>
                <p>Copyright &copy; <span id="year"></span>.
                    <a target="_blank" class="blue-grey-text" href="http://smart-api.info">SmartAPI consortium</a>.
                    All content available via <a target="_blank" rel="license" href="http://creativecommons.org/licenses/by/4.0/">
                    <i class="fa fa-creative-commons blue-grey-text" aria-hidden="true"></i>
                    </a>
                </p>

                <div>
                    All content available via
                    <a rel="license" href="https://creativecommons.org/licenses/by/4.0/" title="Creative Commons Attribution 4.0 International license">
                    CC License
                    </a>.
                </div>
            </div>
        </div>
    </footer>
</template>

<script>
import Image from './Image.vue';
export default {
  components: { Image },
  name: 'Footer',
  mounted: ()=>{
    var currentTime = new Date()
    var year = currentTime.getFullYear()
    var myelement = document.getElementById("year");
    myelement.innerHTML= year;
  }
}
</script>

<style lang="css" scoped>
.footerLogos{
    display: flex;
    justify-content: space-evenly;
    align-items: center;
    flex-wrap: wrap;
}
.footerLogos div{
    flex-basis: 15%;
    min-width: 125px;
    max-width: 125px;
}
</style>
