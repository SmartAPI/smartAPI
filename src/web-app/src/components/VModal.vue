<template>
<teleport to="#modals-go-here">
    <vue-final-modal
        v-bind="$attrs"
        classes="modal-container"
        content-class="modal-content"
    >
        <h6 class="modal__title center ligther grey-text">
            <slot name="title">
                <!-- TITLE -->
            </slot>
        </h6>
        <div class="modal__content">
            <slot>
                <!-- CONTENT GOES HERE -->
            </slot>
        </div>
        <div class="modal__action">
            <button class="btn green btn-small" @click="$emit('confirm')">OK</button>
        </div>
    </vue-final-modal>
</teleport>
</template>

<script>
export default {
  name: 'VModal',
  inheritAttrs: false
}
</script>

<style scoped>
::v-deep .modal-container {
  display: flex;
  justify-content: center;
  align-items: center;
}
::v-deep .modal-content {
  position: relative;
  display: flex;
  flex-direction: column;
  max-height: 90%;
  margin: 0 1rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.25rem;
  background: #fff;
}
.modal__title {
  margin: 0 2rem 0 0;
  font-size: 1.5rem;
  font-weight: 700;
}
.modal__content {
  flex-grow: 1;
  overflow-y: auto;
}
.modal__action {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
  padding: 1rem 0 0;
}
.modal__close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}
.dark-mode div::v-deep .modal-content {
  border-color: #2d3748;
  background-color: #1a202c;
}
</style>