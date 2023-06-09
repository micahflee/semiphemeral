<script setup>
import { ref } from "vue"

const props = defineProps({
  userScreenName: String
})

const file = ref(null)
const loading = ref(false)
const directMessages = ref(false)
const isDMAppAuthenticated = ref(false)
const isDMJobOngoing = ref(false)

function getDMInfo() {
  loading.value = true;
  fetch("/api/dms")
    .then(function (response) {
      loading.value = false
      if (response.status !== 200) {
        console.log(
          "Error fetching DM info, status code: " + response.status
        )
        return
      }
      response.json().then(function (data) {
        isDMAppAuthenticated.value = data["is_dm_app_authenticated"]
        isDMJobOngoing.value = data["is_dm_job_ongoing"]
        directMessages.value = data["direct_messages"]
      });
    })
    .catch(function (err) {
      console.log("Error fetching DM info", err)
    });
}

function onSubmit() {
  if (
    file.value.files[0].name != "direct-messages.js" &&
    file.value.files[0].name != "direct-messages-group.js"
  ) {
    alert(
      'That\'s the wrong file. It should be named "direct-messages.js" or "direct-messages-group.js".'
    );
    return
  }

  var formData = new FormData()
  formData.append("file", file.value.files[0])

  loading.value = true
  fetch("/api/dms", { method: "POST", body: formData })
    .then(function (response) {
      loading.value = false

      if (response.status !== 200) {
        console.log(
          "Error uploading file, status code: " + response.status
        );
        return
      }

      response.json().then(function (data) {
        if (data["error"]) {
          alert(data["error_message"])
        } else {
          getDMInfo()
        }
      })
    })
    .catch(function (err) {
      console.log("Error uploading DMs file", err)
      loading.value = false
    })
}

getDMInfo()
</script>

<template>
  <div>
    <h1>Direct messages</h1>
    <template v-if="loading">
      <p>
        <img src="/images/loading.gif" alt="Loading" />
      </p>
    </template>
    <template v-else>
      <template v-if="isDMAppAuthenticated">
        <h2>Automatically deleting your recent DMs</h2>
        <p>
          Twitter only tells Semiphemeral about the last 30 days of your DMs. Because of this, Semiphemeral can't
          <em>automatically</em> delete all your old DMs, only those within the last 30 days. For example, if you
          configure it to delete DMs older than 7 days, each time it runs it will delete the DMs between 30 days ago and
          7 days ago.
        </p>

        <h2>Deleting all your old DMs</h2>
        <p>
          But don't worry: Semiphemeral can still delete your DMs older than 30 days. You just need to give it a list of
          all of those DMs. In order to get this list you must
          <a href="https://twitter.com/settings/your_twitter_data" target="_blank">download your Twitter archive from
            here</a>. When you request an archive from Twitter it may take them a day or two before it's ready. When
          it's ready, you will download a zip file containing your archive.
        </p>
        <p>Unzip your Twitter archive. There should be a folder called "data", and inside there should be many files
          including:</p>
        <ul>
          <li>"direct-messages.js", containing all of your DMs</li>
          <li>"direct-messages-group.js", containing all of your group DMs</li>
          <li>"direct-message-headers.js", containing metadata of all of your DMs</li>
          <li>"direct-message-group-headers.js", containing metadata of all of your group DMs</li>
        </ul>
        <p>
          <strong>To delete your old DMs, upload your "direct-messages.js" or "direct-messages-group.js"
            file here.</strong> Semiphemeral will delete all of your old DMs listed in these files except for the most
          recent ones as you've specified in your settings. (Semiphemeral ignores the content of DMs and only looks at
          their IDs. The file you uploaded is deleted as soon as the delete job is finished.)
        </p>
        <template v-if="!directMessages">
          <p>
            <em>You must enable deleting old direct messages in settings before you can bulk delete your old DMs.</em>
          </p>
        </template>
        <template v-else>
          <template v-if="isDMJobOngoing">
            <p>
              <em>Your old direct messages will soon be deleted. Check the dashboard for progress updates.</em>
            </p>
          </template>
          <template v-else>
            <form v-on:submit.prevent="onSubmit">
              <p>
                <input ref="file" type="file" accept="text/javascript, application/x-javascript" />
                <input :disabled="loading" class="button" type="submit" value="Delete these old DMs" />
              </p>
            </form>
          </template>
        </template>
      </template>
      <template v-else>
        <p>
          If you want to automatically delete your old direct messages you must give Semiphemeral access to your DMs.
          You can do this on the
          <router-link to="/settings">settings page</router-link>.
        </p>
      </template>
    </template>
  </div>
</template>

<style scoped>
.button {
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
</style>