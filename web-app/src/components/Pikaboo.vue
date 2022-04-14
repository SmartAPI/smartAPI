<template>
    <div class="card-image">
        <Image :img_name="image" img_width="100%"></Image>
        <Image class="pika" img_name="api-editor.svg" img_width="100%"></Image>
    </div>
</template>

<script>
export default {
    name:'Pikaboo',
    props:{
        image:{
            type: String,
            default: 'featured.jpg'
        },
    },
}
</script>

<style>
    .card {
        position: relative;
        overflow: hidden;
    }
    .card .pika {
        width: 50%;
        opacity: 0;
        position: absolute;
        right: -200px;
        transition: all 0.5s;
    }
    .card:hover .pika {
        opacity: 1;
        right: -60px;
    }
</style>