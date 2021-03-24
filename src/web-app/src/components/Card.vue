<template>
    <div class="card portal-card hoverable" :style="{width: width, margin:'10px'}">
        <Pikaboo :image="image"></Pikaboo>
        <div class="card-content blue-grey-text">
        <span class="card-title">{{title}}</span>
        <p v-html="description"></p>
        </div>
        <div class="card-action grey lighten-2">
            <router-link class="btn blue" :to="link">Continue</router-link>
        </div>
    </div>
</template>

<script>
import Pikaboo from './Pikaboo.vue';

export default {
    name: 'Card',
    components:{
        Pikaboo
    },
    props:{
        width:{
            type: String,
            default: '45%'
        },
        image:{
            type: String,
            default: ''
        },
        link:{
            type: String,
            default: ''
        },
        title:{
            type: String,
            default: ''
        },
        description:{
            type: String,
            default: ''
        },
    },
}
</script>