<template>
    <main id="faq-app" class="white w-100 padding20">
    <div class="container-fluid center">
        <div class="white faqHero blue-text">
        <Image alt="faq" img_name="faq.svg" img_width='40%' class="responsive-img" style="max-width:300px;"></Image>
        <h1 class="bold">FAQ</h1>
        </div>
    </div>
    <div class="container center" style="margin-bottom:10vh;">
        <template v-for="section in faq" :key='section.sectionName'>
        <h4 class="grey-text" v-text='section.sectionName'></h4>
        <ul class="collapsible">
            <template v-for="item in section.questions" :key="item.anchor">
            <li :id="item.anchor">
                <div class="collapsible-header blue-text bold" :value="location+item.anchor">
                <i class="fa fa-comment" aria-hidden="true"></i> <span v-text="item.question"></span> <a :href="'#'+item.anchor" class="secondary-content"><i class="material-icons small">link</i></a>
                </div>
                <div class="collapsible-body blue-grey-text flow-text left-align" v-html="item.answer"></div>
            </li>
            </template>
        </ul>
        </template>
    </div>
    </main>
</template>

<script>
import { mapGetters } from 'vuex'
import {Collapsible} from 'materialize-css'

export default {
    name: 'FAQ',
    methods: {
        readURL(){
            let hash = window.location.hash;
            if (hash) {
                document.querySelector('.collapsible-header').classList.remove('active');
                document.querySelector(hash).classList.add('active');
                document.querySelector(hash).scrollIntoView();
            }
        }
    },
    mounted: function(){
        this.readURL();
        var elems = document.querySelectorAll('.collapsible');
        Collapsible.init(elems);
    },
    computed:{
        location: ()=>{
            return window.location
        },
        ...mapGetters([
            'faq',
        ])
    }
}
</script>

<style lang="scss" scoped>
    .faqHero{
        margin: 20px;
        padding: 20px;
        background-image: url('../assets/img/question.jpg');
        background-size: cover;
    }
    code {
        background-color: rgba(27,31,35,.05);
        border-radius: 3px;
        font-size: 85%;
        margin: 0;
        padding: .2em .4em;
    }
</style>