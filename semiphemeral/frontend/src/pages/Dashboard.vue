<script setup>
import { ref, onMounted } from "vue"
import io from 'socket.io-client'
import Job from "./Dashboard/Job.vue"

const props = defineProps({ settings: Object })

const loading = ref(false)
const activeJobs = ref([])
const pendingJobs = ref([])
const finishedJobs = ref([])

onMounted(() => {
  const socket = io('/')
  socket.on('connect', () => {
    console.log('Connected to Socket.IO server')
  })

  // Error messages
  socket.on('fail', (data) => {
    alert(data.message);
  })

  // Job progress
  socket.on('progress', (data) => {
    var job = data
    var index = activeJobs.value.findIndex((j) => j.id === job.id)
    if (index === -1) {
      // Job is not in activeJobs, so add it
      activeJobs.value.push(job)
    } else {
      // Job is in activeJobs, so update it
      activeJobs.value[index] = job
    }
  })

  // Update jobs
  socket.on('update', (data) => {
    fetchJobs()
  })
})

function downloadTwitterData() {
  loading.value = true
  fetch("/api/dashboard", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action: "download",
    }),
  })
    .then(function (response) {
      loading.value = false
      response.json().then(function (data) {
        if (data.error) {
          alert(data['error_message'])
        }
        fetchJobs();
      })
    })
    .catch(function (err) {
      console.log("Error downloading Twitter data", err)
      alert(err)
      loading.value = false
    })
}

function deleteTwitterData() {
}

function fetchJobs() {
  loading.value = true

  // Get lists of pending, active, and finished jobs
  fetch("/api/dashboard")
    .then(function (response) {
      if (response.status !== 200) {
        console.log("Error fetching jobs, status code: " + response.status)
        loading.value = false
        return
      }
      response.json().then(function (data) {
        loading.value = false
        if (data["active_jobs"]) {
          activeJobs.value = data["active_jobs"]
        } else {
          activeJobs.value = []
        }

        if (data["pending_jobs"]) {
          pendingJobs.value = data["pending_jobs"]
        } else {
          pendingJobs.value = []
        }

        if (data["finished_jobs"]) {
          finishedJobs.value = data["finished_jobs"]
        } else {
          finishedJobs.value = []
        }
      })
    })
    .catch(function (err) {
      console.log("Error fetching jobs", err)
      loading.value = false
    })
}

fetchJobs()
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
      <!-- Pending jobs -->
      <template v-if="pendingJobs.length > 0">
        <h2>Pending Jobs</h2>
        <ul class="jobs">
          <li v-for="job in pendingJobs">
            <Job v-bind:job="job" v-bind:key="job.id" />
          </li>
        </ul>
      </template>

      <!-- Active jobs -->
      <template v-if="activeJobs.length > 0">
        <h2>Active Jobs</h2>
        <ul class="jobs">
          <li v-for="job in activeJobs">
            <Job v-bind:job="job" v-bind:key="job.id" />
          </li>
        </ul>
      </template>

      <!-- If no pending or active job, so show interface to start a job -->
      <template v-if="pendingJobs.length == 0 && activeJobs.length == 0">
        <div v-if="settings.since_id == null">
          <p>To start using Semiphemeral, you first must download all of your tweets and likes. Click the button to start
            downloading. This may take a while, depending on how many tweets and likes you have.
          </p>
        </div>
        <div v-else>
          <p>This downloads all of your tweets and likes since the last time you downloaded Twitter data.</p>
          <p>
            <label>
              <input type="checkbox" v-model="downloadAllTweets" />
              Download <em>all</em> of my Twitter data instead of just the newest data
            </label>
          </p>
        </div>
        <p>
          <button class="primary" v-on:click="downloadTwitterData()" v-bind:disabled="loading">Download Twitter
            Data</button>
        </p>

        <template v-if="settings.since_id != null">
          <p>
            <button class="primary" v-on:click="deleteTwitterData()" v-bind:disabled="loading">Delete Twitter
              Data</button>
          </p>
          <p>This deletes your tweets, retweets, likes, and DMs based on your <router-link
              to="/settings">settings</router-link>.</p>
        </template>
      </template>

      <!-- Finished jobs -->
      <template v-if="finishedJobs.length > 0">
        <h2>Finished Jobs</h2>
        <ul class="jobs">
          <li v-for="job in finishedJobs">
            <Job v-bind:job="job" v-bind:key="job.id" />
          </li>
        </ul>
      </template>
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