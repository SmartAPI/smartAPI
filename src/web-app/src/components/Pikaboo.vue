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

<style lang="scss">

    .card{
        position: relative;
        overflow: hidden;
        .pika{
            width: 50%;
            opacity: 0;
            position: absolute;
            right: -200px;
            transition: all .5s;
        }
        &:hover{
           .pika{
            opacity: 1;
            right: -60px;
        } 
        }
    }
</style>