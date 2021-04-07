<template>
  <main id="brand-app" class="white" style="width: 100%; padding-bottom:100px;">
    <MetaHead title="SmartAPI | Branding"></MetaHead>
  <div class="full-width brandBack"></div>
  <div class="container center-align">
    <h3 class="blue-grey-text">Branding</h3>
    <h5 class="blue-grey-text">- Guidelines -</h5>
    <p class="blue-grey-text" style="margin:10px 10%;">
      If you use any of the <span class="logoFont">SmartAPI</span> logos, illustrations or any other images approved for use under these brand guidelines, you agree that you will do so in compliance with the terms and conditions indicated on this page. If you do so, <span class="logoFont">SmartAPI</span> grants you a non-transferable, non-exclusive, royalty-free limited license to use its creative assets, and only in accordance with these brand guidelines. This is not a trademark license.
    </p>
    <p class="blue-grey-text" style="margin:10px 10%;">
      Please refer to these guidelines to achieve consistency and make sure the branded elements of <span class="logoFont">SmartAPI</span> are used correctly across every application. We reserve the right to terminate or modify your permission to display our creative assets.
    </p>
    <hr />
    <h5 class="blue-grey-text">Don't Do This</h5>
    <div class="swatchParent">
      <div class="dont blue-grey-text lighter">
        <i class="fa fa-ban red-text" aria-hidden="true"></i> Distort our images.
      </div>
      <div class="dont blue-grey-text lighter">
        <i class="fa fa-ban red-text" aria-hidden="true"></i> Change the original images in any way.
      </div>
      <div class="dont blue-grey-text lighter">
        <i class="fa fa-ban red-text" aria-hidden="true"></i> Apply filters to our images.
      </div>
      <div class="dont blue-grey-text lighter">
        <i class="fa fa-ban red-text" aria-hidden="true"></i> Overlay images or text over our images.
      </div>
      <div class="dont blue-grey-text lighter">
        <i class="fa fa-ban red-text" aria-hidden="true"></i> Crop our images in any way.
      </div>
      <div class="dont blue-grey-text lighter">
        <i class="fa fa-ban red-text" aria-hidden="true"></i> Don't rotate our images.
      </div>
      <div class="dont blue-grey-text lighter">
        <i class="fa fa-ban red-text" aria-hidden="true"></i> Recreate our images.
      </div>
      <div class="dont blue-grey-text lighter">
        <i class="fa fa-ban red-text" aria-hidden="true"></i> Use our images commercially use without permission.
      </div>
    </div>
    <hr />
    <h5 class="blue-grey-text">Colors</h5>
    <div class="swatchParent">
      <div class="swatch" style="background-color: #E4F2FC;" id="sa1" value="#E4F2FC">
        #E4F2FC
        <CopyButton copy="#E4F2FC" copy_msg="Color Copied!">
            <template v-slot:title>
                Copy Color
            </template>
        </CopyButton>
      </div>
      <div class="swatch" style="background-color: #B2E3F5;" id="sa2" value="#B2E3F5">
        #B2E3F5
        <CopyButton copy="#B2E3F5" copy_msg="Color Copied!">
            <template v-slot:title>
                Copy Color
            </template>
        </CopyButton>
      </div>
      <div class="swatch" style="background-color: #3F85BB;" id="sa3" value="#3F85BB">
        #3F85BB
        <CopyButton copy="#3F85BB" copy_msg="Color Copied!">
            <template v-slot:title>
                Copy Color
            </template>
        </CopyButton>
      </div>
      <div class="swatch" style="background-color: #273238; color: white;" id="sa4" value="#273238">
        #273238
        <CopyButton copy="#273238" copy_msg="Color Copied!">
            <template v-slot:title>
                Copy Color
            </template>
        </CopyButton>
      </div>
    </div>
    <hr />
    <h5 class="blue-grey-text">Brand Name & Font</h5>
    <p class="blue-grey-text">
      <span class="logoFont">SmartAPI</span> recommends the use of our font if used on a heading.<br /> The <b>first letter</b> and the word <b>API</b> in our logo must always be capitalized.
    </p>
    <p class="blue-grey-text">
       <span class="logoFont">SmartAPI</span> uses the font MonoGlyceride by <a href="http://www.tepidmonkey.net/" target="_blank">TepicMonkey.net</a>. <a class='link bold' href='https://www.1001freefonts.com/monoglyceride.font' target='_blank'>Download Here</a>
    </p>
    <hr />
    <div class="grey lighten-3">
      <h5 class="blue-grey-text">Logos</h5>
      <div class="swatchParent">
        <!-- <div class="downloadBox center-align">
          <Image img_width="100px" img_name="download.svg" alt="logo"></Image>
          <span class="blue-text smallFont">Full Package</span>&nbsp;
          <a class="smallButton" href="http://www.smart-api.info/img/logos.zip" download>
          <i class="fa fa-download" aria-hidden="true"></i>
          </a>
        </div> -->
        <div class="downloadBox center-align">
          <Image img_width="100px" img_name="logo-large-text.svg" alt="logo"></Image>
          <span class="blue-text smallFont">Logo (Vertical)</span>&nbsp;
          <a class="smallButton" :href="d2" download>
          <i class="fa fa-download" aria-hidden="true"></i>
          </a>
        </div>
        <div class="downloadBox center-align">
          <Image img_width="300px" img_name="header-logo.png" alt="logo"></Image>
          <span class="blue-text smallFont">Logo (Horizontal)</span>&nbsp;
          <a class="smallButton" :href="d3" download>
          <i class="fa fa-download" aria-hidden="true"></i>
          </a>
        </div>
      </div>
    </div>
    <hr />
    <p class="grey-text">
      Full package includes PNG and SVG versions of our logos with and without text!
    </p>
    <hr />
    <ul class="collection with-header">
        <li class="collection-header"><h4>Image Links</h4></li>
        <li class="collection-item grey lighten-3">
          <img style='border:0px;' width='200' src='../assets/img/header-logo.png' alt='logo 64'/>
            <div class="file-field input-field">
              <CopyButton copy_msg="Image Copied!" copy="<a href='http://www.smart-api.info/' alt='_blank'><img style='border:0px;' width='64' src='http://www.smart-api.info/img/header-logo.png' alt='SmartAPI'/></a>">
                  <template v-slot:title>
                      Copy Image <i class="fa fa-clipboard" aria-hidden="true"></i>
                  </template>
              </CopyButton>
              <div class="file-path-wrapper">
                <input type="text" id="link1" value="<a href='http://www.smart-api.info/' alt='_blank'><img style='border:0px;' width='64' src='http://www.smart-api.info/img/logo-small-64.png' alt='SmartAPI'/></a>">
              </div>
            </div>
        </li>
      </ul>
  </div>
</main>
</template>

<script>

export default {
    name: 'Branding',
    data: function(){
      return {
        d2: require("../assets/img/logo-large.svg"),
        d3: require("../assets/img/header-logo.png"),
      }
    }
}
</script>