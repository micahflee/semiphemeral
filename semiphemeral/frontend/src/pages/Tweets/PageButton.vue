<script setup>
const props = defineProps({
  pageNumber: String,
  isCurrent: Boolean
})
</script>

<template>
  <span>
    <template v-if="isCurrent">
      <span class="button current">{{ pageNumber }}</span>
    </template>
    <template v-else-if="pageNumber == 'previous'">
      <span class="button" v-on:click="$emit('select-page')">Previous</span>
    </template>
    <template v-else-if="pageNumber == 'next'">
      <span class="button" v-on:click="$emit('select-page')">Next</span>
    </template>
    <template v-else>
      <span class="button" v-on:click="$emit('select-page')">{{ pageNumber }}</span>
    </template>
  </span>
</template>

<style scoped>
.button {
  padding: 3px 6px;
  margin: 0 5px 0 0;
  font-size: 0.8em;
  border: 1px solid #999999;
  color: #034b9e;
  background-color: #ffffff;
  cursor: pointer;
}

.current {
  color: #000000;
  background-color: transparent;
  font-weight: bold;
  border: 0;
  cursor: default;
}
</style>