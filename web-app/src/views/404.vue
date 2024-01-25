<template>
    <div class="d-flex justify-content-center align-items-center black white-text" style="min-height:90vh;">
        <div class="center-align">
            <h2>
            <Image img_name="lost.jpg" img_width="300px"></Image>
            </h2>
            <h1>Oh no! You're lost!</h1>
            <h6>This page doesn't exist.</h6>
            <p>
                <router-link to="/">Go Back Home</router-link>
            </p>
        </div>
    </div>
</template>

<script>
export default {
    name: '404',
}
</script>