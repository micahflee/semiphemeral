<script setup>
import { ref } from "vue"
import Job from "./Dashboard/Job.vue"

const props = defineProps({
  userScreenName: String
})

const loading = ref(false)

function downloadTwitterData() {
}

function deleteTwitterData() {
}
</script>

<template>
  <div>
    <h1>Semiphemeral Dashboard</h1>

    <template v-if="loading">
      <p>
        <img src="/images/loading.gif" alt="Loading" />
      </p>
    </template>
    <template v-else>
      <p>
        <button class="primary" v-on:click="downloadTwitterData()" v-bind:disabled="loading">Download Twitter
          Data</button>
      </p>
      <p>This downloads all of your tweets and likes since the last time you downloaded Twitter data.</p>
      <p>
        <button class="primary" v-on:click="deleteTwitterData()" v-bind:disabled="loading">Delete Twitter Data</button>
      </p>
      <p>This deletes your tweets, retweets, likes, and DMs based on your <router-link
          to="/settings">settings</router-link>.</p>
    </template>
  </div>
</template>

<style scoped>
ul.buttons {
  list-style: none;
  padding: 0;
  margin-left: 20px;
}

ul.jobs {
  list-style: none;
  padding: 0;
}

.warning {
  color: #624caf;
  font-weight: bold;
  font-style: italic;
}

.center {
  text-align: center;
}
</style>