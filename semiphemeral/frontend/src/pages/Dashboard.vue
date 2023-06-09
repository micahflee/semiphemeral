<script setup>
import { ref } from "vue"
import Job from "./Dashboard/Job.vue"

const props = defineProps({
  userScreenName: String
})

const loading = ref(false)

const twitterApiKey = ref("")
const twitterApiSecret = ref("")
const twitterAccessToken = ref("")
const twitterAccessTokenSecret = ref("")

</script>

<template>
  <div>
    <h1>
      Semiphemeral Dashboard
      <img class="refresh" @click="fetchJobs()" src="/images/refresh.png" alt="Refresh" title="Refresh" />
    </h1>

    <template v-if="loading">
      <p>
        <img src="/images/loading.gif" alt="Loading" />
      </p>
    </template>
    <template v-else>
      <p>Not implemented</p>
    </template>
  </div>
</template>

<style scoped>
ul.buttons {
  list-style: none;
  padding: 0;
  margin-left: 20px;
}

button.start,
button.download {
  background-color: #4caf50;
  border: none;
  color: white;
  padding: 5px 20px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  cursor: pointer;
  font-weight: bold;
  border-radius: 5px;
  margin: 0 0 5px 0;
}

button.pause,
button.reactivate {
  background-color: #624caf;
  border: none;
  color: white;
  padding: 5px 20px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  cursor: pointer;
  font-weight: bold;
  border-radius: 5px;
  margin: 0 0 5px 0;
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