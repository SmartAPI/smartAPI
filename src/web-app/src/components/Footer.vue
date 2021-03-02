<template>
    <footer id="contact" class="page-footer grey darken-4">
        <div class="container">
            <div class="row">
                <div class="col s12 m6 l6">
                    <h5 class="white-text">SmartAPI Info</h5>
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
                            <router-link to="/add-api" class="footerLink">Add an API</router-link>
                        </li>
                        <li>
                            <a class="footerLink" href="/registry"><i class="material-icons">subdirectory_arrow_right</i> Registry</a>
                        </li>
                        <li>
                            <router-link to="/editor" class="footerLink">Editor</router-link>
                        </li>
                        <li>
                            <a class="footerLink" href="/documentation"><i class="material-icons">subdirectory_arrow_right</i> Documentation</a>
                        </li>
                        <li>
                            <a class="footerLink" href="/guide"><i class="material-icons">subdirectory_arrow_right</i> Guide</a>
                        </li>
                        <li>
                            <router-link to="/faq" class="footerLink">FAQ</router-link>
                        </li>
                        <li>
                            <router-link to="/branding" class="footerLink">Branding</router-link>
                        </li>
                    </ul>
                </div>
                <div class="col s12 m6 l6">
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
export default {
  name: 'Footer',
  mounted: ()=>{
    var currentTime = new Date()
    var year = currentTime.getFullYear()
    var myelement = document.getElementById("year");
    myelement.innerHTML= year;
  }
}
</script>
