<script setup>
import { ref } from "vue"
import Job from "./Dashboard/Job.vue"

const props = defineProps({
  userScreenName: String,
  isConfigured: Boolean
})

const loading = ref(false)

const twitterApiKey = ref("")
const twitterApiSecret = ref("")
const twitterAccessToken = ref("")
const twitterAccessTokenSecret = ref("")

</script>

<template>
  <div>
    <template v-if="isConfigured">
      <h1>
        Semiphemeral Dashboard
        <img class="refresh" @click="fetchJobs()" src="/images/refresh.png" alt="Refresh" title="Refresh" />
      </h1>
    </template>
    <template v-else>
      <h1>Configure Semiphemeral</h1>
    </template>

    <template v-if="loading">
      <p>
        <img src="/images/loading.gif" alt="Loading" />
      </p>
    </template>
    <template v-else>
      <div v-if="isConfigured">
        <p>Not implemented</p>
      </div>
      <div v-else class="configure-instructions">
        <form v-on:submit.prevent="onSubmit">
          <p><strong>Semiphemeral uses the Twitter API.</strong> Since Elon Musk took over Twitter, the billionaire ended
            free access to the
            API in an attempt to squeeze every penny out its users. However, it's still marginally possible for individual
            users to get their own API keys for free, to use for their own accounts.</p>
          <p><strong>Step 1:</strong> Load the <a href="https://developer.twitter.com/en/portal">Twitter Developer
              Portal</a>. It will try to charge you absurdly unreasonable amount of money, but there should be a tiny
            "Sign
            up for Free Account" link. Click that.</p>
          <p class="center"><img src="/images/twitter-dev-account1.png" alt="" /></p>
          <p><strong>Step 2:</strong> Next, you must fill out a form describing your use case (using over 250 characters),
            and agree to some things.</p>
          <p class="center"><img src="/images/twitter-dev-account2.png" alt="" /></p>
          <p><strong>Step 3:</strong> You should now have access to the Twitter Developer Portal. A default project should
            have automatically been created for you. From the Dashboard, you should see your project's app, and it should
            include a "Keys and Tokens" button that's shaped like a skeleton key. Click that.</p>
          <p class="center"><img src="/images/twitter-dev-account3.png" alt="" /></p>
          <p>The Key and Tokens page should look like this:</p>
          <p class="center"><img src="/images/twitter-dev-account4.png" alt="" /></p>
          <p><strong>Step 4:</strong> Under Consumer Keys, next to "API Key and Secret", click the Regenerate button. It
            will ask you if you're sure. Click "Yes, regnerate". It will generate a new key for you and show you two
            values,
            an API Key and an API Key Secret. Copy and paste those values here.</p>
          <p>
            <label class="input" for="twitter-api-key">API Key</label>
            <input type="text" id="twitter-api-key" v-model="twitterApiKey" />
          </p>
          <p>
            <label class="input" for="twitter-api-key">API Key Secret</label>
            <input type="text" id="twitter-api-secret" v-model="twitterApiSecret" />
          </p>
          <p>Then click "Yes, I saved them".</p>
          <p><strong>Step 5:</strong> Under Authentication Tokens, next to "Access Token and Secret", click the Generate
            button. It will generate a new key for you and show you two
            values,
            an Access Token and an Access Token Secret. Copy and paste those values here.</p>
          <p>
            <label class="input" for="twitter-access-token">Access Token</label>
            <input type="text" id="twitter-access-token" v-model="twitterAccessToken" />
          </p>
          <p>
            <label class="input" for="twitter-access-token-secret">Access Token Secret</label>
            <input type="text" id="twitter-access-token-secret" v-model="twitterAccessTokenSecret" />
          </p>
          <p>Then click "Yes, I saved them".</p>
          <p><strong>Step 6:</strong> Once you've entered your API Key, API Key Secret, Access Token, and Access Token
            Secret above, click the following button to test your API credentials to see if they work.</p>
        </form>
      </div>
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

.configure-instructions img {
  width: 500px;
}

.configure-instructions label {
  display: inline-block;
  width: 200px;
  font-weight: bold;
  text-align: right;
  padding-right: 10px;
}

.configure-instructions input[type="text"] {
  width: 400px;
}
</style>