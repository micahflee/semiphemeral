<script setup>
import { ref } from "vue"
import NavBar from "./layout/NavBar.vue"
import ConfigureWizard from "./pages/ConfigureWizard.vue"

const isConfigured = ref(false)
const settings = ref(null)

fetch("/api/settings")
  .then(function (response) {
    if (response.status !== 200) {
      console.log("Error fetching user, status code: " + response.status);
      return;
    }
    response.json().then(function (data) {
      isConfigured.value = data["is_configured"]
      settings.value = data["settings"]
    });
  })
  .catch(function (err) {
    console.log("Error fetching settings", err)
  });
</script>

<template>
  <div v-if="isConfigured">
    <NavBar v-bind="{ settings: settings }"></NavBar>
    <router-view v-bind="{ settings: settings }"></router-view>
  </div>
  <div v-else>
    <ConfigureWizard></ConfigureWizard>
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

img {
  max-width: 100%;
}

.error-message {
  color: red;
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

button.primary {
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

button.secondary {
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
</style>