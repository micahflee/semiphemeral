<script setup>
import { ref } from "vue"
import NavBar from "./layout/NavBar.vue"

const userScreenName = ref("")
const userProfileUrl = ref("")
const isConfigured = ref(false)

fetch("/api/user")
  .then(function (response) {
    if (response.status !== 200) {
      console.log("Error fetching user, status code: " + response.status);
      return;
    }
    response.json().then(function (data) {
      userScreenName.value = data["user_screen_name"]
      userProfileUrl.value = data["user_profile_url"]
    });
  })
  .catch(function (err) {
    console.log("Error fetching user", err)
  });
</script>

<template>
  <div>
    <NavBar v-bind="{
      userScreenName: userScreenName,
      userProfileUrl: userProfileUrl,
      isConfigured: isConfigured
    }"></NavBar>
    <router-view v-bind="{
      userScreenName: userScreenName,
      isConfigured: isConfigured
    }"></router-view>
  </div>
</template>

<style>
html {
  position: relative;
  min-height: 100%;
}

body {
  margin: 0 0 25px;
  padding: 10px;
  font-family: sans-serif;
}

p {
  line-height: 150%;
}

li {
  line-height: 150%;
}

#app {
  max-width: 1000px;
  margin: 0 auto;
  font-size: 0.9em;
}

h1 {
  font-size: 1.3em;
}

h2 {
  font-size: 1.1em;
}

img.refresh {
  margin-left: 1em;
  height: 15px;
  cursor: pointer;
}

a:link,
a:visited {
  color: #28404f;
  text-decoration: underline;
}

a:active,
a:hover {
  color: #5d8fad;
  text-decoration: none;
}

footer {
  position: absolute;
  left: 0;
  bottom: 0;
  height: 25px;
  width: 100%;
  overflow: hidden;
  text-align: right;
  font-size: 0.7em;
}

footer p {
  margin: 0 10px;
}
</style>