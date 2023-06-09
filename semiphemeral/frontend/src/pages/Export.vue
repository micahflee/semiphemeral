<script setup>
const props = defineProps({
  userScreenName: String
})
</script>

<template>
  <div>
    <h1>Export your tweets</h1>

    <p>Semiphemeral lets you export a spreadsheet (CSV file) of your tweets and retweets. Make sure that Semiphemeral
      has downloaded your latest tweets before exporting.</p>

    <p>
      <a class="button" href="/export/download">Download spreadsheet of tweets</a>
    </p>
  </div>
</template>

<style scoped>
a.button {
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