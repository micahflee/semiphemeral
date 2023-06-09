<script setup>
import { ref, watch, onMounted, onUpdated } from "vue"

const props = defineProps({
  tweet: Object,
  userScreenName: String
})

const emit = defineEmits(["exclude-true", "exclude-false"])

const loading = ref(false)
const exclude = ref(false)
const excludeCheckbox = ref(null)
const error = ref("")

function formatDate() {
  var date = new Date(props.tweet.created_at * 1000)
  return "" + date.getFullYear() +
    "/" + (date.getMonth() + 1) +
    "/" + date.getDate()
}

watch(exclude, (newExclude, oldExclude) => {
  // Skip if this is the first time
  if (newExclude == null || oldExclude == null) {
    return
  }
  if (newExclude) {
    emit("exclude-true")
  } else {
    emit("exclude-false")
  }

  loading.value = true
  error.value = ""
  excludeCheckbox.disabled = true

  fetch("/api/tweets", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      status_id: props['tweet'].status_id,
      exclude: exclude.value,
    })
  })
    .then(function (response) {
      loading.value = false
      excludeCheckbox.disabled = false
    })
    .catch(function (err) {
      console.log("Error toggling exclude", err)
      loading.value = false
      excludeCheckbox.disabled = false

      // Toggle back
      var oldExclude = exclude.value
      exclude.value = null
      exclude.value = !oldExclude
      error.value = "Error toggling exclude"
    });
})

onMounted(() => {
  exclude.value = props.tweet.exclude
})

onUpdated(() => {
  exclude.value = props.tweet.exclude
})
</script>

<template>
  <div class="tweet-wrapper">
    <div class="info">
      <label>
        <input ref="excludeCheckbox" type="checkbox" v-model="exclude" />
        <span v-if="exclude" class="excluded">Excluded from deletion</span>
        <span v-else>Exclude from deletion</span>
        <span v-if="loading">
          <img src="/images/loading.gif" title="Loading" />
        </span>
        <span v-if="error != ''" class="error">{{ error }}</span>
      </label>
      <div class="stats">
        {{ tweet.retweet_count }} retweets,
        {{ tweet.like_count }} likes,
        <a target="_blank" :href="`https://twitter.com/${userScreenName}/status/${tweet.status_id}`">see on
          Twitter</a>
      </div>
    </div>
    <div class="tweet-text">{{ tweet.text }}</div>
    <div class="created-at">{{ formatDate() }}</div>
  </div>
</template>

<style scoped>
.tweet-wrapper {
  display: inline-block;
  width: 300px;
  max-width: 100%;
  border: 1px solid #f0f0f0;
  border-radius: 5px;
  padding: 5px 5px 0 5px;
  margin: 0 10px 10px 0;
  overflow: hidden;
}

.created-at {
  font-size: 0.9em;
  color: #666666;
  text-align: right;
}

.excluded {
  font-weight: bold;
}

.stats {
  font-size: 0.8em;
  color: #666666;
}

.error {
  color: #cc0000;
}
</style>