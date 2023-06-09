<script setup>
import { ref } from "vue"

const props = defineProps({
  userScreenName: String
})

const loading = ref(false)
const errorMessage = ref("")
const hasFetched = ref(false)
const twitterApiKey = ref(false)
const twitterApiSecret = ref(false)
const twitterAccessToken = ref(false)
const twitterAccessTokenSecret = ref(false)
const deleteTweets = ref(false)
const tweetsDaysThreshold = ref(false)
const tweetsEnableRetweetThreshold = ref(false)
const tweetsRetweetThreshold = ref(false)
const tweetsEnableLikeThreshold = ref(false)
const tweetsLikeThreshold = ref(false)
const tweetsThreadsThreshold = ref(false)
const retweetsLikes = ref(false)
const retweetsLikesDeleteRetweets = ref(false)
const retweetsLikesRetweetsThreshold = ref(false)
const retweetsLikesDeleteLikes = ref(false)
const retweetsLikesLikesThreshold = ref(false)
const directMessages = ref(false)
const directMessagesThreshold = ref(false)
const downloadAllTweets = ref(false)

function getSettings() {
  fetch("/api/settings")
    .then(function (response) {
      if (response.status !== 200) {
        console.log(
          "Error fetching settings, status code: " + response.status
        );
        return
      }
      response.json().then(function (data) {
        hasFetched.value = data["has_fetched"]
        twitterApiKey.value = data["twitter_api_key"]
        twitterApiSecret.value = data["twitter_api_secret"]
        twitterAccessToken.value = data["twitter_access_token"]
        twitterAccessTokenSecret.value = data["twitter_access_token_secret"]
        deleteTweets.value = data["delete_tweets"]
        tweetsDaysThreshold.value = data["tweets_days_threshold"]
        tweetsEnableRetweetThreshold.value = data["tweets_enable_retweet_threshold"]
        tweetsRetweetThreshold.value = data["tweets_retweet_threshold"]
        tweetsEnableLikeThreshold.value = data["tweets_enable_like_threshold"]
        tweetsLikeThreshold.value = data["tweets_like_threshold"]
        tweetsThreadsThreshold.value = data["tweets_threads_threshold"]
        retweetsLikes.value = data["retweets_likes"]
        retweetsLikesDeleteRetweets.value = data["retweets_likes_delete_retweets"]
        retweetsLikesRetweetsThreshold.value = data["retweets_likes_retweets_threshold"]
        retweetsLikesDeleteLikes.value = data["retweets_likes_delete_likes"]
        retweetsLikesLikesThreshold.value = data["retweets_likes_likes_threshold"]
        directMessages.value = data["direct_messages"]
        directMessagesThreshold.value = data["direct_messages_threshold"]
      });
    })
    .catch(function (err) {
      console.log("Error fetching user", err)
    })
}

function onSubmit() {
  loading.value = true
  fetch("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      twitter_api_key: twitterApiKey.value,
      twitter_api_secret: twitterApiSecret.value,
      twitter_access_token: twitterAccessToken.value,
      twitter_access_token_secret: twitterAccessTokenSecret.value,
      delete_tweets: deleteTweets.value,
      tweets_days_threshold: Number(tweetsDaysThreshold.value),
      tweets_enable_retweet_threshold: tweetsEnableRetweetThreshold.value,
      tweets_retweet_threshold: Number(tweetsRetweetThreshold.value),
      tweets_enable_like_threshold: tweetsEnableLikeThreshold.value,
      tweets_like_threshold: Number(tweetsLikeThreshold.value),
      tweets_threads_threshold: tweetsThreadsThreshold.value,
      retweets_likes: retweetsLikes.value,
      retweets_likes_delete_retweets: retweetsLikesDeleteRetweets.value,
      retweets_likes_retweets_threshold: Number(retweetsLikesRetweetsThreshold.value),
      retweets_likes_delete_likes: retweetsLikesDeleteLikes.value,
      retweets_likes_likes_threshold: Number(retweetsLikesLikesThreshold.value),
      direct_messages: directMessages.value,
      direct_messages_threshold: Number(directMessagesThreshold.value),
      download_all_tweets: downloadAllTweets.value,
    }),
  })
    .then(function (response) {
      loading.value = false
      response.json().then(function (data) {
        if (data.error) {
          errorMessage.value = data['error_message']
        } else {
          errorMessage.value = ""
        }
      })
    })
    .catch(function (err) {
      console.log("Error saving settings", err)
      errorMessage.value = err
      loading.value = false
    })
}

getSettings()
</script>

<template>
  <div>
    <h1>Choose what you'd like Semiphemeral to automatically delete</h1>
    <p class="error-message" v-if="errorMessage.value != ''">{{ errorMessage }}</p>

    <template v-if="loading">
      <p>
        <img src="/images/loading.gif" alt="Loading" />
      </p>
    </template>
    <template v-else>
      <form v-on:submit.prevent="onSubmit">
        <fieldset class="api-creds">
          <legend>Twitter API Credentials</legend>
          <p>
            <label>API Key</label>
            <input type="text" v-model="twitterApiKey" />
          </p>
          <p>
            <label>API Key Secret</label>
            <input type="text" v-model="twitterApiSecret" />
          </p>
          <p>
            <label>Access Token</label>
            <input type="text" v-model="twitterAccessToken" />
          </p>
          <p>
            <label>Access Token Secret</label>
            <input type="text" v-model="twitterAccessTokenSecret" />
          </p>
        </fieldset>
        <p>
          <label class="checkbox">
            <input type="checkbox" v-model="deleteTweets" />
            Delete old tweets
          </label>
        </p>
        <fieldset :class="deleteTweets ? '' : 'disabled'">
          <legend>Tweets</legend>
          <p>
            Delete tweets older than
            <input type="number" class="small" min="0" v-model="tweetsDaysThreshold" :disabled="!deleteTweets" />
            days
          </p>
          <p>
            <label>
              <input type="checkbox" v-model="tweetsEnableRetweetThreshold" :disabled="!deleteTweets" />
              Unless they have at least
            </label>
            <input type="number" class="small" min="0" v-model="tweetsRetweetThreshold"
              :disabled="!deleteTweets || !tweetsEnableRetweetThreshold" />
            retweets
          </p>
          <p>
            <label>
              <input type="checkbox" v-model="tweetsEnableLikeThreshold" :disabled="!deleteTweets" />
              Or at least
            </label>
            <input type="number" class="small" min="0" v-model="tweetsLikeThreshold"
              :disabled="!deleteTweets || !tweetsEnableLikeThreshold" />
            likes
          </p>
          <p>
            <label>
              <input type="checkbox" v-model="tweetsThreadsThreshold" :disabled="!deleteTweets" />
              Don't delete tweets that are part of a thread that contains at least one tweet that meets these thresholds
            </label>
          </p>
        </fieldset>

        <p>
          <label>
            <input type="checkbox" v-model="retweetsLikes" />
            Unretweet and unlike old tweets
          </label>
        </p>

        <fieldset :class="retweetsLikes ? '' : 'disabled'">
          <legend>Retweets and likes</legend>

          <p>
            <label>
              <input type="checkbox" v-model="retweetsLikesDeleteRetweets" :disabled="!retweetsLikes" />
              Unretweet tweets
            </label>
            older than
            <input type="number" class="small" min="0" v-model="retweetsLikesRetweetsThreshold"
              :disabled="!retweetsLikes" />
            days
          </p>

          <p>
            <label>
              <input type="checkbox" v-model="retweetsLikesDeleteLikes" :disabled="!retweetsLikes" />
              Unlike tweets
            </label>
            older than
            <input type="number" class="small" min="0" v-model="retweetsLikesLikesThreshold" :disabled="!retweetsLikes" />
            days
          </p>
        </fieldset>

        <p>
          <label>
            <input type="checkbox" v-model="directMessages" />
            Delete old direct messages
          </label>
        </p>

        <fieldset :class="directMessages ? '' : 'disabled'">
          <legend>Direct messages</legend>

          <p>
            Delete direct messages older than
            <input type="number" class="small" min="0" max="29" v-model="directMessagesThreshold"
              :disabled="!directMessages" />
            days
          </p>

          <p class="dm-note">
            Twitter only allows Semiphemeral access to the last 30 days of DMs, so you have to delete older DMs
            manually.
            <router-link to="/dms">Learn more</router-link>&nbsp;about how this works.
          </p>
        </fieldset>

        <p v-if="hasFetched">
          <label>
            <input type="checkbox" v-model="downloadAllTweets" />
            Force Semiphemeral to download all of my tweets again next time, instead of just the newest ones
          </label>
        </p>

        <p>
          <input :disabled="loading" type="submit" value="Save" />
        </p>
      </form>
    </template>
  </div>
</template>

<style scoped>
input.small {
  width: 3em;
}

.disabled {
  opacity: 50%;
}

.dm-note {
  font-size: 0.8em;
  color: #666666;
}

.api-creds label {
  display: inline-block;
  width: 150px;
}

.api-creds input {
  width: 500px;
}
</style>